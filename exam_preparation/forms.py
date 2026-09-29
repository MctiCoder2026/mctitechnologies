from django import forms
from .models import SSCStudent
from core.models import BranchLocation


class SSCStudentRegistrationForm(forms.ModelForm):

    class Meta:
        model = SSCStudent
        fields = [
            "full_name",
            "mobile",
            "school_name",
            "medium",
            "city",
            "preferred_branch",
            "consent_given",
        ]

        widgets = {
            "full_name": forms.TextInput(attrs={
                "placeholder": "Student Name",
                "class": "form-control",
            }),
            "mobile": forms.TextInput(attrs={
                "placeholder": "10 Digit Mobile Number",
                "inputmode": "numeric",
                "class": "form-control",
            }),
            "school_name": forms.TextInput(attrs={
                "placeholder": "School Name",
                "class": "form-control",
            }),
            "medium": forms.Select(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={
                "placeholder": "City",
                "class": "form-control",
            }),
            "preferred_branch": forms.Select(attrs={"class": "form-control"}),
            "consent_given": forms.CheckboxInput(),
        }

        labels = {
            "full_name": "Student Name",
            "mobile": "Mobile Number",
            "school_name": "School Name",
            "medium": "Medium",
            "city": "City",
            "preferred_branch": "Preferred MCTI Centre",
            "consent_given": "I agree to receive educational guidance and updates from MCTI.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["preferred_branch"].queryset = (
            BranchLocation.objects
            .filter(is_active=True)
            .order_by("branch_name")
        )

        self.fields["preferred_branch"].required = False
        self.fields["city"].required = False
        self.fields["consent_given"].required = True

    def clean_mobile(self):
        mobile = "".join(
            ch for ch in self.cleaned_data["mobile"] if ch.isdigit()
        )

        if len(mobile) != 10:
            raise forms.ValidationError(
                "Please enter a valid 10 digit mobile number."
            )

        return mobile


class SSCStudentLoginForm(forms.Form):
    mobile = forms.CharField(
        max_length=10,
        min_length=10,
        label="Registered Mobile Number",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your 10 digit registered mobile",
                "inputmode": "numeric",
                "autocomplete": "tel",
            }
        ),
    )

    def clean_mobile(self):
        mobile = "".join(
            filter(str.isdigit, self.cleaned_data["mobile"])
        )

        if len(mobile) != 10:
            raise forms.ValidationError(
                "Enter a valid 10 digit mobile number."
            )

        return mobile
