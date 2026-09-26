from decimal import Decimal

from django import forms
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Enrollment, FeePayment, FeePaymentCorrection, Student
from .views import is_admin_user, staff_or_admin, user_can_access_student


class CorrectionForm(forms.Form):
    requested_amount = forms.DecimalField(
        min_value=Decimal("0.01"), max_digits=10, decimal_places=2,
        label="Correct payment amount",
    )
    reason = forms.CharField(
        min_length=10, max_length=2000, widget=forms.Textarea,
        label="Why is this receipt wrong?",
    )


def _display_name(user):
    return user.get_full_name().strip() or user.username


@login_required
def request_correction(request, payment_id):
    if not staff_or_admin(request.user):
        return HttpResponseForbidden("Staff access required.")
    payment = get_object_or_404(
        FeePayment.objects.select_related("student", "enrollment"),
        pk=payment_id,
    )
    if not user_can_access_student(request.user, payment.student):
        return HttpResponseForbidden("Student belongs to another branch.")
    pending = payment.correction_requests.filter(status="pending").first()
    form = CorrectionForm(request.POST or None)
    if request.method == "POST":
        if pending:
            return HttpResponse("This receipt already has a pending request.", status=409)
        if form.is_valid():
            requested = form.cleaned_data["requested_amount"]
            if requested == payment.amount:
                form.add_error("requested_amount", "Enter an amount different from the receipt.")
            else:
                with transaction.atomic():
                    locked = FeePayment.objects.select_for_update().get(pk=payment.pk)
                    if locked.amount != payment.amount:
                        return HttpResponse("Receipt changed; reload this page.", status=409)
                    if FeePaymentCorrection.objects.filter(payment=locked, status="pending").exists():
                        return HttpResponse("Correction already pending.", status=409)
                    FeePaymentCorrection.objects.create(
                        payment=locked,
                        original_amount=locked.amount,
                        requested_amount=requested,
                        reason=form.cleaned_data["reason"].strip(),
                        requested_by=request.user,
                        requested_by_name=_display_name(request.user),
                    )
                return redirect("fee_correction_queue")
    return render(request, "core/fee_correction_request.html", {
        "payment": payment, "pending": pending, "form": form,
    })


@login_required
def correction_queue(request):
    if not staff_or_admin(request.user):
        return HttpResponseForbidden("Staff access required.")
    records = FeePaymentCorrection.objects.select_related(
        "payment__student", "payment__enrollment__course",
    ).order_by("-requested_at", "-id")
    if not is_admin_user(request.user):
        branch = request.user.staff_profile.branch
        records = records.filter(payment__student__branch__iexact=branch)
    return render(request, "core/fee_correction_queue.html", {
        "records": records[:200],
        "can_review": is_admin_user(request.user),
        "pending_count": records.filter(status="pending").count(),
    })


@login_required
@require_POST
def review_correction(request, correction_id):
    if not is_admin_user(request.user):
        return HttpResponseForbidden("Only HO/admin can review receipt corrections.")
    decision = request.POST.get("decision")
    note = request.POST.get("review_note", "").strip()[:2000]
    if decision not in ("approved", "rejected"):
        return HttpResponse("Choose approve or reject.", status=400)
    if decision == "rejected" and len(note) < 5:
        return HttpResponse("Give a rejection reason.", status=400)

    with transaction.atomic():
        correction = get_object_or_404(
            FeePaymentCorrection.objects.select_for_update(), pk=correction_id,
        )
        if correction.status != "pending":
            return HttpResponse("Already reviewed.", status=409)
        payment = FeePayment.objects.select_for_update().get(pk=correction.payment_id)
        if payment.amount != correction.original_amount:
            return HttpResponse("Receipt has changed; review again.", status=409)

        if decision == "approved":
            if payment.enrollment_id:
                enrollment = Enrollment.objects.select_for_update().get(
                    pk=payment.enrollment_id,
                )
                total_fee = enrollment.final_fee
                payments = list(
                    FeePayment.objects.select_for_update().filter(
                        enrollment=enrollment,
                    ).order_by("payment_date", "id")
                )
            else:
                student = Student.objects.select_for_update().select_related(
                    "admission",
                ).get(pk=payment.student_id)
                total_fee = student.admission.total_fee if student.admission else Decimal("0")
                payments = list(
                    FeePayment.objects.select_for_update().filter(
                        student=student, enrollment__isnull=True,
                    ).order_by("payment_date", "id")
                )
            new_total = sum(
                (correction.requested_amount if p.pk == payment.pk else p.amount)
                for p in payments
            )
            if correction.requested_amount > payment.amount and new_total > total_fee:
                return HttpResponse("Correction exceeds the total fee.", status=400)
            running = Decimal("0")
            for item in payments:
                if item.pk == payment.pk:
                    item.amount = correction.requested_amount
                item.previous_paid = running
                running += item.amount
                item.balance_after_payment = max(total_fee - running, Decimal("0"))
            FeePayment.objects.bulk_update(
                payments, ["amount", "previous_paid", "balance_after_payment"],
            )

        correction.status = decision
        correction.reviewed_by = request.user
        correction.reviewed_by_name = _display_name(request.user)
        correction.reviewed_at = timezone.now()
        correction.review_note = note
        correction.save(update_fields=[
            "status", "reviewed_by", "reviewed_by_name",
            "reviewed_at", "review_note",
        ])
    return redirect("fee_correction_queue")
