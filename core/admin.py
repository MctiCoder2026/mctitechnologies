from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import redirect, get_object_or_404
from django.utils.html import format_html
from django.contrib import messages

from .models import Attendance, BranchLocation

from .models import (
    Course,
    CourseModule,
    Enquiry,
    EnquiryActivity,
    Admission,
    Student,
    FeePayment,
    StaffProfile,
    JobPost,
    Attendance,
)


# ============================================================
# COURSE
# ============================================================

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "category",
        "duration",
        "fee",
        "is_active",
    )

    list_filter = (
        "category",
        "is_active",
    )

    search_fields = (
        "title",
        "category",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }


# ============================================================
# COURSE MODULE
# ============================================================

@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):

    list_display = (
        "course",
        "module_number",
        "title",
    )

    list_filter = (
        "course",
    )

    search_fields = (
        "title",
        "course__title",
    )

    ordering = (
        "course",
        "module_number",
    )


# ============================================================
# ENQUIRY
# ============================================================

@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "mobile",
        "course",
        "branch",
        "status",
        "followup_date",
        "created_at",
        "delete_duplicate_button",
    )

    list_filter = (
        "status",
        "branch",
        "course",
    )

    search_fields = (
        "name",
        "mobile",
        "email",
    )

    readonly_fields = (
        "created_at",
    )

    @admin.display(description="Delete")
    def delete_duplicate_button(self, obj):
        url = reverse(
            "admin:core_enquiry_delete_duplicate",
            args=[obj.pk]
        )
        return format_html(
            '<a href="{}" style="background:#ba2121;color:#fff;'
            'padding:6px 10px;border-radius:4px;'
            'text-decoration:none;font-weight:600;">'
            'Delete Dummy</a>',
            url
        )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:object_id>/delete-duplicate/",
                self.admin_site.admin_view(
                    self.delete_duplicate_view
                ),
                name="core_enquiry_delete_duplicate",
            ),
        ]
        return custom_urls + urls

    def delete_duplicate_view(self, request, object_id):
        if not request.user.is_superuser:
            messages.error(
                request,
                "Only Super Admin can delete enquiries."
            )
            return redirect("admin:core_enquiry_changelist")

        obj = get_object_or_404(Enquiry, pk=object_id)

        if request.method == "POST":
            enquiry_id = obj.pk
            enquiry_name = obj.name

            obj.delete()

            messages.success(
                request,
                f"Enquiry #{enquiry_id} - {enquiry_name} deleted successfully."
            )

            return redirect("admin:core_enquiry_changelist")

        context = {
            **self.admin_site.each_context(request),
            "title": "Delete Duplicate / Dummy Enquiry",
            "object": obj,
            "object_type": "Enquiry",
            "cancel_url": reverse(
                "admin:core_enquiry_changelist"
            ),
        }

        from django.template.response import TemplateResponse

        return TemplateResponse(
            request,
            "admin/delete_duplicate_confirm.html",
            context,
        )


# ============================================================
# ENQUIRY ACTIVITY
# ============================================================

@admin.register(EnquiryActivity)
class EnquiryActivityAdmin(admin.ModelAdmin):

    list_display = (
        "enquiry",
        "activity_type",
        "created_by",
        "created_at",
    )

    list_filter = (
        "activity_type",
    )

    search_fields = (
        "enquiry__name",
        "enquiry__mobile",
        "message",
    )

    readonly_fields = (
        "created_at",
    )


# ============================================================
# ADMISSION
# ============================================================

@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):

    list_display = (
        "admission_number",
        "student_name",
        "mobile",
        "course",
        "branch",
        "total_fee",
        "paid_fee",
        "balance_fee_display",
        "payment_status",
        "admission_date",
        "delete_duplicate_button",
    )

    list_filter = (
        "payment_status",
        "branch",
        "course",
        "admission_date",
    )

    search_fields = (
        "admission_number",
        "student_name",
        "mobile",
        "email",
    )

    readonly_fields = (
        "admission_number",
        "created_at",
        "balance_fee_display",
    )

    date_hierarchy = "admission_date"

    @admin.display(description="Balance Fee")
    def balance_fee_display(self, obj):
        return obj.balance_fee

    @admin.display(description="Delete")
    def delete_duplicate_button(self, obj):
        url = reverse(
            "admin:core_admission_delete_duplicate",
            args=[obj.pk]
        )
        return format_html(
            '<a href="{}" style="background:#ba2121;color:#fff;'
            'padding:6px 10px;border-radius:4px;'
            'text-decoration:none;font-weight:600;">'
            'Delete Dummy</a>',
            url
        )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:object_id>/delete-duplicate/",
                self.admin_site.admin_view(
                    self.delete_duplicate_view
                ),
                name="core_admission_delete_duplicate",
            ),
        ]
        return custom_urls + urls

    def delete_duplicate_view(self, request, object_id):
        if not request.user.is_superuser:
            messages.error(
                request,
                "Only Super Admin can delete admissions."
            )
            return redirect("admin:core_admission_changelist")

        obj = get_object_or_404(Admission, pk=object_id)

        linked_student = getattr(obj, "student", None)

        if request.method == "POST":
            admission_id = obj.pk
            admission_number = obj.admission_number

            obj.delete()

            messages.success(
                request,
                f"Admission {admission_number} (ID {admission_id}) deleted. "
                "Student, enrollments and payments were not renumbered."
            )

            return redirect("admin:core_admission_changelist")

        context = {
            **self.admin_site.each_context(request),
            "title": "Delete Duplicate / Dummy Admission",
            "object": obj,
            "object_type": "Admission",
            "linked_student": linked_student,
            "cancel_url": reverse(
                "admin:core_admission_changelist"
            ),
        }

        from django.template.response import TemplateResponse

        return TemplateResponse(
            request,
            "admin/delete_duplicate_confirm.html",
            context,
        )


# ============================================================
# STUDENT
# ============================================================

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    list_display = (
        "student_id",
        "name",
        "mobile",
        "course",
        "branch",
        "total_fee",
        "paid_fee",
        "balance_fee",
        "payment_status",
        "status",
        "trainer",
        "joining_date",
    )

    list_filter = (
        "status",
        "branch",
        "course",
        "joining_date",
    )

    search_fields = (
        "student_id",
        "name",
        "mobile",
        "email",
    )

    readonly_fields = (
        "student_id",
        "created_at",
        "total_fee",
        "paid_fee",
        "balance_fee",
        "payment_status",
    )

    date_hierarchy = "joining_date"

    @admin.display(description="Total Fee")
    def total_fee(self, obj):

        if obj.admission:
            return obj.admission.total_fee

        return 0

    @admin.display(description="Paid Fee")
    def paid_fee(self, obj):

        if obj.admission:
            return obj.admission.paid_fee

        return 0

    @admin.display(description="Balance Fee")
    def balance_fee(self, obj):

        if obj.admission:
            return obj.admission.balance_fee

        return 0

    @admin.display(description="Payment Status")
    def payment_status(self, obj):

        if obj.admission:
            return obj.admission.get_payment_status_display()

        return "-"


# ============================================================
# FEE PAYMENT
# ============================================================

@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):

    list_display = (
        "receipt_number",
        "student",
        "payment_date",
        "amount",
        "previous_paid",
        "balance_after_payment",
        "payment_mode",
        "transaction_id",
        "collected_by",
        "print_receipt",
    )

    list_filter = (
        "payment_mode",
        "payment_date",
    )

    search_fields = (
        "receipt_number",
        "student__student_id",
        "student__name",
        "student__mobile",
        "transaction_id",
    )

    readonly_fields = (
        "receipt_number",
        "previous_paid",
        "balance_after_payment",
        "created_at",
    )

    date_hierarchy = "payment_date"

    @admin.display(description="Print Receipt")
    def print_receipt(self, obj):

        url = reverse(
            "fee_receipt",
            args=[obj.receipt_number]
        )

        return format_html(
            '<a href="{}" target="_blank">'
            '🖨 Print Receipt'
            '</a>',
            url
        )


# ============================================================
# STAFF PROFILE
# ============================================================

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "branch",
        "department",
        "designation",
        "joining_date",
        "is_active",
    )

    list_filter = (
        "branch",
        "department",
        "is_active",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "designation",
    )


# ============================================================
# JOB POST
# ============================================================

@admin.register(JobPost)
class JobPostAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "company_name",
        "location",
        "posted_branch",
        "posted_by",
        "last_date",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "posted_branch",
        "eligible_courses",
        "last_date",
    )

    search_fields = (
        "title",
        "company_name",
        "location",
        "required_skills",
        "posted_branch",
        "posted_by__username",
    )

    filter_horizontal = (
        "eligible_courses",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


# ============================================================
# ATTENDANCE
# ============================================================

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "attendance_date",
        "status",
        "branch",
        "course",
        "marked_by",
        "updated_at",
    )

    list_filter = (
        "status",
        "branch",
        "course",
        "attendance_date",
    )

    search_fields = (
        "student__student_id",
        "student__name",
        "student__mobile",
        "remarks",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    date_hierarchy = "attendance_date"

    ordering = (
        "-attendance_date",
        "student__name",
    )
@admin.register(BranchLocation)
class BranchLocationAdmin(admin.ModelAdmin):
    list_display = (
        "branch_name",
        "latitude",
        "longitude",
        "radius_meters",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "branch_name",
    )
