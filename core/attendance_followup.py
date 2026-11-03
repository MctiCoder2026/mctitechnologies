from django.contrib.auth.decorators import login_required
from django.db.models import Max, Min, Q
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import Student


@login_required
def attendance_followup(request):
    from .views import _attendance_access

    is_admin, forced_branch, branches = _attendance_access(request)

    if not is_admin and (not request.user.is_staff or forced_branch is None):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Staff access required.")

    today = timezone.localdate()
    branch = (
        request.GET.get("branch", "").strip().lower()
        if is_admin else forced_branch
    )

    allowed = {value for value, _ in branches if value}

    if branch and branch not in allowed:
        branch = ""

    try:
        days = int(request.GET.get("days", "3"))
    except ValueError:
        days = 3

    if days not in (0, 2, 3, 5, 7):
        days = 3

    search = request.GET.get("search", "").strip()[:100]

    students = (
        Student.objects.filter(
            status="active",
            enrollments__status="active",
            enrollments__enrollment_date__lte=today,
        )
        .exclude(Q(branch__isnull=True) | Q(branch=""))
        .distinct()
    )

    if branch:
        students = students.filter(branch__iexact=branch)

    students = students.annotate(
        last_present=Max(
            "attendance_records__attendance_date",
            filter=Q(
                attendance_records__status="present",
                attendance_records__attendance_date__lte=today,
            ),
        ),
        first_enrollment=Min(
            "enrollments__enrollment_date",
            filter=Q(
                enrollments__status="active",
                enrollments__enrollment_date__lte=today,
            ),
        ),
    )

    if search:
        students = students.filter(
            Q(name__icontains=search)
            | Q(mobile__icontains=search)
            | Q(student_id__icontains=search)
        )

    rows = []

    for student in students.order_by("name", "id"):
        reference = student.last_present or student.first_enrollment or today
        inactive_days = max((today - reference).days, 0)
        present_today = student.last_present == today

        if days == 0:
            if present_today:
                continue
        elif inactive_days < days:
            continue

        rows.append({
            "student": student,
            "last_present": student.last_present,
            "inactive_days": inactive_days,
            "present_today": present_today,
        })

    return render(request, "core/attendance_followup.html", {
        "rows": rows,
        "today": today,
        "days": days,
        "branch_filter": branch,
        "branches": branches,
        "is_admin": is_admin,
        "search": search,
        "total": len(rows),
    })
