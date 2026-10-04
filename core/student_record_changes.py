from decimal import Decimal

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import (
    Admission, Attendance, Enrollment, FeePayment,
    MonthlyBranchClosing, Student, StudentRecordChangeAudit,
)
from .student_basic_details import allowed_students


class ChangeForm(forms.Form):
    new_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
    )
    status = forms.ChoiceField(
        required=False,
        choices=[("active", "Active Student"), ("completed", "Ex Student")],
    )
    enrollment = forms.ModelChoiceField(
        queryset=Enrollment.objects.none(), required=False,
        label="Original enrollment to update with admission date (optional)",
    )
    reason = forms.CharField(
        min_length=10, max_length=2000,
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    def clean_new_date(self):
        value = self.cleaned_data.get("new_date")
        if value and value > timezone.localdate():
            raise forms.ValidationError("Future date is not allowed.")
        return value


def check_months(branch, dates):
    for value in set(dates):
        closing = MonthlyBranchClosing.objects.select_for_update().filter(
            branch__iexact=(branch or "").strip(),
            year=value.year, month=value.month,
        ).first()
        if closing and closing.status != "draft":
            raise forms.ValidationError(
                f"{value:%B %Y} is submitted/locked. Date correction blocked."
            )


@login_required
@require_http_methods(["GET", "POST"])
def change_record(request, kind, record_id):
    if kind not in ("student", "admission", "receipt"):
        return HttpResponseForbidden("Invalid record.")
    if kind != "student" and not (
        request.user.is_active and request.user.is_superuser
    ):
        return HttpResponseForbidden("Only the Power User can change dates.")

    if kind == "student":
        record = get_object_or_404(
            allowed_students(request.user), pk=record_id,
        )
        student = record
        initial = {"status": record.status}
    elif kind == "admission":
        record = get_object_or_404(Admission, pk=record_id)
        student = Student.objects.filter(admission_id=record.pk).first()
        initial = {"new_date": record.admission_date}
    else:
        record = get_object_or_404(
            FeePayment.objects.select_related("student"), pk=record_id,
        )
        student = record.student
        initial = {"new_date": record.payment_date}

    form = ChangeForm(
        request.POST if request.method == "POST" else None,
        initial=initial,
    )
    if kind == "student":
        form.fields.pop("new_date")
        form.fields.pop("enrollment")
        choices = list(form.fields["status"].choices)
        if record.status not in ("active", "completed"):
            choices.append((record.status, record.get_status_display()))
        form.fields["status"].choices = choices
        form.fields["status"].required = True
    else:
        form.fields.pop("status")
        form.fields["new_date"].required = True
        if kind == "admission" and student:
            form.fields["enrollment"].queryset = Enrollment.objects.filter(
                student_id=student.pk,
            ).order_by("pk")
        else:
            form.fields.pop("enrollment")

    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                reason = form.cleaned_data["reason"].strip()
                if student:
                    student = Student.objects.select_for_update().get(pk=student.pk)

                if kind == "student":
                    # Recheck branch permission inside the transaction.
                    record = get_object_or_404(
                        allowed_students(request.user).select_for_update(),
                        pk=record_id,
                    )
                    before = {"status": record.status}
                    after = {"status": form.cleaned_data["status"]}
                    if before == after:
                        raise forms.ValidationError("Status is unchanged.")
                    record.status = after["status"]
                    record.save(update_fields=["status"])
                elif kind == "admission":
                    record = Admission.objects.select_for_update().get(pk=record_id)
                    old = record.admission_date
                    new = form.cleaned_data["new_date"]
                    chosen = form.cleaned_data.get("enrollment")
                    enrollment = None
                    if chosen:
                        enrollment = Enrollment.objects.select_for_update().get(
                            pk=chosen.pk, student_id=student.pk,
                        )
                        if enrollment.status == "cancelled":
                            raise forms.ValidationError(
                                "Cancelled enrollment cannot be selected."
                            )
                        check_months(
                            enrollment.branch or student.branch,
                            [enrollment.enrollment_date, new],
                        )
                    check_months(
                        record.branch or (student.branch if student else ""),
                        [old, new],
                    )
                    before = {"admission_date": str(old)}
                    after = {"admission_date": str(new)}
                    if enrollment:
                        before["enrollment_id"] = enrollment.pk
                        after["enrollment_id"] = enrollment.pk
                        before["enrollment_date"] = str(enrollment.enrollment_date)
                        after["enrollment_date"] = str(new)
                    if before == after:
                        raise forms.ValidationError("Date is unchanged.")
                    record.admission_date = new
                    record.save(update_fields=["admission_date"])
                    if student:
                        before["joining_date"] = str(student.joining_date)
                        after["joining_date"] = str(new)
                        Student.objects.filter(pk=student.pk).update(joining_date=new)
                    if enrollment:
                        Enrollment.objects.filter(pk=enrollment.pk).update(
                            enrollment_date=new,
                        )
                else:
                    record = FeePayment.objects.select_for_update().get(pk=record_id)
                    if record.student_id != student.pk:
                        raise forms.ValidationError("Receipt changed; reload.")
                    enrollment = None
                    if record.enrollment_id:
                        enrollment = Enrollment.objects.select_for_update().get(
                            pk=record.enrollment_id,
                        )
                    old = record.payment_date
                    new = form.cleaned_data["new_date"]
                    check_months(
                        (enrollment.branch if enrollment else "") or student.branch,
                        [old, new],
                    )
                    if old == new:
                        raise forms.ValidationError("Date is unchanged.")
                    if record.correction_requests.filter(status="pending").exists():
                        raise forms.ValidationError(
                            "Review the pending receipt correction first."
                        )
                    before = {"payment_date": str(old),
                              "receipt_number": record.receipt_number}
                    after = {"payment_date": str(new),
                             "receipt_number": record.receipt_number}
                    record.payment_date = new
                    record.save(update_fields=["payment_date"])

                    payments = FeePayment.objects.select_for_update()
                    if enrollment:
                        payments = payments.filter(enrollment_id=enrollment.pk)
                        total_fee = enrollment.final_fee
                    else:
                        payments = payments.filter(
                            student_id=student.pk, enrollment__isnull=True,
                        )
                        admission = (
                            Admission.objects.select_for_update().get(
                                pk=student.admission_id
                            ) if student.admission_id else None
                        )
                        total_fee = admission.total_fee if admission else Decimal("0")
                    payments = list(payments.order_by("payment_date", "pk"))
                    running = Decimal("0")
                    for payment in payments:
                        payment.previous_paid = running
                        running += payment.amount
                        payment.balance_after_payment = max(
                            total_fee-running, Decimal("0"),
                        )
                    FeePayment.objects.bulk_update(
                        payments, ["previous_paid", "balance_after_payment"],
                    )

                StudentRecordChangeAudit.objects.create(
                    record_type=kind, record_id=record.pk,
                    before=before, after=after, reason=reason,
                    changed_by=request.user,
                )
        except forms.ValidationError as error:
            form.add_error(None, error)
        else:
            messages.success(request, "Change saved; audit history retained.")
            if kind == "receipt":
                return redirect("fee_receipt", receipt_number=record.receipt_number)
            if kind == "admission":
                return redirect("admission_detail", admission_id=record.pk)
            return redirect("student_list")

    return render(request, "core/student_record_change.html", {
        "form": form, "kind": kind, "record": record, "student": student,
    })
