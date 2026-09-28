from django.db import models
from django.conf import settings


class Assessment(models.Model):
    ASSESSMENT_TYPES = [
        ("awareness", "Awareness Quiz"),
        ("hiring", "Hiring Assessment"),
        ("staff", "Staff Assessment"),
        ("placement", "Placement Assessment"),
        ("scholarship", "Scholarship Test"),
        ("other", "Other"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)

    assessment_type = models.CharField(
        max_length=30,
        choices=ASSESSMENT_TYPES,
        default="awareness",
    )

    description = models.TextField(blank=True)

    total_questions = models.PositiveIntegerField(default=25)
    passing_score = models.PositiveIntegerField(default=0)

    duration_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(default=True)
    certificate_enabled = models.BooleanField(default=False)
    lead_capture_enabled = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class AssessmentQuestion(models.Model):
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="questions",
    )

    question_text = models.TextField()
    category = models.CharField(max_length=100, blank=True)

    order = models.PositiveIntegerField(default=1)
    marks = models.PositiveIntegerField(default=1)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.assessment.title} - Q{self.order}"


class AssessmentOption(models.Model):
    question = models.ForeignKey(
        AssessmentQuestion,
        on_delete=models.CASCADE,
        related_name="options",
    )

    option_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.option_text


class AssessmentAttempt(models.Model):
    STATUS_CHOICES = [
        ("started", "Started"),
        ("completed", "Completed"),
        ("abandoned", "Abandoned"),
    ]

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.PROTECT,
        related_name="attempts",
    )

    participant_profile = models.ForeignKey(
        "AssessmentParticipantProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attempts",
    )

    participant_name = models.CharField(max_length=150)
    participant_mobile = models.CharField(max_length=20, blank=True)
    participant_email = models.EmailField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="started",
    )

    score = models.PositiveIntegerField(default=0)
    total_marks = models.PositiveIntegerField(default=0)
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.participant_name} - {self.assessment.title}"


class AssessmentAnswer(models.Model):
    attempt = models.ForeignKey(
        AssessmentAttempt,
        on_delete=models.CASCADE,
        related_name="answers",
    )

    question = models.ForeignKey(
        AssessmentQuestion,
        on_delete=models.PROTECT,
        related_name="answers",
    )

    selected_option = models.ForeignKey(
        AssessmentOption,
        on_delete=models.PROTECT,
        related_name="selected_answers",
        null=True,
        blank=True,
    )

    is_correct = models.BooleanField(default=False)
    marks_awarded = models.PositiveIntegerField(default=0)

    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["attempt", "question"],
                name="unique_assessment_attempt_question",
            )
        ]

    def __str__(self):
        return f"{self.attempt_id} - Q{self.question_id}"


class AssessmentResult(models.Model):
    attempt = models.OneToOneField(
        AssessmentAttempt,
        on_delete=models.CASCADE,
        related_name="result",
    )

    result_band = models.CharField(max_length=100)
    result_title = models.CharField(max_length=200, blank=True)
    result_message = models.TextField(blank=True)
    recommendation = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.attempt.participant_name} - {self.result_band}"


class AssessmentCertificate(models.Model):
    attempt = models.OneToOneField(
        AssessmentAttempt,
        on_delete=models.CASCADE,
        related_name="certificate",
    )

    certificate_id = models.CharField(
        max_length=50,
        unique=True,
    )

    verification_token = models.CharField(
        max_length=100,
        unique=True,
    )

    issued_at = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)

    def __str__(self):
        return self.certificate_id


class AssessmentParticipantProfile(models.Model):
    CURRENT_STATUS_CHOICES = [
        ("student", "Student"),
        ("fresher", "Fresher"),
        ("working", "Working Professional"),
        ("business", "Business / Self Employed"),
        ("other", "Other"),
    ]

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.PROTECT,
        related_name="participant_profiles",
    )

    full_name = models.CharField(max_length=150)
    mobile = models.CharField(max_length=20)
    email = models.EmailField(blank=True)

    qualification = models.CharField(max_length=150, blank=True)
    institution_name = models.CharField(max_length=200, blank=True)

    district = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)

    current_status = models.CharField(
        max_length=30,
        choices=CURRENT_STATUS_CHOICES,
        blank=True,
    )

    career_interest = models.CharField(max_length=150, blank=True)

    enquiry = models.ForeignKey(
        "core.Enquiry",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assessment_profiles",
    )

    consent_given = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["mobile"]),
            models.Index(fields=["district"]),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.mobile}"

# ============================================================
# MCTI SCHOLARSHIP TEST
# ============================================================

class ScholarshipResult(models.Model):
    CLAIM_STATUS_CHOICES = [
        ("new", "New"),
        ("test_completed", "Test Completed"),
        ("contacted", "Contacted"),
        ("interested", "Interested"),
        ("sent_to_enquiry", "Sent to Enquiry"),
        ("not_interested", "Not Interested"),
        ("claimed", "Scholarship Claimed"),
        ("converted", "Converted"),
        ("expired", "Expired"),
    ]

    attempt = models.OneToOneField(
        AssessmentAttempt,
        on_delete=models.CASCADE,
        related_name="scholarship_result",
    )

    scholarship_percentage = models.PositiveIntegerField(default=0)
    scholarship_band = models.CharField(max_length=100, blank=True)

    selected_course = models.CharField(max_length=200, blank=True)
    preferred_branch = models.CharField(max_length=100, blank=True)

    claim_status = models.CharField(
        max_length=20,
        choices=CLAIM_STATUS_CHOICES,
        default="new",
    )

    valid_until = models.DateField(null=True, blank=True)
    claimed_at = models.DateTimeField(null=True, blank=True)

    counsellor_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.attempt.participant_name} - "
            f"{self.scholarship_percentage}% Scholarship"
        )


# ============================================================
# HR HIRING ASSESSMENT SYSTEM
# ============================================================

class HiringJobRole(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=170, unique=True)
    description = models.TextField(blank=True)

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="hiring_job_roles",
    )

    technical_weight = models.PositiveIntegerField(default=100)
    practical_weight = models.PositiveIntegerField(default=0)
    communication_weight = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class HiringSalaryMatrix(models.Model):
    EMPLOYMENT_TYPES = [
        ("intern", "Intern"),
        ("part_time", "Part-Time"),
        ("full_time", "Full-Time"),
        ("trainer", "Trainer"),
    ]

    PERFORMANCE_BANDS = [
        ("not_shortlisted", "Below 40 - Not Shortlisted"),
        ("trainee", "40-54 - Trainee"),
        ("junior", "55-69 - Junior"),
        ("skilled", "70-84 - Skilled"),
        ("advanced", "85-100 - Advanced"),
    ]

    job_role = models.ForeignKey(
        HiringJobRole,
        on_delete=models.CASCADE,
        related_name="salary_matrix",
    )

    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPES,
    )

    performance_band = models.CharField(
        max_length=30,
        choices=PERFORMANCE_BANDS,
    )

    min_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    max_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "job_role",
                    "employment_type",
                    "performance_band",
                ],
                name="unique_hiring_salary_matrix",
            )
        ]

    def __str__(self):
        return (
            f"{self.job_role.name} - "
            f"{self.get_employment_type_display()} - "
            f"{self.get_performance_band_display()}"
        )


class HiringCandidate(models.Model):
    full_name = models.CharField(max_length=150)
    mobile = models.CharField(max_length=20)
    email = models.EmailField(blank=True)

    qualification = models.CharField(max_length=150, blank=True)
    experience = models.CharField(max_length=150, blank=True)
    city = models.CharField(max_length=100, blank=True)

    resume_url = models.URLField(blank=True)

    consent_given = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["mobile"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.mobile}"


class HiringApplication(models.Model):
    STATUS_CHOICES = [
        ("applied", "Applied"),
        ("test_pending", "Test Pending"),
        ("test_completed", "Test Completed"),
        ("practical_pending", "Practical Pending"),
        ("shortlisted", "Shortlisted"),
        ("selected", "Selected"),
        ("hold", "Hold"),
        ("rejected", "Rejected"),
        ("joined", "Joined"),
    ]

    candidate = models.ForeignKey(
        HiringCandidate,
        on_delete=models.PROTECT,
        related_name="applications",
    )

    job_role = models.ForeignKey(
        HiringJobRole,
        on_delete=models.PROTECT,
        related_name="applications",
    )

    employment_type = models.CharField(
        max_length=20,
        choices=HiringSalaryMatrix.EMPLOYMENT_TYPES,
    )

    assessment_attempt = models.OneToOneField(
        AssessmentAttempt,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hiring_application",
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="applied",
    )

    source = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.candidate.full_name} - {self.job_role.name}"


class HiringEvaluation(models.Model):
    application = models.OneToOneField(
        HiringApplication,
        on_delete=models.CASCADE,
        related_name="evaluation",
    )

    technical_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    practical_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    communication_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    final_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    performance_band = models.CharField(
        max_length=30,
        choices=HiringSalaryMatrix.PERFORMANCE_BANDS,
        blank=True,
    )

    suggested_salary_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    suggested_salary_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    approved_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    evaluated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hiring_evaluations",
    )

    evaluated_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.application} - {self.final_score}%"


class HiringInterviewProfile(models.Model):
    """
    Standard pre-assessment interview profile.

    These answers provide HR context and are NOT automatically
    converted into hiring marks.
    """

    application = models.OneToOneField(
        HiringApplication,
        on_delete=models.CASCADE,
        related_name="interview_profile",
    )

    about_yourself = models.TextField()
    why_mcti = models.TextField()
    why_select_you = models.TextField()
    strengths = models.TextField()
    weakness_improving = models.TextField()

    career_goals = models.TextField()
    current_learning = models.TextField(blank=True)
    role_interest = models.TextField()

    why_train_students = models.TextField(
        blank=True,
        help_text="Primarily for trainer roles.",
    )

    job_source = models.CharField(
        max_length=150,
        blank=True,
    )

    expected_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    joining_availability = models.CharField(
        max_length=150,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Interview Profile - {self.application.candidate.full_name}"
