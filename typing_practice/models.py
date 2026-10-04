from django.db import models
from core.models import Student


class TypingLesson(models.Model):

    LEVEL_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]

    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True)

    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default="beginner"
    )

    order = models.PositiveIntegerField(default=1)

    content = models.TextField()

    target_wpm = models.PositiveIntegerField(default=20)
    target_accuracy = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=90
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class TypingAttempt(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="typing_attempts"
    )

    lesson = models.ForeignKey(
        TypingLesson,
        on_delete=models.CASCADE,
        related_name="attempts"
    )

    wpm = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0
    )

    accuracy = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    errors = models.PositiveIntegerField(default=0)

    typed_characters = models.PositiveIntegerField(default=0)

    duration_seconds = models.PositiveIntegerField(default=0)

    passed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.student.student_id} - "
            f"{self.lesson.title} - "
            f"{self.wpm} WPM"
        )


class TypingProgress(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="typing_progress"
    )

    lesson = models.ForeignKey(
        TypingLesson,
        on_delete=models.CASCADE,
        related_name="student_progress"
    )

    best_wpm = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0
    )

    best_accuracy = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    best_errors = models.PositiveIntegerField(default=0)

    attempts_count = models.PositiveIntegerField(default=0)

    is_completed = models.BooleanField(default=False)

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "lesson"],
                name="unique_student_typing_lesson_progress"
            )
        ]

    def __str__(self):
        return (
            f"{self.student.student_id} - "
            f"{self.lesson.title}"
        )


# ============================================================
# TYPING V2 - EXAMS
# ============================================================

class TypingExam(models.Model):

    lesson = models.OneToOneField(
        TypingLesson,
        on_delete=models.CASCADE,
        related_name="exam"
    )

    title = models.CharField(max_length=150)

    content = models.TextField()

    target_wpm = models.PositiveIntegerField(default=20)

    target_accuracy = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=90
    )

    duration_seconds = models.PositiveIntegerField(
        default=60
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class TypingExamAttempt(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="typing_exam_attempts"
    )

    exam = models.ForeignKey(
        TypingExam,
        on_delete=models.CASCADE,
        related_name="attempts"
    )

    branch = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    wpm = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0
    )

    accuracy = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    errors = models.PositiveIntegerField(default=0)

    typed_characters = models.PositiveIntegerField(default=0)

    duration_seconds = models.PositiveIntegerField(default=0)

    passed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.student.student_id} - "
            f"{self.exam.title}"
        )


# ============================================================
# TYPING V2 - GAMES
# ============================================================

class TypingGameAttempt(models.Model):

    GAME_CHOICES = [
        ("letter_rush", "Letter Rush"),
        ("word_burst", "Word Burst"),
        ("speed_60", "60 Second Challenge"),
        ("accuracy", "Accuracy Challenge"),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="typing_game_attempts"
    )

    game_type = models.CharField(
        max_length=30,
        choices=GAME_CHOICES
    )

    branch = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    score = models.PositiveIntegerField(default=0)

    wpm = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0
    )

    accuracy = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    duration_seconds = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


# ============================================================
# TYPING V2 - DAILY ACTIVITY / ACCOUNTABILITY
# ============================================================

class TypingActivity(models.Model):

    ACTIVITY_CHOICES = [
        ("practice", "Practice"),
        ("exam", "Exam"),
        ("game", "Game"),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="typing_activity"
    )

    branch = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    activity_type = models.CharField(
        max_length=20,
        choices=ACTIVITY_CHOICES
    )

    duration_seconds = models.PositiveIntegerField(default=0)

    typed_characters = models.PositiveIntegerField(default=0)
    active_seconds = models.PositiveIntegerField(default=0)


    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


# ============================================================
# TYPING V2 - FINAL LEVEL PROGRESS
# Practice does NOT pass a level.
# Official exam controls level completion.
# ============================================================

class TypingLevelProgress(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="typing_level_progress"
    )

    lesson = models.ForeignKey(
        TypingLesson,
        on_delete=models.CASCADE,
        related_name="level_progress"
    )

    exam_attempts = models.PositiveIntegerField(default=0)

    best_exam_wpm = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0
    )

    best_exam_accuracy = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    exam_passed = models.BooleanField(default=False)

    passed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "lesson"],
                name="unique_student_typing_level"
            )
        ]

    def __str__(self):
        return (
            f"{self.student.student_id} - "
            f"{self.lesson.title}"
        )


# Typing achievement certificate: permanent issuance snapshot.
import uuid


class TypingCertificate(models.Model):
    CERTIFICATE_TYPES = [
        ("legacy", "Previously Issued Achievement"),
        ("basic", "English Typing - 30 WPM"),
        ("master", "Master in English Typing - 40 WPM"),
    ]
    certificate_type = models.CharField(
        max_length=10,
        choices=CERTIFICATE_TYPES,
        default="legacy",
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="typing_certificates",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "certificate_type"],
                name="unique_typing_certificate_per_type",
            )
        ]

    @property
    def achievement_title(self):
        return {
            "basic": "English Typing - 30 Words Per Minute",
            "master": "Master in English Typing - 40 Words Per Minute",
        }.get(self.certificate_type, "MCTI English Typing")

    verification_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    student_name = models.CharField(max_length=255)
    student_identifier = models.CharField(max_length=100)
    final_wpm = models.DecimalField(max_digits=7, decimal_places=2)
    final_accuracy = models.DecimalField(max_digits=5, decimal_places=2)
    benchmarks_completed = models.PositiveIntegerField()
    completed_at = models.DateTimeField()
    issued_at = models.DateTimeField(auto_now_add=True)

    @property
    def certificate_number(self):
        return f"MCTI-TYP-{self.pk:06d}"

    def __str__(self):
        return f"{self.certificate_number} - {self.student_name}"


class TypingWeeklyReward(models.Model):
    STATUS_CHOICES = [
        ("eligible", "Eligible"),
        ("approved", "Approved"),
        ("given", "Gift Given"),
        ("rejected", "Rejected"),
    ]
    REWARD_CHOICES = [
        ("consistency", "Consistent Performer"),
        ("star", "Weekly Typing Star"),
    ]
    student = models.ForeignKey(
        Student, on_delete=models.PROTECT,
        related_name="typing_rewards",
    )
    week_start = models.DateField()
    reward_type = models.CharField(max_length=20, choices=REWARD_CHOICES)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="eligible"
    )
    qualifying_days = models.PositiveIntegerField(default=0)
    active_minutes = models.PositiveIntegerField(default=0)
    gift_description = models.CharField(max_length=255, blank=True)
    approved_by = models.ForeignKey(
        "auth.User", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="approved_typing_rewards",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    fulfilled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "week_start", "reward_type"],
                name="unique_student_week_typing_reward",
            )
        ]

    def __str__(self):
        return f"{self.student} - {self.week_start} - {self.reward_type}"
