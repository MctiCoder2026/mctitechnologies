from django.contrib import admin
from .models import Branch, LocalTestimonial, BranchGallery

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "phone", "is_head_office", "is_active")
    list_filter = ("is_head_office", "is_active")
    search_fields = ("name", "address", "phone")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(LocalTestimonial)
class LocalTestimonialAdmin(admin.ModelAdmin):
    list_display = ("student_name", "branch", "course_name", "rating", "is_active")
    list_filter = ("branch", "rating", "is_active")
    search_fields = ("student_name", "course_name", "review")

@admin.register(BranchGallery)
class BranchGalleryAdmin(admin.ModelAdmin):
    list_display = ("title", "branch", "display_order", "is_active")
    list_filter = ("branch", "is_active")
    search_fields = ("title", "alt_text")
