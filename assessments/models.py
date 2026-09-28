from django.db import models


class Assessment(models.Model):
    ASSESSMENT_TYPES = [
        ("awareness", "Awareness Quiz"),
        ("hiring", "Hiring Assessment"),
        ("staff", "Staff Assessment"),
        ("placement", "Placement Assessment"),
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
