from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Enrollment
from .views import get_user_branch, is_admin_user, staff_or_admin


@user_passes_test(staff_or_admin, login_url="staff_login")
def update_enrollment_status(request, enrollment_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    action = request.POST.get("action", "").strip()
    reason = request.POST.get("reason", "").strip()

    if action not in ("cancel", "reactivate", "complete", "reopen_completed"):
        return HttpResponseForbidden("Invalid action")

    if action in ("reactivate", "reopen_completed") and not is_admin_user(request.user):
        return HttpResponseForbidden("HO access required")

    with transaction.atomic():
        enrollment = get_object_or_404(
            Enrollment.objects.select_for_update().select_related(
                "student"
            ),
            pk=enrollment_id,
        )

        if not is_admin_user(request.user):
            staff_branch = (get_user_branch(request.user) or "").strip().lower()
            enrollment_branch = (
                enrollment.branch or enrollment.student.branch or ""
            ).strip().lower()

            if not staff_branch or staff_branch != enrollment_branch:
                return HttpResponseForbidden("Branch access denied")

        admission = enrollment.student.admission
        redirect_url = (
            redirect("admission_detail", admission_id=admission.id)
            if admission
            else redirect("student_list")
        )

        if action == "complete":
            if enrollment.status != "active":
                messages.error(request, "Only active courses can be completed.")
                return redirect_url

            if len(reason) < 10:
                messages.error(request, "Enter a completion note of at least 10 characters.")
                return redirect_url

            enrollment.status = "completed"
            existing_notes = enrollment.notes or ""
            completion_note = (
                f"Course completed on {timezone.localdate().isoformat()} "
                f"by {request.user.username}: {reason}"
            )
            enrollment.notes = (
                existing_notes + "\n" + completion_note
            ).strip()
            enrollment.save(update_fields=["status", "notes"])
            messages.success(request, "Course marked as Completed.")

        elif action == "reopen_completed":
            if enrollment.status != "completed":
                messages.error(request, "Only completed courses can be reopened.")
                return redirect_url

            enrollment.status = "active"
            enrollment.save(update_fields=["status"])
            messages.success(request, "Completed course reactivated.")

        elif action == "cancel":
            if enrollment.status != "active":
                messages.error(request, "Only active enrollments can be cancelled.")
                return redirect_url

            if not reason:
                messages.error(request, "Cancellation reason is mandatory.")
                return redirect_url

            enrollment.status = "cancelled"
            enrollment.cancellation_reason = reason
            enrollment.cancelled_at = timezone.now()
            enrollment.cancelled_by = request.user
            enrollment.save(update_fields=[
                "status", "cancellation_reason",
                "cancelled_at", "cancelled_by",
            ])
            messages.success(request, "Enrollment marked as Left / Cancelled.")

        elif action == "reactivate":
            if enrollment.status != "cancelled":
                messages.error(request, "Enrollment is not cancelled.")
                return redirect_url

            enrollment.status = "active"
            enrollment.save(update_fields=["status"])
            messages.success(request, "Enrollment reactivated successfully.")

    return redirect_url


@user_passes_test(is_admin_user, login_url="staff_login")
def cancelled_fee_report(request):
    branch = request.GET.get("branch", "").strip().lower()
    search = request.GET.get("search", "").strip()

    enrollments = (
        Enrollment.objects.filter(status="cancelled")
        .select_related("student", "course", "cancelled_by")
        .prefetch_related("fee_payments")
        .order_by("-cancelled_at", "-id")
    )

    if branch:
        enrollments = enrollments.filter(branch__iexact=branch)

    if search:
        enrollments = enrollments.filter(
            Q(student__name__icontains=search)
            | Q(enrollment_number__icontains=search)
            | Q(course__title__icontains=search)
        )

    rows = list(enrollments)
    total_pending = sum((row.balance_fee for row in rows), 0)
    total_paid = sum((row.total_paid for row in rows), 0)

    return render(request, "core/cancelled_fee_report.html", {
        "rows": rows,
        "total_pending": total_pending,
        "total_paid": total_paid,
        "selected_branch": branch,
        "search": search,
        "branches": [
            ("kharghar", "Kharghar"),
            ("panvel", "Panvel"),
            ("koperkhairane", "Koperkhairane"),
            ("kamothe", "Kamothe"),
            ("ghansoli", "Ghansoli"),
            ("nerul", "Nerul"),
        ],
    })
