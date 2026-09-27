from django.contrib import admin

from .models import (
    LMSModule,
    LMSTopic,
    LMSTopicContent,
    QuizQuestion,
    StudentTopicProgress,
    QuizAttempt,
    
)


# =========================================================
# LMS MODULE
# =========================================================

@admin.register(LMSModule)
class LMSModuleAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "course",
        "order",
        "title",
        "is_active",
    )

    list_filter = (
        "course",
        "is_active",
    )

    search_fields = (
        "title",
        "course__title",
    )

    ordering = (
        "course",
        "order",
    )

    list_editable = (
        "order",
        "is_active",
    )


# =========================================================
# QUIZ QUESTION INLINE
# =========================================================
class LMSTopicContentInline(admin.TabularInline):

    model = LMSTopicContent
    extra = 0

    fields = (
        "language",
        "description",
        "video_url",
        "notes_file",
        "practice_file",
        "is_active",
    )
class QuizQuestionInline(admin.TabularInline):

    model = QuizQuestion
    extra = 0

    fields = (
        "language",
        "order",
        "question",
        "option_a",
        "option_b",
        "option_c",
        "option_d",
        "correct_answer",
        "is_active",
    )

    ordering = (
        "language",
        "order",
    )


# =========================================================
# LMS TOPIC
# =========================================================

@admin.register(LMSTopic)
class LMSTopicAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "module",
        "order",
        "title",
        "has_video",
        "has_notes",
        "has_practice",
        "is_active",
    )

    list_filter = (
        "module__course",
        "module",
        "is_active",
    )

    search_fields = (
        "title",
        "module__title",
        "module__course__title",
    )

    ordering = (
        "module__course",
        "module__order",
        "order",
    )

    list_editable = (
        "order",
        "is_active",
    )

    inlines = [
    LMSTopicContentInline,
    QuizQuestionInline,
]

    fieldsets = (

        (
            "Topic Information",
            {
                "fields": (
                    "module",
                    "title",
                    "description",
                    "order",
                    "is_active",
                )
            }
        ),

        (
            "Learning Resources",
            {
                "fields": (
                    "video_url",
                    "notes_file",
                    "practice_file",
                )
            }
        ),

    )

    def has_video(self, obj):
        return bool(obj.video_url)

    has_video.boolean = True
    has_video.short_description = "Video"

    def has_notes(self, obj):
        return bool(obj.notes_file)

    has_notes.boolean = True
    has_notes.short_description = "Notes"

    def has_practice(self, obj):
        return bool(obj.practice_file)

    has_practice.boolean = True
    has_practice.short_description = "Practice"


# =========================================================
# QUIZ QUESTION
# =========================================================

@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "topic",
        "language",
        "order",
        "short_question",
        "correct_answer",
        "is_active",
    )

    list_filter = (
        "language",
        "topic__module__course",
        "topic__module",
        "topic",
        "is_active",
    )

    search_fields = (
        "question",
        "topic__title",
        "topic__module__title",
        "topic__module__course__title",
    )

    ordering = (
        "topic__module__course",
        "topic__module__order",
        "topic__order",
        "language",
        "order",
    )

    list_editable = (
        "language",
        "order",
        "correct_answer",
        "is_active",
    )

    fieldsets = (

        (
            "Question",
            {
                "fields": (
                    "topic",
                    "language",
                    "question",
                    "order",
                    "is_active",
                )
            }
        ),

        (
            "Options",
            {
                "fields": (
                    "option_a",
                    "option_b",
                    "option_c",
                    "option_d",
                )
            }
        ),

        (
            "Correct Answer",
            {
                "fields": (
                    "correct_answer",
                )
            }
        ),

    )

    def short_question(self, obj):

        if len(obj.question) > 70:
            return obj.question[:70] + "..."

        return obj.question

    short_question.short_description = "Question"


# =========================================================
# STUDENT TOPIC PROGRESS
# =========================================================

@admin.register(StudentTopicProgress)
class StudentTopicProgressAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "topic",
        "is_unlocked",
        "is_completed",
        "best_score",
        "attempts",
        "last_attempt_at",
    )

    list_filter = (
        "is_unlocked",
        "is_completed",
        "topic__module__course",
        "topic__module",
    )

    search_fields = (
        "student__name",
        "student__student_id",
        "topic__title",
        "topic__module__title",
    )

    readonly_fields = (
        "last_attempt_at",
        "completed_at",
    )

    ordering = (
        "-last_attempt_at",
    )


# =========================================================
# QUIZ ATTEMPT
# =========================================================

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "topic",
        "score",
        "total_questions",
        "passed",
        "attempted_at",
    )

    list_filter = (
        "passed",
        "topic__module__course",
        "topic__module",
        "attempted_at",
    )

    search_fields = (
        "student__name",
        "student__student_id",
        "topic__title",
    )

    readonly_fields = (
        "student",
        "topic",
        "score",
        "total_questions",
        "passed",
        "attempted_at",
    )

    ordering = (
        "-attempted_at",
    )

# Classroom teaching standard (separate from LMS quiz progress)
from core.models import StaffProfile
from django import forms
from django.utils import timezone
from .models import (
    TrainingChecklistItem,
    TrainingDeliveryPlan,
    TrainingDeliverySession,
    TrainingDeliveryEnrollment,
    LMSTopicDoubt,
    WeeklyTeachingAssignment,
)


class TrainingChecklistForm(forms.ModelForm):
    class Meta:
        model = TrainingChecklistItem
        fields = "__all__"

    def clean(self):
        data = super().clean()
        topic = data.get("lms_topic")
        course = data.get("course")
        if topic and course and topic.module.course_id != course.pk:
            raise forms.ValidationError("Linked LMS topic belongs to another course.")
        if data.get("is_published"):
            for field in (
                "learning_outcome", "trainer_steps",
                "student_practice", "completion_check",
            ):
                if not (data.get(field) or "").strip():
                    self.add_error(field, "Required before publishing.")
        if self.instance.pk and (
            TrainingDeliverySession.objects.filter(topic=self.instance).exists()
            or WeeklyTeachingAssignment.objects.filter(topic=self.instance).exists()
        ):
            for field in (
                "course", "lms_topic", "module_title",
                "module_order", "title", "order",
            ):
                if field in self.changed_data:
                    self.add_error(field, "Topic identity is fixed after teaching starts.")
            guidance = (
                "learning_outcome", "trainer_steps",
                "student_practice", "completion_check",
            )
            if any(field in self.changed_data for field in guidance):
                if (data.get("version") or 0) <= self.instance.version:
                    self.add_error(
                        "version", "Increase version when changing a taught topic's standard."
                    )
        return data


@admin.register(TrainingChecklistItem)
class TrainingChecklistItemAdmin(admin.ModelAdmin):
    form = TrainingChecklistForm
    list_display = (
        "course", "module_order", "module_title", "order",
        "title", "version", "is_published", "approved_by",
    )
    list_filter = ("course", "is_published", "version")
    search_fields = ("course__title", "module_title", "title")
    ordering = ("course", "module_order", "order", "id")
    readonly_fields = ("approved_by", "approved_at", "created_at", "updated_at")
    fields = (
        "course", "lms_topic", "module_title", "module_order",
        "title", "order", "learning_outcome", "trainer_steps",
        "student_practice", "completion_check", "expected_sessions",
        "version", "is_published", "approved_by", "approved_at",
        "created_at", "updated_at",
    )

    def save_model(self, request, obj, form, change):
        if obj.is_published and (not change or "is_published" in form.changed_data):
            obj.approved_by = StaffProfile.objects.filter(
                user=request.user, is_active=True
            ).first()
            obj.approved_at = timezone.now()
        super().save_model(request, obj, form, change)


class TrainingDeliveryPlanForm(forms.ModelForm):
    class Meta:
        model = TrainingDeliveryPlan
        fields = "__all__"

    def clean(self):
        data = super().clean()
        enrollment = data.get("enrollment")
        course = data.get("course")
        start = data.get("start_item")
        if enrollment and course:
            valid = (
                enrollment.course_id == course.id and not enrollment.course.is_package
            ) or (
                enrollment.course.is_package
                and enrollment.course.included_courses.filter(pk=course.id).exists()
            )
            if not valid:
                raise forms.ValidationError("Course is not in this enrollment.")
        if start and course and start.course_id != course.id:
            self.add_error("start_item", "Starting topic must belong to the selected course.")
        if data.get("revised_completion_date") and not (
            data.get("revision_reason") or ""
        ).strip():
            self.add_error("revision_reason", "Explain why the target date changed.")
        return data


@admin.register(TrainingDeliveryPlan)
class TrainingDeliveryPlanAdmin(admin.ModelAdmin):
    form = TrainingDeliveryPlanForm
    change_list_template = "admin/lms/trainingdeliveryplan/change_list.html"
    list_display = (
        "enrollment", "course", "assigned_trainer",
        "target_completion_date", "revised_completion_date",
    )
    list_filter = ("course",)
    search_fields = ("enrollment__student__name", "course__title")
    readonly_fields = ("set_by", "created_at", "updated_at")

    def save_model(self, request, obj, form, change):
        obj.set_by = StaffProfile.objects.filter(
            user=request.user, is_active=True
        ).first()
        super().save_model(request, obj, form, change)


class DeliveryEnrollmentInline(admin.TabularInline):
    model = TrainingDeliveryEnrollment
    extra = 0
    can_delete = False
    readonly_fields = ("enrollment",)

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(TrainingDeliverySession)
class TrainingDeliverySessionAdmin(admin.ModelAdmin):
    list_display = (
        "session_date", "topic", "taught_by",
        "assigned_trainer", "branch", "session_type",
    )
    list_filter = ("branch", "session_type", "session_date", "topic__course")
    search_fields = ("topic__title", "taught_by__user__username")
    readonly_fields = (
        "topic", "session_date", "taught_by", "assigned_trainer",
        "branch", "session_type", "notes", "standard_snapshot", "created_at",
    )
    inlines = (DeliveryEnrollmentInline,)

    def has_add_permission(self, request):
        return False


@admin.register(LMSTopicDoubt)
class LMSTopicDoubtAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "topic", "status", "opened_at", "resolved_by")
    list_filter = ("status", "topic__course")
    search_fields = ("enrollment__student__name", "topic__title", "question")
    readonly_fields = (
        "enrollment", "topic", "question", "status", "opened_at",
        "resolved_at", "resolved_by", "resolution_session", "trainer_note",
    )

    def has_add_permission(self, request):
        return False
