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


# ============================================================
# HR HIRING APPLICATION FORM
# ============================================================

class HiringApplicationForm(forms.Form):

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

    qualification = forms.CharField(
        max_length=150,
        label="Highest Qualification",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Example: BCA, BSc IT, BE, BCom"
            }
        ),
    )

    experience = forms.CharField(
        max_length=150,
        required=False,
        label="Experience",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Example: Fresher / 2 Years"
            }
        ),
    )

    city = forms.CharField(
        max_length=100,
        label="Current City",
        widget=forms.TextInput(
            attrs={"placeholder": "Example: Navi Mumbai"}
        ),
    )

    job_role = forms.ModelChoiceField(
        queryset=None,
        label="Applying For",
        empty_label="Select Job Role",
    )

    employment_type = forms.ChoiceField(
        label="Employment Preference",
        choices=[
            ("intern", "Intern"),
            ("part_time", "Part-Time"),
            ("full_time", "Full-Time"),
            ("trainer", "Trainer"),
        ],
    )

    consent_given = forms.BooleanField(
        required=True,
        label=(
            "I confirm that the information provided is correct "
            "and agree to participate in the MCTI hiring assessment."
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        from .models import HiringJobRole

        self.fields["job_role"].queryset = (
            HiringJobRole.objects.filter(
                is_active=True,
                assessment__is_active=True,
            )
            .select_related("assessment")
            .order_by("name")
        )

    def clean_mobile(self):
        mobile = "".join(
            ch for ch in self.cleaned_data["mobile"]
            if ch.isdigit()
        )

        if len(mobile) != 10:
            raise forms.ValidationError(
                "Enter a valid 10 digit mobile number."
            )

        return mobile


class HiringEvaluationForm(forms.Form):
    decision = forms.ChoiceField(
        label="Final HR Decision",
        choices=[
            ("", "Select Decision"),
            ("selected", "Select Candidate"),
            ("hold", "Hold for Review"),
            ("rejected", "Reject Candidate"),
        ],
    )

    notes = forms.CharField(
        label="HR Decision Notes",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": (
                    "Reason for selection, hold or rejection..."
                ),
            }
        ),
    )


class HiringInterviewProfileForm(forms.Form):

    about_yourself = forms.ChoiceField(
        label="1. Which option describes you best?",
        choices=[
            ("", "Select"),
            ("Fresher looking for first opportunity", "Fresher looking for first opportunity"),
            ("Student looking for internship / part-time work", "Student looking for internship / part-time work"),
            ("Working professional looking for growth", "Working professional looking for growth"),
            ("Experienced trainer / teacher", "Experienced trainer / teacher"),
            ("Experienced professional changing career", "Experienced professional changing career"),
            ("Freelancer / independent professional", "Freelancer / independent professional"),
        ],
    )

    why_mcti = forms.ChoiceField(
        label="2. Why do you want to join MCTI Technologies?",
        choices=[
            ("", "Select"),
            ("Career Growth", "Career Growth"),
            ("Teaching Opportunity", "Teaching Opportunity"),
            ("Learning New Technologies", "Learning New Technologies"),
            ("Industry Exposure", "Industry Exposure"),
            ("Long-term Career Opportunity", "Long-term Career Opportunity"),
            ("Training + Practical Experience", "Training + Practical Experience"),
        ],
    )

    why_select_you = forms.ChoiceField(
        label="3. Why should we select you?",
        choices=[
            ("", "Select"),
            ("Strong Technical Skills", "Strong Technical Skills"),
            ("Good Communication Skills", "Good Communication Skills"),
            ("Strong Teaching Ability", "Strong Teaching Ability"),
            ("Good Practical Experience", "Good Practical Experience"),
            ("Fast Learner", "Fast Learner"),
            ("Disciplined and Responsible", "Disciplined and Responsible"),
            ("Combination of Technical and Communication Skills", "Combination of Technical and Communication Skills"),
        ],
    )

    strengths = forms.ChoiceField(
        label="4. What is your strongest quality?",
        choices=[
            ("", "Select"),
            ("Technical Knowledge", "Technical Knowledge"),
            ("Communication", "Communication"),
            ("Teaching", "Teaching"),
            ("Problem Solving", "Problem Solving"),
            ("Discipline", "Discipline"),
            ("Leadership", "Leadership"),
            ("Sales and Convincing", "Sales and Convincing"),
            ("Quick Learning", "Quick Learning"),
        ],
    )

    weakness_improving = forms.ChoiceField(
        label="5. Which area are you currently improving?",
        choices=[
            ("", "Select"),
            ("Communication", "Communication"),
            ("Technical Depth", "Technical Depth"),
            ("Confidence", "Confidence"),
            ("Time Management", "Time Management"),
            ("Teaching Skills", "Teaching Skills"),
            ("Sales Skills", "Sales Skills"),
            ("Leadership", "Leadership"),
            ("Public Speaking", "Public Speaking"),
        ],
    )

    role_interest = forms.ChoiceField(
        label="6. Why are you interested in this role?",
        choices=[
            ("", "Select"),
            ("My skills match this role", "My skills match this role"),
            ("I already have experience in this field", "I already have experience in this field"),
            ("I want to build my career in this field", "I want to build my career in this field"),
            ("I am interested in teaching this subject", "I am interested in teaching this subject"),
            ("I want practical industry experience", "I want practical industry experience"),
            ("This role offers good growth opportunities", "This role offers good growth opportunities"),
        ],
    )

    career_goals = forms.ChoiceField(
        label="7. What is your main career goal for the next 2–3 years?",
        choices=[
            ("", "Select"),
            ("Become a Subject Expert", "Become a Subject Expert"),
            ("Become a Professional Trainer", "Become a Professional Trainer"),
            ("Become a Developer / Technical Professional", "Become a Developer / Technical Professional"),
            ("Become a Team Leader", "Become a Team Leader"),
            ("Move into Management", "Move into Management"),
            ("Start My Own Business", "Start My Own Business"),
            ("Still Exploring My Career", "Still Exploring My Career"),
        ],
    )

    current_learning = forms.ChoiceField(
        label="8. What are you currently learning or improving?",
        required=False,
        choices=[
            ("", "Select"),
            ("Artificial Intelligence", "Artificial Intelligence"),
            ("Programming / Development", "Programming / Development"),
            ("Data Analytics", "Data Analytics"),
            ("Cloud / AWS", "Cloud / AWS"),
            ("Cyber Security", "Cyber Security"),
            ("Digital Marketing", "Digital Marketing"),
            ("Accounting / Tally / Excel", "Accounting / Tally / Excel"),
            ("Communication / English", "Communication / English"),
            ("Teaching / Presentation Skills", "Teaching / Presentation Skills"),
        ],
    )

    why_train_students = forms.ChoiceField(
        label="9. If this is a Trainer role, why do you want to train students?",
        required=False,
        choices=[
            ("", "Not Applicable / Select"),
            ("I enjoy teaching", "I enjoy teaching"),
            ("I want to share my knowledge", "I want to share my knowledge"),
            ("I want to build my career as a trainer", "I want to build my career as a trainer"),
            ("Teaching is one of my strengths", "Teaching is one of my strengths"),
            ("I like both technology and teaching", "I like both technology and teaching"),
            ("I enjoy helping students solve problems", "I enjoy helping students solve problems"),
        ],
    )

    job_source = forms.ChoiceField(
        label="10. Where did you hear about this job?",
        choices=[
            ("", "Select"),
            ("LinkedIn", "LinkedIn"),
            ("Indeed", "Indeed"),
            ("Naukri", "Naukri"),
            ("WhatsApp", "WhatsApp"),
            ("Instagram", "Instagram"),
            ("Facebook", "Facebook"),
            ("Google", "Google"),
            ("MCTI Student / Alumni", "MCTI Student / Alumni"),
            ("Employee Reference", "Employee Reference"),
            ("Friend / Relative", "Friend / Relative"),
            ("Walk-in", "Walk-in"),
            ("Other", "Other"),
        ],
    )

    expected_salary = forms.DecimalField(
        label="11. Expected Monthly Salary / Stipend (₹)",
        required=False,
        min_value=0,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            "placeholder": "Example: 15000",
            "min": "0",
        }),
    )

    joining_availability = forms.ChoiceField(
        label="12. When can you join?",
        choices=[
            ("Immediately", "Immediately"),
            ("Within 7 Days", "Within 7 Days"),
            ("Within 15 Days", "Within 15 Days"),
            ("Within 30 Days", "Within 30 Days"),
            ("More than 30 Days", "More than 30 Days"),
        ],
    )


# ============================================================
# MCTI SCHOLARSHIP TEST REGISTRATION
# ============================================================

class ScholarshipRegistrationForm(forms.Form):

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
        label="Email Address",
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

    institution_name = forms.CharField(
        max_length=200,
        required=False,
        label="College / School / Institute",
        widget=forms.TextInput(
            attrs={"placeholder": "College, school or institute name"}
        ),
    )

    city = forms.CharField(
        max_length=100,
        label="City",
        widget=forms.TextInput(
            attrs={"placeholder": "Example: Navi Mumbai"}
        ),
    )

    course = forms.ChoiceField(
        label="Course You Are Interested In",
        choices=[],
    )

    preferred_branch = forms.ChoiceField(
        label="Preferred MCTI Branch",
        choices=[],
    )

    consent_given = forms.BooleanField(
        required=True,
        label=(
            "I agree to receive my scholarship result, admission guidance "
            "and career-related communication from MCTI."
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        from core.models import Course, BranchLocation

        self.fields["course"].choices = [
            (course.title, course.title)
            for course in Course.objects.filter(
                is_active=True
            ).order_by("display_order", "title")
        ]

        self.fields["preferred_branch"].choices = [
            (branch.branch_name, branch.branch_name)
            for branch in BranchLocation.objects.filter(
                is_active=True
            ).order_by("branch_name")
        ]

    def clean_mobile(self):
        mobile = "".join(
            ch for ch in self.cleaned_data["mobile"]
            if ch.isdigit()
        )

        if len(mobile) != 10:
            raise forms.ValidationError(
                "Enter a valid 10 digit mobile number."
            )

        return mobile
