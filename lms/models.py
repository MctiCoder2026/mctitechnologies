import uuid

from django.db import models
from django.conf import settings
from django.utils import timezone

from core.models import Course, Student, StaffProfile


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
# LMS TOPIC CONTENT - MULTILINGUAL
# =========================================================

class LMSTopicContent(models.Model):

    LANGUAGE_CHOICES = [
        ("en", "English"),
        ("hi", "Hindi"),
        ("mr", "Marathi"),
    ]

    topic = models.ForeignKey(
        LMSTopic,
        on_delete=models.CASCADE,
        related_name="contents"
    )

    language = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        default="en"
    )

    description = models.TextField(
        blank=True
    )

    video_url = models.URLField(
        blank=True
    )

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
        unique_together = (
            "topic",
            "language",
        )

        ordering = (
            "topic",
            "language",
        )

    def __str__(self):
        return (
            f"{self.topic.title} - "
            f"{self.get_language_display()}"
        )


# =========================================================
# QUIZ QUESTION
# =========================================================

class QuizQuestion(models.Model):

    LANGUAGE_CHOICES = [
        ("en", "English"),
        ("hi", "Hindi"),
        ("mr", "Marathi"),
    ]

    topic = models.ForeignKey(
        LMSTopic,
        on_delete=models.CASCADE,
        related_name="quiz_questions"
    )

    language = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        default="en"
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


# =========================================================
# CERTIFICATE
# =========================================================

class Certificate(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="lms_certificates"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lms_certificates"
    )

    certificate_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True
    )

    verification_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    issue_date = models.DateField(
        auto_now_add=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = (
            "student",
            "course",
        )
        ordering = ["-issue_date"]

    def save(self, *args, **kwargs):

        if not self.certificate_number:

            year = (
                self.issue_date.year
                if self.issue_date
                else timezone.now().year
            )

            unique_code = self.verification_token.hex[:10].upper()

            self.certificate_number = (
                f"MCTI-CERT-{year}-{unique_code}"
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.certificate_number} - "
            f"{self.student.name}"
        )

# =========================================================
# STAFF LMS TOPIC PROGRESS
# =========================================================

class StaffTopicProgress(models.Model):

    staff = models.ForeignKey(
        StaffProfile,
        on_delete=models.CASCADE,
        related_name="lms_topic_progress"
    )

    topic = models.ForeignKey(
        LMSTopic,
        on_delete=models.CASCADE,
        related_name="staff_progress"
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
        null=True,
        blank=True
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        unique_together = (
            "staff",
            "topic",
        )

    def __str__(self):
        return (
            f"{self.staff} - "
            f"{self.topic.title} - "
            f"{self.best_score}/{self.total_questions}"
        )


# =========================================================
# STAFF QUIZ ATTEMPT
# =========================================================

class StaffQuizAttempt(models.Model):

    staff = models.ForeignKey(
        StaffProfile,
        on_delete=models.CASCADE,
        related_name="lms_quiz_attempts"
    )

    topic = models.ForeignKey(
        LMSTopic,
        on_delete=models.CASCADE,
        related_name="staff_quiz_attempts"
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

    class Meta:
        ordering = ["-attempted_at"]

    def __str__(self):
        return (
            f"{self.staff} - "
            f"{self.topic.title} - "
            f"{self.score}/{self.total_questions}"
        )

# =========================================================
# CLASSROOM TEACHING DELIVERY TRACKER
# =========================================================

class TrainingDeliverySession(models.Model):

    SESSION_TYPE_CHOICES = [
        ("regular", "Regular Class"),
        ("doubt_reteach", "Doubt Re-teaching"),
        ("revision", "Revision"),
    ]

    topic = models.ForeignKey(
        "TrainingChecklistItem",
        on_delete=models.PROTECT,
        related_name="delivery_sessions"
    )

    branch = models.CharField(
        max_length=100,
        blank=True
    )

    assigned_trainer = models.ForeignKey(
        StaffProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_delivery_sessions"
    )

    taught_by = models.ForeignKey(
        StaffProfile,
        on_delete=models.PROTECT,
        related_name="delivered_training_sessions"
    )

    session_type = models.CharField(
        max_length=20,
        choices=SESSION_TYPE_CHOICES,
        default="regular"
    )

    session_date = models.DateField(
        default=timezone.localdate
    )

    notes = models.TextField(
        blank=True
    )

    enrollments = models.ManyToManyField(
        "core.Enrollment",
        through="TrainingDeliveryEnrollment",
        related_name="teaching_delivery_sessions"
    )

    standard_snapshot = models.JSONField(
        default=dict,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-session_date", "-id"]

    def __str__(self):
        return (
            f"{self.topic} - {self.session_date} - "
            f"{self.taught_by}"
        )


class TrainingDeliveryEnrollment(models.Model):

    session = models.ForeignKey(
        TrainingDeliverySession,
        on_delete=models.CASCADE,
        related_name="student_records"
    )

    enrollment = models.ForeignKey(
        "core.Enrollment",
        on_delete=models.CASCADE,
        related_name="teaching_delivery_records"
    )

    practice_verified_at = models.DateTimeField(
        null=True,
        blank=True
    )

    practice_verified_by = models.ForeignKey(
        StaffProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_student_lab_practices"
    )

    practice_evidence = models.TextField(blank=True)

    class Meta:
        unique_together = (
            "session",
            "enrollment",
        )

    def __str__(self):
        return (
            f"{self.enrollment.student} - "
            f"{self.session.topic}"
        )


class LMSTopicDoubt(models.Model):

    STATUS_CHOICES = [
        ("open", "Open"),
        ("cleared", "Cleared"),
    ]

    enrollment = models.ForeignKey(
        "core.Enrollment",
        on_delete=models.CASCADE,
        related_name="lms_topic_doubts"
    )

    topic = models.ForeignKey(
        "TrainingChecklistItem",
        on_delete=models.PROTECT,
        related_name="student_doubts"
    )

    question = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open"
    )

    opened_at = models.DateTimeField(
        auto_now_add=True
    )

    resolved_at = models.DateTimeField(
        null=True,
        blank=True
    )

    resolved_by = models.ForeignKey(
        StaffProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_lms_doubts"
    )

    resolution_session = models.ForeignKey(
        TrainingDeliverySession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_doubts"
    )

    trainer_note = models.TextField(
        blank=True
    )

    class Meta:
        ordering = ["status", "-opened_at"]

    def __str__(self):
        return (
            f"{self.enrollment.student} - "
            f"{self.topic} - {self.status}"
        )


# =========================================================
# APPROVED CLASSROOM CHECKLIST
# =========================================================

class TrainingChecklistItem(models.Model):

    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="training_checklist_items"
    )

    lms_topic = models.OneToOneField(
        LMSTopic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="classroom_checklist_item"
    )

    module_title = models.CharField(max_length=200)
    module_order = models.PositiveIntegerField(default=1)
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=1)

    learning_outcome = models.TextField(blank=True)
    trainer_steps = models.TextField(blank=True)
    student_practice = models.TextField(blank=True)
    completion_check = models.TextField(blank=True)

    expected_sessions = models.PositiveSmallIntegerField(default=1)
    version = models.PositiveIntegerField(default=1)
    is_published = models.BooleanField(default=False)

    approved_by = models.ForeignKey(
        StaffProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_training_checklist_items"
    )

    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("course_id", "module_order", "order", "id")

    def __str__(self):
        return f"{self.course.title} - {self.module_title} - {self.title}"

# =========================================================
# STUDENT COURSE DELIVERY PLAN
# =========================================================

class TrainingDeliveryPlan(models.Model):

    enrollment = models.ForeignKey(
        "core.Enrollment",
        on_delete=models.CASCADE,
        related_name="training_delivery_plans"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="training_delivery_plans"
    )

    assigned_trainer = models.ForeignKey(
        StaffProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_course_delivery_plans"
    )

    start_item = models.ForeignKey(
        TrainingChecklistItem,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="enrollment_start_plans"
    )

    baseline_note = models.TextField(blank=True)

    target_completion_date = models.DateField(
        null=True,
        blank=True
    )

    revised_completion_date = models.DateField(
        null=True,
        blank=True
    )

    revision_reason = models.TextField(blank=True)

    weekly_classes = models.PositiveSmallIntegerField(
        null=True,
        blank=True
    )

    set_by = models.ForeignKey(
        StaffProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_course_delivery_plans"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("enrollment", "course"),)

    def __str__(self):
        return f"{self.enrollment} - {self.course.title} - Training Plan"


# Independent trainer login. Staff passwords are never shared.
class ClassroomTrainer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="classroom_trainer_profile",
    )
    name = models.CharField(max_length=120)
    branch = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.branch})"


class WeeklyTeachingAssignment(models.Model):
    enrollment = models.ForeignKey(
        "core.Enrollment", on_delete=models.PROTECT,
        related_name="weekly_teaching_assignments",
    )
    topic = models.ForeignKey(
        TrainingChecklistItem, on_delete=models.PROTECT,
        related_name="weekly_teaching_assignments",
    )
    trainer = models.ForeignKey(
        ClassroomTrainer, on_delete=models.PROTECT,
        related_name="weekly_assignments",
    )
    week_start = models.DateField()
    assigned_by = models.ForeignKey(
        StaffProfile, on_delete=models.SET_NULL,
        null=True, related_name="weekly_assignments_created",
    )
    instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("enrollment", "topic", "week_start"),)
        ordering = ("-week_start", "id")

    def __str__(self):
        return f"{self.enrollment.student} - {self.topic.title} - {self.week_start}"


class TrainerTeachingReport(models.Model):
    REVIEW_CHOICES = [
        ("submitted", "Awaiting staff approval"),
        ("approved", "Approved"),
        ("rejected", "Needs correction"),
    ]
    STUDENT_CHOICES = [
        ("pending", "Awaiting student"),
        ("satisfied", "Satisfied"),
        ("doubt", "Has doubt"),
    ]
    assignment = models.ForeignKey(
        WeeklyTeachingAssignment, on_delete=models.PROTECT,
        related_name="teaching_reports",
    )
    submitted_by = models.ForeignKey(
        ClassroomTrainer, on_delete=models.PROTECT,
        related_name="submitted_teaching_reports",
    )
    taught_on = models.DateField(default=timezone.localdate)
    teaching_note = models.TextField()
    coverage_reason = models.TextField(blank=True)
    lab_completed = models.BooleanField(default=False)
    lab_evidence = models.TextField(blank=True)
    review_status = models.CharField(
        max_length=12, choices=REVIEW_CHOICES, default="submitted",
    )
    reviewed_by = models.ForeignKey(
        StaffProfile, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="reviewed_teaching_reports",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField(blank=True)
    student_response = models.CharField(
        max_length=12, choices=STUDENT_CHOICES, default="pending",
    )
    student_note = models.TextField(blank=True)
    student_responded_at = models.DateTimeField(null=True, blank=True)

    # Trainer confirms the student's completion/feedback.
    # This controls training progression independently of staff quality review.
    trainer_approved_at = models.DateTimeField(null=True, blank=True)

    closed_by = models.ForeignKey(
        StaffProfile, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="closed_teaching_reports",
    )
    closed_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-submitted_at", "-id")

    def __str__(self):
        return f"{self.assignment} - {self.submitted_by.name} - {self.review_status}"



class ClassroomTrainerAttendance(models.Model):
    trainer = models.ForeignKey(
        ClassroomTrainer, on_delete=models.PROTECT,
        related_name="classroom_attendance",
    )
    attendance_date = models.DateField()
    source_report = models.ForeignKey(
        TrainerTeachingReport, on_delete=models.PROTECT,
        related_name="attendance_credits",
    )
    approved_by = models.ForeignKey(
        StaffProfile, on_delete=models.SET_NULL,
        null=True, related_name="trainer_attendance_approved",
    )
    approved_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = (("trainer", "attendance_date"),)
        ordering = ("-attendance_date", "-id")

    def __str__(self):
        return f"{self.trainer.name} - {self.attendance_date}"
