from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Max, Min, Q, Sum
from django.db.models.functions import Lower, Trim
from django.shortcuts import render
from django.utils import timezone
from .models import Attendance, Enrollment, Student, FeePayment

BRANCHES = [("kharghar", "Kharghar"), ("panvel", "Panvel"), ("koperkhairane", "Koperkhairane"), ("kamothe", "Kamothe"), ("ghansoli", "Ghansoli"), ("nerul", "Nerul")]

@login_required
def student_monitoring(request):
    from .views import is_admin_user
    if not is_admin_user(request.user):
        raise PermissionDenied("Head Office / Power User only")
    today = timezone.localdate()
    from datetime import date
    try:
        selected_date = date.fromisoformat(request.GET.get("date", ""))
    except ValueError:
        selected_date = today
    if selected_date > today:
        selected_date = today
    branch = request.GET.get("branch", "").strip().lower()
    if branch not in dict(BRANCHES):
        branch = ""
    rows = []
    for key, label in BRANCHES:
        if branch and key != branch:
            continue
        enrollments = Enrollment.objects.annotate(normalized_branch=Lower(Trim("branch"))).filter(normalized_branch=key, enrollment_date__lte=selected_date)
        active_enrollments = enrollments.filter(status="active")
        active_ids = active_enrollments.values_list("student_id", flat=True).distinct()
        attendance = Attendance.objects.annotate(normalized_branch=Lower(Trim("branch"))).filter(normalized_branch=key, attendance_date=selected_date)
        active_attendance = attendance.filter(student_id__in=active_ids)
        active_students = Student.objects.filter(id__in=active_ids)
        last_present = Attendance.objects.filter(student_id__in=active_ids, status="present", attendance_date__lte=selected_date).values("student_id").annotate(last=Max("attendance_date"))
        last_map = {item["student_id"]: item["last"] for item in last_present}
        first_dates = {item["student_id"]: item["first"] for item in active_enrollments.values("student_id").annotate(first=Min("enrollment_date"))}
        inactive7 = inactive15 = inactive30 = never = 0
        for student_id in active_students.values_list("id", flat=True):
            last = last_map.get(student_id)
            reference = last or first_dates.get(student_id) or selected_date
            days = max((selected_date-reference).days, 0)
            inactive7 += days >= 7
            inactive15 += days >= 15
            inactive30 += days >= 30
            never += last is None
        rows.append({"key": key, "name": label, "active_students": active_students.count(), "active_enrollments": active_enrollments.count(), "present": active_attendance.filter(status="present").values("student_id").distinct().count(), "absent": active_attendance.filter(status="absent").values("student_id").distinct().count(), "leave": active_attendance.filter(status="leave").values("student_id").distinct().count(), "inactive7": inactive7, "inactive15": inactive15, "inactive30": inactive30, "never": never, "cancelled": enrollments.filter(status="cancelled").count(), "completed": enrollments.filter(status="completed").count()})
    totals = {key: sum(row[key] for row in rows) for key in ("active_students", "active_enrollments", "present", "absent", "leave", "inactive7", "inactive15", "inactive30", "never", "cancelled", "completed")}
    cancelled_qs = (
        Enrollment.objects
        .annotate(normalized_branch=Lower(Trim("branch")))
        .filter(
            normalized_branch__in=(
                [branch] if branch else [key for key, _ in BRANCHES]
            ),
            status="cancelled",
            enrollment_date__lte=selected_date,
        )
    )

    cancelled_ids = cancelled_qs.values_list("id", flat=True)

    cancelled_fee = (
        cancelled_qs.aggregate(total=Sum("final_fee"))["total"] or 0
    )

    collected = (
        FeePayment.objects
        .filter(
            enrollment_id__in=cancelled_ids,
            payment_date__lte=selected_date,
        )
        .aggregate(total=Sum("amount"))["total"] or 0
    )

    financial = {
        "cancelled_fee": cancelled_fee,
        "collected": collected,
        "uncollected": max(cancelled_fee - collected, 0),
    }

    return render(request, "core/student_monitoring.html", {"rows": rows, "totals": totals, "branches": BRANCHES, "branch_filter": branch, "selected_date": selected_date, "financial": financial})
