from django import forms
from django.forms import inlineformset_factory

from .models import (
    CareerProfile,
    Resume,
    ResumeEducation,
    ResumeExperience,
    ResumeProject,
    ResumeCertification,
)


class CareerProfileForm(forms.ModelForm):
    class Meta:
        model = CareerProfile

        fields = [
            "full_name",
            "mobile",
            "email",
            "date_of_birth",
            "highest_qualification",
            "college_name",
            "passing_year",
            "career_interest",
            "preferred_job_role",
            "skills",
            "languages",
            "city",
            "consent_given",
        ]

        widgets = {
            "date_of_birth": forms.DateInput(
                attrs={
                    "type": "date"
                }
            ),

            "skills": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": (
                        "Example: MS Office, Excel, "
                        "Tally, Python"
                    )
                }
            ),

            "consent_given": forms.CheckboxInput(),
        }


class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume

        fields = [
            "title",
            "professional_summary",
            "objective",
        ]

        widgets = {
            "professional_summary": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": (
                        "Write a short professional summary"
                    )
                }
            ),

            "objective": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": (
                        "Write your career objective"
                    )
                }
            ),
        }


class GuestCareerStartForm(forms.Form):

    full_name = forms.CharField(
        max_length=150,
        label="Full Name",

        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your full name"
            }
        )
    )

    mobile = forms.CharField(
        max_length=15,
        min_length=10,
        label="Mobile Number",

        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "10 digit mobile number",
                "inputmode": "numeric"
            }
        )
    )

    consent_given = forms.BooleanField(
        required=True,
        label=(
            "I agree to share my details with "
            "MCTI for career guidance."
        )
    )

    def clean_mobile(self):

        mobile = self.cleaned_data[
            "mobile"
        ].strip()

        digits = "".join(
            filter(
                str.isdigit,
                mobile
            )
        )

        if (
            len(digits) == 12
            and digits.startswith("91")
        ):
            digits = digits[2:]

        if len(digits) != 10:
            raise forms.ValidationError(
                "Please enter a valid 10 digit mobile number."
            )

        return digits


# =========================================================
# RESUME EDUCATION FORMSET
# =========================================================

EducationFormSet = inlineformset_factory(
    Resume,
    ResumeEducation,

    fields=[
        "qualification",
        "institute_name",
        "board_university",
        "start_year",
        "end_year",
        "percentage_cgpa",
        "order",
    ],

    extra=1,
    can_delete=True,
)


# =========================================================
# RESUME EXPERIENCE FORMSET
# =========================================================

ExperienceFormSet = inlineformset_factory(
    Resume,
    ResumeExperience,

    fields=[
        "company_name",
        "job_title",
        "start_date",
        "end_date",
        "currently_working",
        "description",
        "order",
    ],

    widgets={
        "start_date": forms.DateInput(
            attrs={
                "type": "date"
            }
        ),

        "end_date": forms.DateInput(
            attrs={
                "type": "date"
            }
        ),

        "description": forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": (
                    "Describe your responsibilities "
                    "and achievements"
                )
            }
        ),
    },

    extra=1,
    can_delete=True,
)


# =========================================================
# RESUME PROJECT FORMSET
# =========================================================

ProjectFormSet = inlineformset_factory(
    Resume,
    ResumeProject,

    fields=[
        "project_title",
        "project_url",
        "description",
        "order",
    ],

    widgets={
        "description": forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": (
                    "Describe your project"
                )
            }
        ),
    },

    extra=1,
    can_delete=True,
)


# =========================================================
# RESUME CERTIFICATION FORMSET
# =========================================================

CertificationFormSet = inlineformset_factory(
    Resume,
    ResumeCertification,

    fields=[
        "certification_name",
        "issuing_organization",
        "issue_year",
        "order",
    ],

    extra=1,
    can_delete=True,
)