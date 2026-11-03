"""Read-only context adapter for MCTI Executive Command Center V3."""
from .management_analytics_v3 import executive_summary

def command_center_context(start_date=None, end_date=None):
    analytics = executive_summary(start_date, end_date)
    branches = analytics["branches"]


    # MCTI_V3_MANAGEMENT_ALERTS_V1
    lowest_conversion_branch = min(
        branches,
        key=lambda b: b["crm_conversion"]["verified_conversion_rate"],
        default=None,
    )

    return {
        "v3_lowest_conversion_branch": lowest_conversion_branch,
        "v3": analytics,
        "v3_branches": branches,
        "v3_top_cancellation_loss_branch": max(
            branches,
            key=lambda row: row["potential_loss"],
            default=None,
        ),
        "v3_top_collection_branch": max(
            branches,
            key=lambda row: row["collection"],
            default=None
        ),
        "v3_top_outstanding_branch": max(
            branches,
            key=lambda row: row["outstanding"],
            default=None
        ),
    }


from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render



@login_required(login_url="staff_login")
def command_center_preview(request):
    """Super Admin-only V3 preview. Does not replace live dashboard."""

    if not request.user.is_active or not request.user.is_superuser:
        raise PermissionDenied

    # Build the preview context without rendering the legacy dashboard.
    from .models import Admission, Enquiry, Student, FeePayment
    from django.db.models import Sum

    context = {
        "total_enquiries": Enquiry.objects.count(),
        "new_enquiries": Enquiry.objects.filter(status="new").count(),
        "converted_enquiries": Enquiry.objects.filter(status="converted").count(),
        "total_admissions": Admission.objects.count(),
        "total_students": Student.objects.filter(status="active").count(),
        "total_collected": (
            FeePayment.objects.aggregate(total=Sum("amount"))["total"] or 0
        ),
    }

    context.update(command_center_context())

    return render(
        request,
        "core/management_command_center_v3.html",
        context,
    )
