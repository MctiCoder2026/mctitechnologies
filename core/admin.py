
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    Course,
    CourseModule,
    Enquiry,
    EnquiryActivity,
    Admission,
    Student,
    FeePayment,
    StaffProfile,
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
