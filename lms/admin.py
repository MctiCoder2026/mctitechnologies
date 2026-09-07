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