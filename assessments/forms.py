from django import forms


class AIReadyRegistrationForm(forms.Form):

    full_name = forms.CharField(
        max_length=150,
        label="Full Name",
        widget=forms.TextInput(
            attrs={"placeholder": "Enter your full name"}
        ),
    )

    mobile = forms.CharField(
        max_length=10,
        min_length=10,
        label="Mobile Number",
        widget=forms.TextInput(
            attrs={
                "placeholder": "10 digit mobile number",
                "inputmode": "numeric",
            }
        ),
    )

    email = forms.EmailField(
        required=False,
        label="Email",
        widget=forms.EmailInput(
            attrs={"placeholder": "Email address (optional)"}
        ),
    )

    qualification = forms.ChoiceField(
        label="Highest Qualification",
        choices=[
            ("10th", "10th"),
            ("12th", "12th"),
            ("diploma", "Diploma"),
            ("graduate", "Graduate"),
            ("postgraduate", "Postgraduate"),
            ("other", "Other"),
        ],
    )

    institution_name = forms.CharField(
        max_length=200,
        required=False,
        label="College / School / Institute",
        widget=forms.TextInput(
            attrs={"placeholder": "College, school or institute name"}
        ),
    )

    district = forms.CharField(
        max_length=100,
        label="District",
        widget=forms.TextInput(
            attrs={"placeholder": "Example: Thane"}
        ),
    )

    city = forms.CharField(
        max_length=100,
        label="City",
        widget=forms.TextInput(
            attrs={"placeholder": "Example: Navi Mumbai"}
        ),
    )

    current_status = forms.ChoiceField(
        label="Current Status",
        choices=[
            ("student", "Student"),
            ("fresher", "Fresher"),
            ("working", "Working Professional"),
            ("business", "Business / Self-employed"),
            ("other", "Other"),
        ],
    )

    career_interest = forms.CharField(
        max_length=150,
        required=False,
        label="Career Interest",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Example: AI, Data, Coding, Accounts"
            }
        ),
    )

    consent_given = forms.BooleanField(
        required=True,
        label=(
            "I agree to receive my result, certificate and "
            "career-related communication from MCTI."
        ),
    )

    def clean_mobile(self):
        mobile = "".join(
            ch for ch in self.cleaned_data["mobile"] if ch.isdigit()
        )

        if len(mobile) != 10:
            raise forms.ValidationError(
                "Enter a valid 10 digit mobile number."
            )

        return mobile
