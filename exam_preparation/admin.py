from django.contrib import admin
from .models import SSCStudent, SSCResource, SSCDownload


@admin.register(SSCStudent)
class SSCStudentAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "mobile",
        "school_name",
        "medium",
        "city",
        "preferred_branch",
        "created_at",
    )
    list_filter = ("medium", "preferred_branch", "created_at")
    search_fields = ("full_name", "mobile", "school_name", "city")


@admin.register(SSCResource)
class SSCResourceAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "subject",
        "year",
        "medium",
        "resource_type",
        "source_name",
        "is_official_source",
        "is_active",
    )
    list_filter = (
        "subject",
        "year",
        "medium",
        "resource_type",
        "is_official_source",
        "is_active",
    )
    search_fields = ("title", "source_name")


@admin.register(SSCDownload)
class SSCDownloadAdmin(admin.ModelAdmin):
    list_display = ("student", "resource", "downloaded_at")
    list_filter = ("downloaded_at",)
    search_fields = (
        "student__full_name",
        "student__mobile",
        "resource__title",
    )


