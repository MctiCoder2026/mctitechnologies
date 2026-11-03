from datetime import timedelta
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from django.db.models import Sum
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Enrollment, EarlyFeeDiscountRequest
from .views import is_admin_user, get_user_branch, staff_or_admin


def _allowed(user, enrollment):
    if is_admin_user(user):
        return True
    branch = get_user_branch(user)
    return bool(
        staff_or_admin(user)
        and branch
        and branch.lower() == (enrollment.branch or enrollment.student.branch or "").strip().lower()
    )


def _due_date(enrollment):
    latest = enrollment.fee_payments.order_by("-payment_date").values_list(
        "payment_date", flat=True
    ).first()
    return (latest or enrollment.enrollment_date) + timedelta(days=30)


@login_required
def request_discount(request, enrollment_id):
    enrollment = get_object_or_404(
        Enrollment.objects.select_related("student", "course"),
        pk=enrollment_id,
    )
    if not _allowed(request.user, enrollment):
        return HttpResponseForbidden("Access denied")

    if request.method == "POST":
        try:
            amount = Decimal(request.POST.get("amount", "").strip())
            payment_date = timezone.datetime.strptime(
                request.POST.get("proposed_payment_date", ""), "%Y-%m-%d"
            ).date()
        except (InvalidOperation, ValueError):
            messages.error(request, "Enter a valid amount and payment date.")
            return redirect("early_discount_request", enrollment_id=enrollment.id)

        reason = request.POST.get("reason", "").strip()
        due = _due_date(enrollment)
        today = timezone.localdate()

        if (
            enrollment.status != "active"
            or enrollment.balance_fee <= 0
            or not amount.is_finite()
            or amount <= 0
            or amount.as_tuple().exponent < -2
            or amount > enrollment.balance_fee
            or not reason
            or payment_date < today
            or payment_date >= due
            or today >= due
        ):
            messages.error(request, "Discount request is not eligible.")
            return redirect("early_discount_request", enrollment_id=enrollment.id)

        try:
            EarlyFeeDiscountRequest.objects.create(
                enrollment=enrollment,
                requested_by=request.user,
                amount=amount,
                reason=reason,
                proposed_payment_date=payment_date,
                due_date_at_request=due,
            )
        except IntegrityError:
            messages.error(request, "A pending request already exists.")
        else:
            messages.success(request, "Discount request submitted for HO approval.")
        return redirect("early_discount_request", enrollment_id=enrollment.id)

    return render(request, "core/early_discount_request.html", {
        "enrollment": enrollment,
        "due_date": _due_date(enrollment),
        "requests": enrollment.early_discount_requests.select_related(
            "requested_by", "reviewed_by"
        ).all(),
    })


@login_required
def discount_approvals(request):
    if not is_admin_user(request.user):
        return HttpResponseForbidden("HO access only")

    requests = EarlyFeeDiscountRequest.objects.select_related(
        "enrollment", "enrollment__student",
        "enrollment__course", "requested_by", "reviewed_by"
    ).order_by("-requested_at")

    return render(request, "core/early_discount_approvals.html", {
        "requests": requests[:300],
    })


@login_required
@require_POST
def review_discount(request, request_id):
    if not is_admin_user(request.user):
        return HttpResponseForbidden("HO access only")

    action = request.POST.get("action")
    if action not in ("approve", "reject"):
        return HttpResponseForbidden("Invalid action")

    with transaction.atomic():
        initial = get_object_or_404(EarlyFeeDiscountRequest, pk=request_id)
        enrollment = Enrollment.objects.select_for_update().get(
            pk=initial.enrollment_id
        )
        item = EarlyFeeDiscountRequest.objects.select_for_update().get(pk=request_id)

        if item.status != "pending":
            messages.error(request, "Request already reviewed.")
            return redirect("early_discount_approvals")

        note = request.POST.get("review_note", "").strip()
        now = timezone.now()

        if action == "approve":
            today = timezone.localdate()
            EarlyFeeDiscountRequest.objects.filter(
                enrollment=enrollment,
                status="approved",
                applied_amount=0,
                proposed_payment_date__lt=today,
            ).update(status="expired")
            EarlyFeeDiscountRequest.objects.filter(
                enrollment=enrollment,
                status="approved",
                applied_amount=0,
                due_date_at_request__lte=today,
            ).update(status="expired")

            existing_approval = EarlyFeeDiscountRequest.objects.filter(
                enrollment=enrollment,
                status="approved",
                applied_amount=0,
            ).exclude(pk=item.pk).exists()

            if existing_approval:
                messages.error(
                    request,
                    "Another approved discount is awaiting payment."
                )
                return redirect("early_discount_approvals")

            due = _due_date(enrollment)
            paid = enrollment.fee_payments.aggregate(
                total=Sum("amount")
            )["total"] or Decimal("0")
            balance = enrollment.final_fee - paid

            if (
                enrollment.status != "active"
                or timezone.localdate() >= due
                or item.proposed_payment_date < timezone.localdate()
                or item.proposed_payment_date >= due
                or not item.amount.is_finite()
                or item.amount <= 0
                or item.amount > balance
            ):
                messages.error(request, "Discount no longer eligible.")
                return redirect("early_discount_approvals")

            # Option A: approval authorizes discount; payment applies it.
            item.applied_amount = Decimal("0.00")
            item.status = "approved"
        else:
            item.status = "rejected"

        item.reviewed_by = request.user
        item.reviewed_at = now
        item.review_note = note
        item.save(update_fields=[
            "status", "applied_amount", "reviewed_by",
            "reviewed_at", "review_note"
        ])

    messages.success(request, f"Discount request {item.status}.")
    return redirect("early_discount_approvals")
