from decimal import Decimal
import json

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .models import (
    Enrollment, FeePayment, FeePaymentDeletionAudit,
    MonthlyBranchClosing, Student,
)


class DeleteReceiptForm(forms.Form):
    reason = forms.CharField(
        min_length=10, max_length=2000,
        widget=forms.Textarea(attrs={"rows": 3}),
        label="Reason for deleting this receipt",
    )
    receipt_number = forms.CharField(
        max_length=30, label="Type the receipt number to confirm",
    )
    confirm = forms.BooleanField(
        label="I confirm this receipt entry is incorrect.",
    )


@login_required
@require_http_methods(["GET", "POST"])
def delete_receipt(request, payment_id):
    if not (request.user.is_active and request.user.is_superuser):
        return HttpResponseForbidden("Only the active superuser can delete receipts.")

    payment = get_object_or_404(
        FeePayment.objects.select_related("student", "enrollment__course"),
        pk=payment_id,
    )
    form = DeleteReceiptForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if form.cleaned_data["receipt_number"].strip() != payment.receipt_number:
            form.add_error("receipt_number", "Receipt number does not match.")
        else:
            try:
                with transaction.atomic():
                    student = Student.objects.select_for_update().get(
                        pk=payment.student_id,
                    )
                    enrollment = None
                    if payment.enrollment_id:
                        enrollment = Enrollment.objects.select_for_update().get(
                            pk=payment.enrollment_id,
                        )
                    locked = FeePayment.objects.select_for_update().get(pk=payment.pk)
                    if (
                        locked.student_id != payment.student_id
                        or locked.enrollment_id != payment.enrollment_id
                        or locked.amount != payment.amount
                        or locked.receipt_number != payment.receipt_number
                        or locked.payment_date != payment.payment_date
                    ):
                        return HttpResponse("Receipt changed; reload and review.", status=409)

                    branch = (
                        enrollment.branch if enrollment else student.branch
                    ) or ""
                    closing = MonthlyBranchClosing.objects.select_for_update().filter(
                        branch__iexact=branch.strip(),
                        year=locked.payment_date.year,
                        month=locked.payment_date.month,
                    ).first()
                    if closing and closing.status != "draft":
                        return HttpResponse(
                            "This payment month is submitted/locked. "
                            "Receipt deletion is blocked.", status=409,
                        )
                    corrections = list(
                        locked.correction_requests.select_for_update().order_by("pk")
                    )

                    snapshot = {
                        f.attname: getattr(locked, f.attname)
                        for f in locked._meta.concrete_fields
                    }
                    snapshot["correction_history"] = [
                        {
                            f.attname: getattr(correction, f.attname)
                            for f in correction._meta.concrete_fields
                        }
                        for correction in corrections
                    ]
                    snapshot["student_name"] = student.name
                    snapshot["student_identifier"] = student.student_id
                    snapshot["branch"] = branch
                    snapshot["course"] = str(enrollment.course) if enrollment else ""
                    snapshot = json.loads(json.dumps(
                        snapshot, cls=DjangoJSONEncoder,
                    ))

                    if enrollment:
                        remaining = list(
                            FeePayment.objects.select_for_update().filter(
                                enrollment_id=enrollment.pk,
                            ).exclude(pk=locked.pk).order_by("payment_date", "pk")
                        )
                        total_fee = enrollment.final_fee
                    else:
                        remaining = list(
                            FeePayment.objects.select_for_update().filter(
                                student_id=student.pk, enrollment__isnull=True,
                            ).exclude(pk=locked.pk).order_by("payment_date", "pk")
                        )
                        admission = student.admission
                        total_fee = admission.total_fee if admission else Decimal("0")

                    FeePaymentDeletionAudit.objects.create(
                        original_payment_id=locked.pk,
                        receipt_number=locked.receipt_number,
                        snapshot=snapshot,
                        reason=form.cleaned_data["reason"].strip(),
                        deleted_by=request.user,
                        deleted_by_name=(
                            request.user.get_full_name().strip() or request.user.username
                        ),
                    )
                    receipt = locked.receipt_number
                    # Full correction history is already saved in the audit snapshot.
                    if corrections:
                        locked.correction_requests.filter(
                            pk__in=[item.pk for item in corrections]
                        ).delete()
                    locked.delete()
                    running = Decimal("0")
                    for item in remaining:
                        item.previous_paid = running
                        running += item.amount
                        item.balance_after_payment = max(total_fee-running, Decimal("0"))
                    if remaining:
                        FeePayment.objects.bulk_update(
                            remaining, ["previous_paid", "balance_after_payment"],
                        )
            except ProtectedError:
                form.add_error(
                    None, "Another record protects this receipt. No changes were saved.",
                )
            else:
                messages.success(request, f"{receipt} deleted; audit copy retained.")
                return redirect("fee_payment_list")
    return render(request, "core/delete_fee_receipt.html", {
        "payment": payment, "form": form,
    })
