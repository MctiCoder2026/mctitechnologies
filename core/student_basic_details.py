from urllib.parse import urlencode
from django import forms
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .models import Student, Admission


def allowed_students(user):
    if not user.is_authenticated or not user.is_active:
        return Student.objects.none()
    if user.is_superuser:
        return Student.objects.all()
    profile = getattr(user, "staff_profile", None)
    if not user.is_staff or not profile or not profile.is_active:
        return Student.objects.none()
    branch = (profile.branch or "").strip()
    if not branch:
        return Student.objects.none()
    return Student.objects.filter(branch__iexact=branch)


class BasicDetailsForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["name", "date_of_birth", "photo"]
        labels = {"date_of_birth": "Date of Birth"}
        widgets = {
            "date_of_birth": forms.DateInput(
                format="%Y-%m-%d", attrs={"type": "date"}
            ),
        }

    def clean_name(self):
        value = self.cleaned_data["name"].strip()
        if not value:
            raise forms.ValidationError("Enter the student's name.")
        return value

    def clean_date_of_birth(self):
        value = self.cleaned_data.get("date_of_birth")
        if value and value > timezone.localdate():
            raise forms.ValidationError("Birth date cannot be in the future.")
        return value

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo and hasattr(photo, "size") and photo.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Photo must be 5 MB or smaller.")
        return photo


@login_required
def edit_basic_details(request, student_id):
    student = get_object_or_404(allowed_students(request.user), pk=student_id)
    form = BasicDetailsForm(
        request.POST if request.method == "POST" else None,
        request.FILES if request.method == "POST" else None,
        instance=student,
    )
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            locked = get_object_or_404(
                allowed_students(request.user).select_for_update(),
                pk=student.pk,
            )
            for field in ("name", "date_of_birth", "photo"):
                value = form.cleaned_data.get(field)
                if field == "photo" and value is False:
                    value = ""
                setattr(locked, field, value)
            updated = locked
            updated.save(update_fields=["name", "date_of_birth", "photo"])
            if updated.admission_id:
                Admission.objects.filter(pk=updated.admission_id).update(
                    student_name=updated.name,
                )
        return redirect("student_list")
    return render(request, "core/student_basic_details.html", {
        "student": student, "form": form,
    })


def birthday_context(user):
    today = timezone.localdate()
    students = allowed_students(user).filter(
        status="active",
        date_of_birth__month=today.month,
        date_of_birth__day=today.day,
    ).order_by("name", "pk")
    rows = []
    for student in students:
        number = "".join(c for c in (student.mobile or "") if c.isdigit())
        if len(number) == 12 and number.startswith("91"):
            number = number[2:]
        elif len(number) == 11 and number.startswith("0"):
            number = number[1:]
        branch = (student.branch or "MCTI").replace("_", " ").title()
        message = (
            f"Happy Birthday, {student.name}! 🎂\n\n"
            "Wishing you happiness, success and a bright future. "
            "Keep learning and growing!\n\n"
            f"— Team MCTI Technologies, {branch}"
        )
        link = ""
        if len(number) == 10 and number[0] in "6789":
            link = "https://wa.me/91" + number + "?" + urlencode({"text": message})
        rows.append({"student": student, "whatsapp_url": link})
    return {"birthday_rows": rows, "birthday_today": today,
            "birthday_user_id": user.pk}
