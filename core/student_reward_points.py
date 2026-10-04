from decimal import Decimal
from django import forms
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Sum
from .forms import EnrollmentForm
from .models import Student, StudentRewardEntry

MONTHLY_POINTS = 500

def reward_balance(student):
    return StudentRewardEntry.objects.filter(
        student_id=student.pk
    ).aggregate(total=Sum("points"))["total"] or 0

def credit_attendance_points(award, actor):
    if not actor.is_active or not actor.is_superuser:
        raise PermissionDenied("Only the owner can approve reward points.")
    with transaction.atomic():
        Student.objects.select_for_update().get(pk=award.student_id)
        entry, created = StudentRewardEntry.objects.get_or_create(
            award=award,
            defaults={
                "student_id": award.student_id,
                "points": MONTHLY_POINTS,
                "description": (
                    "Monthly Attendance Star: " + award.month.strftime("%b %Y")
                ),
                "created_by": actor,
            },
        )
        if entry.points != MONTHLY_POINTS or entry.student_id != award.student_id:
            raise ValueError("Reward ledger mismatch.")
        award.reward_points = MONTHLY_POINTS
        award.save(update_fields=["reward_points"])
        return created

class RewardEnrollmentForm(EnrollmentForm):
    reward_points = forms.IntegerField(
        required=False, min_value=0, initial=0,
        label="Use reward points",
        widget=forms.NumberInput(attrs={"min": "0", "step": "1"}),
    )

    def __init__(self, *args, student, **kwargs):
        self.reward_student = student
        super().__init__(*args, **kwargs)

    def clean(self):
        data = super().clean()
        course = data.get("course")
        if not course:
            return data
        points = data.get("reward_points") or 0
        fee = Decimal(course.fee or 0)
        manual_discount = data.get("discount_amount") or Decimal("0")
        limit = max(0, int(fee * Decimal("0.10")))
        balance = reward_balance(self.reward_student)

        if points > balance:
            self.add_error("reward_points", "Not enough reward points.")
        if points > limit:
            self.add_error(
                "reward_points",
                f"Maximum {limit} points allowed for this course.",
            )
        if manual_discount + points > fee:
            self.add_error(
                "reward_points", "Combined discounts cannot exceed the course fee."
            )
        if points and (
            self.reward_student.course_id == course.pk
            or self.reward_student.enrollments.filter(course_id=course.pk).exists()
        ):
            self.add_error(
                "reward_points", "Reward points are for a different next course."
            )
        if points and data.get("status") != "active":
            self.add_error(
                "reward_points", "Points can be used only for an active enrollment."
            )

        final_fee = fee - manual_discount - points
        initial_payment = data.get("initial_payment") or Decimal("0")
        if initial_payment > final_fee:
            self.add_error(
                "initial_payment", "Initial payment exceeds the fee after rewards."
            )
        data["final_fee"] = final_fee
        return data

    def save(self, commit=True):
        enrollment = super().save(commit=False)
        points = self.cleaned_data.get("reward_points") or 0
        enrollment.reward_points_used = points
        enrollment.discount_amount += Decimal(points)
        enrollment.final_fee = enrollment.standard_fee - enrollment.discount_amount
        if commit:
            raise ValueError("Reward enrollment must use the atomic save flow.")
        return enrollment
