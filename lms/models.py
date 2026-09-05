from django.db import models
from django.conf import settings

from core.models import Course, Student


# =========================================================
# LMS MODULE
# =========================================================

class LMSModule(models.Model):

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lms_modules"
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    order = models.PositiveIntegerField(
        default=1
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["course", "order"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


# =========================================================
# LMS TOPIC
# =========================================================

class LMSTopic(models.Model):

    module = models.ForeignKey(
        LMSModule,
        on_delete=models.CASCADE,
        related_name="topics"
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    order = models.PositiveIntegerField(
        default=1
    )

    # Optional video
    video_url = models.URLField(
        blank=True
    )

    # Optional files
    notes_file = models.FileField(
        upload_to="lms/notes/",
        blank=True,
        null=True
    )

    practice_file = models.FileField(
        upload_to="lms/practice/",
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["module", "order"]

    def __str__(self):
        return f"{self.module.title} - {self.title}"


# =========================================================
# QUIZ QUESTION
# =========================================================

class QuizQuestion(models.Model):

    topic = models.ForeignKey(
        LMSTopic,
        on_delete=models.CASCADE,
        related_name="quiz_questions"
    )

    question = models.TextField()

    option_a = models.CharField(
        max_length=300
    )

    option_b = models.CharField(
        max_length=300
    )

    option_c = models.CharField(
        max_length=300
    )

    option_d = models.CharField(
        max_length=300
    )

    CORRECT_CHOICES = [
        ("A", "Option A"),
        ("B", "Option B"),
        ("C", "Option C"),
        ("D", "Option D"),
    ]

    correct_answer = models.CharField(
        max_length=1,
        choices=CORRECT_CHOICES
    )

    order = models.PositiveIntegerField(
        default=1
    )

    is_active = models.BooleanField(
        default=True
    )

    class Meta:
        ordering = ["topic", "order"]

    def __str__(self):
        return f"{self.topic.title} - Q{self.order}"


# =========================================================
# STUDENT TOPIC PROGRESS
# =========================================================

class StudentTopicProgress(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="lms_topic_progress"
    )

    topic = models.ForeignKey(
        LMSTopic,
        on_delete=models.CASCADE,
        related_name="student_progress"
    )

    is_unlocked = models.BooleanField(
        default=False
    )

    is_completed = models.BooleanField(
        default=False
    )

    best_score = models.PositiveIntegerField(
        default=0
    )

    total_questions = models.PositiveIntegerField(
        default=0
    )

    attempts = models.PositiveIntegerField(
        default=0
    )

    last_attempt_at = models.DateTimeField(
        blank=True,
        null=True
    )

    completed_at = models.DateTimeField(
        blank=True,
        null=True
    )

    class Meta:
        unique_together = (
            "student",
            "topic",
        )

    def __str__(self):
        return f"{self.student} - {self.topic}"


# =========================================================
# QUIZ ATTEMPT
# =========================================================

class QuizAttempt(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="lms_quiz_attempts"
    )

    topic = models.ForeignKey(
        LMSTopic,
        on_delete=models.CASCADE,
        related_name="quiz_attempts"
    )

    score = models.PositiveIntegerField(
        default=0
    )

    total_questions = models.PositiveIntegerField(
        default=0
    )

    passed = models.BooleanField(
        default=False
    )

    attempted_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.student} - "
            f"{self.topic.title} - "
            f"{self.score}/{self.total_questions}"
        )