from django import forms
from core.models import Course


class LocalEnquiryForm(forms.Form):

    name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "placeholder": "Your Name"
        })
    )

    mobile = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            "placeholder": "Mobile Number"
        })
    )

    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            "placeholder": "Email (Optional)"
        })
    )

    course = forms.ModelChoiceField(
        queryset=Course.objects.filter(
            is_active=True
        ).order_by("title"),
        empty_label="Select Course"
    )

    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "placeholder": "Message (Optional)",
            "rows": 3
        })
    )
