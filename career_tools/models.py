from django.db import models
from django.conf import settings
from core.models import Student, Enquiry


class CareerProfile(models.Model):
    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="career_profile"
    )

    enquiry = models.ForeignKey(
        Enquiry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="career_profiles"
    )

    full_name = models.CharField(max_length=150)
    mobile = models.CharField(max_length=20)
    email = models.EmailField(blank=True)

    date_of_birth = models.DateField(null=True, blank=True)

    highest_qualification = models.CharField(max_length=150, blank=True)
    college_name = models.CharField(max_length=200, blank=True)
    passing_year = models.PositiveIntegerField(null=True, blank=True)

    career_interest = models.CharField(max_length=200, blank=True)
    preferred_job_role = models.CharField(max_length=200, blank=True)

    skills = models.TextField(blank=True)
    languages = models.CharField(max_length=250, blank=True)

    city = models.CharField(max_length=100, blank=True)

    is_guest = models.BooleanField(default=False)
    consent_given = models.BooleanField(default=False)

    source = models.CharField(
        max_length=100,
        default="MCTI Career Kit"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name


class Resume(models.Model):
    profile = models.ForeignKey(
        CareerProfile,
        on_delete=models.CASCADE,
        related_name="resumes"
    )

    title = models.CharField(
        max_length=150,
        default="Professional Resume"
    )

    professional_summary = models.TextField(blank=True)

    objective = models.TextField(blank=True)

    template_name = models.CharField(
        max_length=50,
        default="professional"
    )

    is_default = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.profile.full_name} - {self.title}"


class ResumeEducation(models.Model):
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name="education"
    )

    qualification = models.CharField(max_length=150)
    institute_name = models.CharField(max_length=200, blank=True)
    board_university = models.CharField(max_length=200, blank=True)

    start_year = models.PositiveIntegerField(null=True, blank=True)
    end_year = models.PositiveIntegerField(null=True, blank=True)

    percentage_cgpa = models.CharField(max_length=50, blank=True)

    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.qualification


class ResumeExperience(models.Model):
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name="experience"
    )

    company_name = models.CharField(max_length=200)
    job_title = models.CharField(max_length=150)

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    currently_working = models.BooleanField(default=False)

    description = models.TextField(blank=True)

    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.job_title} - {self.company_name}"


class ResumeProject(models.Model):
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name="projects"
    )

    project_title = models.CharField(max_length=200)
    project_url = models.URLField(blank=True)
    description = models.TextField(blank=True)

    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.project_title


class ResumeCertification(models.Model):
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name="certifications"
    )

    certification_name = models.CharField(max_length=200)
    issuing_organization = models.CharField(max_length=200, blank=True)

    issue_year = models.PositiveIntegerField(null=True, blank=True)

    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.certification_name
    
    # =========================================================
# APTITUDE TEST
# =========================================================

class AptitudeQuestion(models.Model):

    CATEGORY_CHOICES = [
        ("numerical", "Numerical Aptitude"),
        ("logical", "Logical Reasoning"),
        ("verbal", "Verbal Ability"),
        ("computer", "Computer / Digital Aptitude"),
        ("career", "Career / Work Aptitude"),
    ]

    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES
    )

    question = models.TextField()

    option_a = models.CharField(max_length=250)
    option_b = models.CharField(max_length=250)
    option_c = models.CharField(max_length=250)
    option_d = models.CharField(max_length=250)

    CORRECT_OPTION_CHOICES = [
        ("A", "A"),
        ("B", "B"),
        ("C", "C"),
        ("D", "D"),
    ]

    correct_option = models.CharField(
        max_length=1,
        choices=CORRECT_OPTION_CHOICES
    )

    explanation = models.TextField(
        blank=True
    )

    difficulty = models.CharField(
        max_length=20,
        choices=[
            ("easy", "Easy"),
            ("medium", "Medium"),
            ("hard", "Hard"),
        ],
        default="medium"
    )

    is_active = models.BooleanField(
        default=True
    )

    order = models.PositiveIntegerField(
        default=1
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "category",
            "order",
            "id"
        ]

    def __str__(self):
        return (
            f"{self.get_category_display()} - "
            f"{self.question[:60]}"
        )


class AptitudeAttempt(models.Model):

    profile = models.ForeignKey(
        CareerProfile,
        on_delete=models.CASCADE,
        related_name="aptitude_attempts"
    )

    total_questions = models.PositiveIntegerField(
        default=0
    )

    attempted_questions = models.PositiveIntegerField(
        default=0
    )

    correct_answers = models.PositiveIntegerField(
        default=0
    )

    score_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    numerical_score = models.PositiveIntegerField(
        default=0
    )

    logical_score = models.PositiveIntegerField(
        default=0
    )

    verbal_score = models.PositiveIntegerField(
        default=0
    )

    computer_score = models.PositiveIntegerField(
        default=0
    )

    career_score = models.PositiveIntegerField(
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("started", "Started"),
            ("completed", "Completed"),
        ],
        default="started"
    )

    started_at = models.DateTimeField(
        auto_now_add=True
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return (
            f"{self.profile.full_name} - "
            f"{self.score_percentage}%"
        )


class AptitudeAnswer(models.Model):

    attempt = models.ForeignKey(
        AptitudeAttempt,
        on_delete=models.CASCADE,
        related_name="answers"
    )

    question = models.ForeignKey(
        AptitudeQuestion,
        on_delete=models.CASCADE,
        related_name="answers"
    )

    selected_option = models.CharField(
        max_length=1,
        choices=[
            ("A", "A"),
            ("B", "B"),
            ("C", "C"),
            ("D", "D"),
        ]
    )

    is_correct = models.BooleanField(
        default=False
    )

    answered_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "attempt",
                    "question",
                ],
                name="unique_aptitude_answer_per_attempt"
            )
        ]

    def __str__(self):
        return (
            f"{self.attempt.profile.full_name} - "
            f"Q{self.question_id}"
        )
    # =========================================================
# CAREER RECOMMENDATION
# =========================================================

class CareerRecommendation(models.Model):
    profile = models.ForeignKey(
        CareerProfile,
        on_delete=models.CASCADE,
        related_name="career_recommendations"
    )

    aptitude_attempt = models.ForeignKey(
        AptitudeAttempt,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="career_recommendations"
    )

    overall_summary = models.TextField(
        blank=True
    )

    strongest_area = models.CharField(
        max_length=100,
        blank=True
    )

    improvement_area = models.CharField(
        max_length=100,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("generated", "Generated"),
            ("reviewed", "Reviewed"),
        ],
        default="generated"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return (
            f"{self.profile.full_name} - "
            f"Recommendation #{self.id}"
        )


class CareerRecommendationItem(models.Model):
    recommendation = models.ForeignKey(
        CareerRecommendation,
        on_delete=models.CASCADE,
        related_name="items"
    )

    rank = models.PositiveIntegerField(
        default=1
    )

    career_title = models.CharField(
        max_length=150
    )

    match_percentage = models.PositiveIntegerField(
        default=0
    )

    reason = models.TextField(
        blank=True
    )

    skills_to_improve = models.TextField(
        blank=True
    )

    recommended_course = models.CharField(
        max_length=200,
        blank=True
    )

    next_step = models.TextField(
        blank=True
    )

    class Meta:
        ordering = [
            "rank",
            "id",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "recommendation",
                    "rank",
                ],
                name="unique_recommendation_rank"
            )
        ]

    def __str__(self):
        return (
            f"{self.rank}. "
            f"{self.career_title}"
        )