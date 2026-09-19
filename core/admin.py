from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Attendance, BranchLocation
from django import forms
from django.db.models import Sum

from .models import (
    BranchPartner,
    MonthlyBranchClosing,
    MonthlyPartnerShare,
)

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

    # ============================================================
# BRANCH PARTNERS
# ============================================================

class BranchPartnerAdminForm(forms.ModelForm):

    class Meta:
        model = BranchPartner
        fields = "__all__"

    def clean(self):

        cleaned_data = super().clean()

        branch = cleaned_data.get("branch")
        percentage = (
            cleaned_data.get("share_percentage")
            or 0
        )
        is_active = cleaned_data.get(
            "is_active"
        )

        if percentage <= 0:
            self.add_error(
                "share_percentage",
                "Share percentage must be greater than zero."
            )

        if percentage > 100:
            self.add_error(
                "share_percentage",
                "Share percentage cannot exceed 100%."
            )

        if branch and is_active:

            existing = BranchPartner.objects.filter(
                branch=branch,
                is_active=True
            )

            if self.instance.pk:
                existing = existing.exclude(
                    pk=self.instance.pk
                )

            existing_total = (
                existing.aggregate(
                    total=Sum("share_percentage")
                )["total"]
                or 0
            )

            if existing_total + percentage > 100:

                self.add_error(
                    "share_percentage",
                    (
                        "Total active partner share for "
                        "this branch cannot exceed 100%."
                    )
                )

        return cleaned_data


@admin.register(BranchPartner)
class BranchPartnerAdmin(admin.ModelAdmin):

    form = BranchPartnerAdminForm

    list_display = (
        "branch",
        "partner_name",
        "share_percentage",
        "is_active",
        "updated_at",
    )

    list_filter = (
        "branch",
        "is_active",
    )

    search_fields = (
        "partner_name",
        "branch",
    )

    ordering = (
        "branch",
        "partner_name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


# ============================================================
# MONTHLY BRANCH CLOSING
# ============================================================

class MonthlyPartnerShareInline(
    admin.TabularInline
):

    model = MonthlyPartnerShare

    extra = 0

    can_delete = False

    readonly_fields = (
        "partner_name",
        "share_percentage",
        "share_amount",
        "is_paid",
        "paid_at",
        "remarks",
    )


@admin.register(MonthlyBranchClosing)
class MonthlyBranchClosingAdmin(
    admin.ModelAdmin
):

    list_display = (
        "branch",
        "closing_period",
        "admissions_count",
        "billing_amount",
        "collection_amount",
        "total_expenses_display",
        "cash_profit_display",
        "status",
        "created_by",
        "updated_at",
    )

    list_filter = (
        "status",
        "branch",
        "year",
        "month",
    )

    search_fields = (
        "branch",
        "remarks",
        "created_by__username",
    )

    readonly_fields = (
        "total_expenses_display",
        "pending_collection_display",
        "business_profit_display",
        "cash_profit_display",
        "distributable_profit_display",
        "cash_loss_display",
        "created_at",
        "updated_at",
        "submitted_at",
        "validated_at",
        "closed_at",
    )

    inlines = [
        MonthlyPartnerShareInline
    ]

    ordering = (
        "-year",
        "-month",
        "branch",
    )

    def closing_period(self, obj):
        return f"{obj.month:02d}/{obj.year}"

    closing_period.short_description = (
        "Month"
    )

    def total_expenses_display(
        self,
        obj
    ):
        return obj.total_expenses

    total_expenses_display.short_description = (
        "Total Expenses"
    )

    def pending_collection_display(
        self,
        obj
    ):
        return obj.pending_collection

    pending_collection_display.short_description = (
        "Pending Collection"
    )

    def business_profit_display(
        self,
        obj
    ):
        return obj.business_profit

    business_profit_display.short_description = (
        "Billing Profit/Loss"
    )

    def cash_profit_display(
        self,
        obj
    ):
        return obj.cash_profit

    cash_profit_display.short_description = (
        "Cash Profit/Loss"
    )

    def distributable_profit_display(
        self,
        obj
    ):
        return obj.distributable_profit

    distributable_profit_display.short_description = (
        "Distributable Profit"
    )

    def cash_loss_display(
        self,
        obj
    ):
        return obj.cash_loss

    cash_loss_display.short_description = (
        "Cash Loss"
    )

    def get_readonly_fields(
        self,
        request,
        obj=None
    ):

        readonly = list(
            super().get_readonly_fields(
                request,
                obj
            )
        )

        if obj and obj.status == "closed":

            readonly.extend(
                field.name
                for field in obj._meta.fields
                if field.name not in readonly
            )

        return tuple(readonly)

    def has_delete_permission(
        self,
        request,
        obj=None
    ):

        if obj and obj.status == "closed":
            return False

        return super().has_delete_permission(
            request,
            obj
        )


@admin.register(MonthlyPartnerShare)
class MonthlyPartnerShareAdmin(
    admin.ModelAdmin
):

    list_display = (
        "closing",
        "partner_name",
        "share_percentage",
        "share_amount",
        "is_paid",
        "paid_at",
    )

    list_filter = (
        "is_paid",
        "closing__branch",
        "closing__year",
        "closing__month",
    )

    search_fields = (
        "partner_name",
        "closing__branch",
    )

    readonly_fields = (
        "closing",
        "partner_name",
        "share_percentage",
        "share_amount",
    )