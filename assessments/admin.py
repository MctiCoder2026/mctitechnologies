from django.contrib import admin

from .models import (
    HiringJobRole,
    HiringSalaryMatrix,
    HiringCandidate,
    HiringApplication,
    HiringEvaluation,
)


@admin.register(HiringJobRole)
class HiringJobRoleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "technical_weight",
        "practical_weight",
        "communication_weight",
        "is_active",
    )
    list_filter = ("is_active",)
    search_fields = ("name", "slug")


@admin.register(HiringSalaryMatrix)
class HiringSalaryMatrixAdmin(admin.ModelAdmin):
    list_display = (
        "job_role",
        "employment_type",
        "performance_band",
        "min_salary",
        "max_salary",
        "is_active",
    )
    list_filter = (
        "employment_type",
        "performance_band",
        "is_active",
        "job_role",
    )
    search_fields = ("job_role__name",)
    list_editable = (
        "min_salary",
        "max_salary",
        "is_active",
    )


@admin.register(HiringCandidate)
class HiringCandidateAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "mobile",
        "email",
        "qualification",
        "city",
        "created_at",
    )
    search_fields = (
        "full_name",
        "mobile",
        "email",
    )


@admin.register(HiringApplication)
class HiringApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "candidate",
        "job_role",
        "employment_type",
        "status",
        "created_at",
    )
    list_filter = (
        "job_role",
        "employment_type",
        "status",
    )
    search_fields = (
        "candidate__full_name",
        "candidate__mobile",
        "candidate__email",
    )


@admin.register(HiringEvaluation)
class HiringEvaluationAdmin(admin.ModelAdmin):
    list_display = (
        "application",
        "technical_score",
        "practical_score",
        "communication_score",
        "final_score",
        "performance_band",
        "suggested_salary_min",
        "suggested_salary_max",
        "approved_salary",
    )
    list_filter = ("performance_band",)
    readonly_fields = (
        "technical_score",
        "final_score",
        "performance_band",
        "suggested_salary_min",
        "suggested_salary_max",
    )
