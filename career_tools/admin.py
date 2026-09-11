from django.contrib import admin

from .models import (
    CareerProfile,
    Resume,
    ResumeEducation,
    ResumeExperience,
    ResumeProject,
    ResumeCertification,
    AptitudeQuestion,
    AptitudeAttempt,
    AptitudeAnswer,
)


class ResumeEducationInline(admin.TabularInline):
    model = ResumeEducation
    extra = 0


class ResumeExperienceInline(admin.TabularInline):
    model = ResumeExperience
    extra = 0


class ResumeProjectInline(admin.TabularInline):
    model = ResumeProject
    extra = 0


class ResumeCertificationInline(admin.TabularInline):
    model = ResumeCertification
    extra = 0


@admin.register(CareerProfile)
class CareerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "mobile",
        "student",
        "career_interest",
        "preferred_job_role",
        "is_guest",
        "created_at",
    )

    search_fields = (
        "full_name",
        "mobile",
        "email",
        "student__student_id",
    )

    list_filter = (
        "is_guest",
        "consent_given",
        "created_at",
    )


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = (
        "profile",
        "title",
        "template_name",
        "is_default",
        "updated_at",
    )

    search_fields = (
        "profile__full_name",
        "profile__mobile",
    )

    inlines = [
        ResumeEducationInline,
        ResumeExperienceInline,
        ResumeProjectInline,
        ResumeCertificationInline,
    ]


@admin.register(AptitudeQuestion)
class AptitudeQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "category",
        "question",
        "correct_option",
        "difficulty",
        "order",
        "is_active",
    )

    list_filter = (
        "category",
        "difficulty",
        "is_active",
    )

    search_fields = (
        "question",
        "option_a",
        "option_b",
        "option_c",
        "option_d",
    )

    list_editable = (
        "difficulty",
        "order",
        "is_active",
    )

    ordering = (
        "category",
        "order",
        "id",
    )


@admin.register(AptitudeAttempt)
class AptitudeAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "profile",
        "total_questions",
        "correct_answers",
        "score_percentage",
        "status",
        "started_at",
        "completed_at",
    )

    list_filter = (
        "status",
        "started_at",
    )

    search_fields = (
        "profile__full_name",
        "profile__mobile",
    )

    readonly_fields = (
        "started_at",
        "completed_at",
    )


@admin.register(AptitudeAnswer)
class AptitudeAnswerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "attempt",
        "question",
        "selected_option",
        "is_correct",
        "answered_at",
    )

    list_filter = (
        "is_correct",
        "answered_at",
    )

    search_fields = (
        "attempt__profile__full_name",
        "question__question",
    )

    readonly_fields = (
        "answered_at",
    )