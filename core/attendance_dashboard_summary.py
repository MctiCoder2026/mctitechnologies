from django.db.models import Max, Min, Q
from django.utils import timezone

from .models import Student


def attendance_action_summary(user):
    from .views import _attendance_access
    from django.test import RequestFactory

    request = RequestFactory().get("/attendance/follow-up/")
    request.user = user

    is_admin, forced_branch, _ = _attendance_access(request)

    if not is_admin and (not user.is_staff or not forced_branch):
        return {"allowed": False}

    today = timezone.localdate()

    qs = (
        Student.objects.filter(
            status="active",
            enrollments__status="active",
            enrollments__enrollment_date__lte=today,
        )
        .exclude(Q(branch__isnull=True) | Q(branch=""))
        .annotate(
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
        .distinct()
    )

    if not is_admin:
        qs = qs.filter(branch__iexact=forced_branch)

    counts = {3: 0, 5: 0, 7: 0}

    for last_present, first_enrollment in qs.values_list(
        "last_present", "first_enrollment"
    ):
        reference = last_present or first_enrollment or today
        inactive_days = max((today - reference).days, 0)

        for threshold in counts:
            if inactive_days >= threshold:
                counts[threshold] += 1

    return {
        "allowed": True,
        "branch": "All Branches" if is_admin else forced_branch.title(),
        "days3": counts[3],
        "days5": counts[5],
        "days7": counts[7],
    }
