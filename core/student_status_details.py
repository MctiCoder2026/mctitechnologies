import csv
from datetime import date
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Max, Min
from django.db.models.functions import Lower, Trim
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from .models import Enrollment, Attendance

@login_required
def student_status_details(request):
    from .views import is_admin_user
    if not is_admin_user(request.user):
        raise PermissionDenied("Head Office / Power User only")

    branch = request.GET.get("branch", "").strip().lower()
    status = request.GET.get("status", "active").strip().lower()
    allowed_branches = {
        "kharghar", "panvel", "koperkhairane",
        "kamothe", "ghansoli", "nerul"
    }
    allowed_statuses = {
        "active", "cancelled", "completed", "hold", "inactive15"
    }

    if branch not in allowed_branches or status not in allowed_statuses:
        raise PermissionDenied("Invalid report filter")

    today = timezone.localdate()
    try:
        selected_date = date.fromisoformat(request.GET.get("date", ""))
    except ValueError:
        selected_date = today
    if selected_date > today:
        selected_date = today
    enrollments = (
        Enrollment.objects
        .annotate(normalized_branch=Lower(Trim("branch")))
        .filter(
            normalized_branch=branch,
            enrollment_date__lte=selected_date,
            status="active" if status == "inactive15" else status
        )
        .select_related("student", "course", "cancelled_by")
        .order_by("student__name", "id")
    )

    student_ids = list(enrollments.values_list("student_id", flat=True))
    last_present = {
        row["student_id"]: row["last"]
        for row in Attendance.objects.filter(
            student_id__in=student_ids,
            status="present",
            attendance_date__lte=selected_date
        ).values("student_id").annotate(last=Max("attendance_date"))
    }

    latest_attendance = {}
    for attendance in (
        Attendance.objects
        .filter(student_id__in=student_ids, attendance_date__lte=selected_date)
        .select_related("marked_by")
        .order_by("-attendance_date", "-id")
    ):
        latest_attendance.setdefault(attendance.student_id, attendance)

    first_dates = {
        item["student_id"]: item["first"]
        for item in enrollments.values("student_id").annotate(
            first=Min("enrollment_date")
        )
    }
    seen_students = set()
    records = []
    for enrollment in enrollments:
        last = last_present.get(enrollment.student_id)
        reference = last or first_dates.get(enrollment.student_id) or selected_date
        inactive_days = max((selected_date - reference).days, 0)

        if status == "inactive15":
            if inactive_days < 15 or enrollment.student_id in seen_students:
                continue
            seen_students.add(enrollment.student_id)

        records.append({
            "enrollment": enrollment,
            "last_present": last,
            "latest_attendance": latest_attendance.get(enrollment.student_id),
            "inactive_days": inactive_days,
        })

    if request.GET.get("export") == "csv":
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="mcti_{branch}_{status}_students.csv"'
        )
        response.write(chr(65279))
        writer = csv.writer(response)
        writer.writerow([
            "Student", "Mobile", "Course", "Branch",
            "Enrollment Date", "Status", "Branch Remarks",
            "Cancellation Reason", "Cancelled By", "Cancelled At",
            "Last Present", "Latest Attendance Status",
            "Latest Attendance Remark", "Attendance Date",
            "Marked By", "Inactive Days"
        ])

        def safe(value):
            value = str(value or "")
            if value.lstrip().startswith(("=", "+", "-", "@")):
                return "'" + value
            return value

        for row in records:
            e = row["enrollment"]
            a = row["latest_attendance"]
            writer.writerow([safe(value) for value in [
                e.student.name, e.student.mobile,
                e.course.title if e.course else "",
                e.branch, e.enrollment_date, e.status,
                e.notes, e.cancellation_reason,
                e.cancelled_by.get_full_name() or e.cancelled_by.username
                if e.cancelled_by else "",
                e.cancelled_at, row["last_present"],
                a.status if a else "",
                a.remarks if a else "",
                a.attendance_date if a else "",
                a.marked_by.get_full_name() or a.marked_by.username
                if a and a.marked_by else "",
                row["inactive_days"]
            ]])
        return response

    return render(request, "core/student_status_details.html", {
        "records": records,
        "branch": branch.title(),
        "status": status,
        "selected_date": selected_date,
    })
