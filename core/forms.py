from django import forms
from django.contrib.auth.models import User

from .models import (
    Enquiry,
    Admission,
    FeePayment,
    JobPost,
)



BRANCH_CHOICES = [
    ("", "Select Branch"),
    ("kharghar", "Kharghar"),
    ("panvel", "Panvel"),
    ("koperkhairane", "Koperkhairane"),
    ("kamothe", "Kamothe"),
    ("ghansoli", "Ghansoli"),
    ("nerul", "Nerul"),
]



# ============================================================
# ENQUIRY FORM
# ============================================================

class EnquiryForm(forms.ModelForm):

    class Meta:
        model = Enquiry

        fields = [
            "name",
            "mobile",
            "email",
            "course",
            "branch",
            "message",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Your Name",
                    "class": "form-control",
                }
            ),

            "mobile": forms.TextInput(
                attrs={
                    "placeholder": "Mobile Number",
                    "class": "form-control",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "placeholder": "Email Address",
                    "class": "form-control",
                }
            ),

            "course": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "branch": forms.Select(
                choices=[
                    ("", "Select Preferred Branch"),
                    ("kharghar", "Kharghar"),
                    ("panvel", "Panvel"),
                    ("koperkhairane", "Koperkhairane"),
                    ("kamothe", "Kamothe"),
                    ("ghansoli", "Ghansoli"),
                    ("nerul", "Nerul"),
                ],
                attrs={
                    "class": "form-control",
                }
            ),

            "message": forms.Textarea(
                attrs={
                    "placeholder": "Your Message",
                    "rows": 5,
                    "class": "form-control",
                }
            ),
        }


# ============================================================
# ENQUIRY STATUS FORM
# ============================================================

class EnquiryStatusForm(forms.ModelForm):

    class Meta:
        model = Enquiry

        fields = [
            "status",
        ]

        widgets = {
            "status": forms.Select(
                attrs={
                    "class": "mcti-status-select",
                }
            )
        }


# ============================================================
# ENQUIRY FOLLOW-UP FORM
# ============================================================

class EnquiryFollowupForm(forms.ModelForm):

    class Meta:
        model = Enquiry

        fields = [
            "followup_date",
            "followup_notes",
        ]

        widgets = {
            "followup_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),

            "followup_notes": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Follow-up notes...",
                    "class": "form-control",
                }
            ),
        }


# ============================================================
# ENQUIRY STAFF ASSIGNMENT FORM
# ============================================================

class EnquiryAssignmentForm(forms.ModelForm):

    class Meta:
        model = Enquiry

        fields = [
            "assigned_user",
        ]

        widgets = {
            "assigned_user": forms.Select(
                attrs={
                    "class": "mcti-assigned-select",
                }
            )
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["assigned_user"].queryset = (
            User.objects.filter(
                is_active=True
            ).order_by(
                "first_name",
                "username"
            )
        )

        self.fields["assigned_user"].label = "Assign Staff"
        self.fields["assigned_user"].required = False
        self.fields["assigned_user"].empty_label = "Not Assigned"


# ============================================================
# ADMISSION FORM
# ============================================================

class AdmissionForm(forms.ModelForm):

    class Meta:
        model = Admission

        fields = [
            "student_name",
            "mother_name",
            "mobile",
            "secondary_mobile",
            "email",
            "address",
            "photo",
            "course",
            "branch",
            "admission_date",
            "total_fee",
            "paid_fee",
            "initial_payment_mode",
            "notes",
        ]

        widgets = {

            "student_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Student Name",
                }
            ),

            "mother_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Mother Name",
                }
            ),

            "mobile": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Primary Mobile Number",
                }
            ),

            "secondary_mobile": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Secondary Mobile Number",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Email Address",
                }
            ),

            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Full Address",
                    "rows": 3,
                }
            ),

            "photo": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),

            "course": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "branch": forms.Select(
                choices=BRANCH_CHOICES,
                attrs={
                    "class": "form-control",
                }
            ),

            "admission_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "total_fee": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Total Fee",
                    "min": "0",
                    "step": "0.01",
                }
            ),

            "paid_fee": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Paid Fee",
                    "min": "0",
                    "step": "0.01",
                }
            ),

            "initial_payment_mode": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Admission notes...",
                    "rows": 4,
                }
            ),
        }

    def __init__(self, *args, enquiry=None, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["branch"].required = True
        self.fields["branch"].choices = BRANCH_CHOICES

        if enquiry and not self.instance.pk:

            self.fields["student_name"].initial = enquiry.name
            self.fields["mobile"].initial = enquiry.mobile
            self.fields["email"].initial = enquiry.email
            self.fields["course"].initial = enquiry.course
            self.fields["branch"].initial = enquiry.branch

# ============================================================
# FEE PAYMENT FORM
# ============================================================

class FeePaymentForm(forms.ModelForm):

    class Meta:
        model = FeePayment

        fields = [
            "amount",
            "payment_mode",
            "transaction_id",
            "remarks",
        ]

        widgets = {

            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Payment Amount",
                    "min": "1",
                    "step": "0.01",
                }
            ),

            "payment_mode": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "transaction_id": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Transaction / UTR Number",
                }
            ),

            "remarks": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Payment remarks...",
                    "rows": 3,
                }
            ),
        }

# ============================================================
# ADMISSION EDIT FORM
# ============================================================

class AdmissionEditForm(forms.ModelForm):

    class Meta:
        model = Admission

        fields = [
            "student_name",
            "mother_name",
            "mobile",
            "secondary_mobile",
            "email",
            "address",
            "photo",
            "course",
            "branch",
            "admission_date",
            "total_fee",
            "notes",
        ]

        widgets = {
            "student_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Student Name",
                }
            ),

            "mother_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Mother Name",
                }
            ),

            "mobile": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Mobile Number",
                }
            ),

            "secondary_mobile": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Secondary Mobile Number",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Email Address",
                }
            ),

            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Full Address",
                }
            ),

            "photo": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),

            "course": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "branch": forms.Select(
                choices=BRANCH_CHOICES,
                attrs={
                    "class": "form-control",
                }
            ),

            "admission_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "total_fee": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "step": "0.01",
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["branch"].required = True
        self.fields["branch"].choices = BRANCH_CHOICES

        # If old Admission.branch is blank, automatically use the
        # branch selected earlier in the original Enquiry.
        if (
            self.instance
            and self.instance.pk
            and not self.instance.branch
            and getattr(self.instance, "enquiry_id", None)
            and self.instance.enquiry
            and self.instance.enquiry.branch
        ):
            self.fields["branch"].initial = self.instance.enquiry.branch


# ============================================================
# JOB POST FORM
# ============================================================

class JobPostForm(forms.ModelForm):

    class Meta:

        model = JobPost

        fields = [
            "title",
            "company_name",
            "location",
            "salary",
            "experience",
            "required_skills",
            "description",
            "eligibility",
            "eligible_courses",
            "apply_link",
            "contact_email",
            "contact_mobile",
            "last_date",
            "status",
        ]

        widgets = {

            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Job Title",
                }
            ),

            "company_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Company Name",
                }
            ),

            "location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Job Location",
                }
            ),

            "salary": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: ₹18,000 - ₹25,000",
                }
            ),

            "experience": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: Fresher / 1-2 Years",
                }
            ),

            "required_skills": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Required Skills",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Job Description",
                }
            ),

            "eligibility": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Eligibility",
                }
            ),

            "eligible_courses": forms.SelectMultiple(
                attrs={
                    "class": "form-control",
                }
            ),

            "apply_link": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://...",
                }
            ),

            "contact_email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "HR Email",
                }
            ),

            "contact_mobile": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "HR Contact Number",
                }
            ),

            "last_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
        }
