from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import redirect, get_object_or_404
from django.utils.html import format_html
from django.contrib import messages

from .models import Attendance, BranchLocation
from django import forms
from django.db.models import Sum
from .models import (
    ExpenseCategory,
    DailyBranchExpense,
    DailyExpenseAuditLog,
)

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


# =====================================================# COURSE
# =====================================================
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


# =====================================================# COURSE MODULE
# =====================================================
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


# =====================================================# ENQUIRY
# =====================================================
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


# =====================================================# ENQUIRY ACTIVITY
# =====================================================
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


# =====================================================# ADMISSION
# =====================================================
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


# =====================================================# STUDENT
# =====================================================
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


# =====================================================# FEE PAYMENT
# =====================================================
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

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return tuple(
                field.name for field in self.model._meta.fields
                if field.name != "id"
            )
        return super().get_readonly_fields(request, obj)

    def has_delete_permission(self, request, obj=None):
        return False

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


# =====================================================# STAFF PROFILE
# =====================================================
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


# =====================================================# JOB POST
# =====================================================
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


# =====================================================# ATTENDANCE
# =====================================================
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

    # =====================================================# BRANCH PARTNERS
# =====================================================
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


# =====================================================# MONTHLY BRANCH CLOSING
# =====================================================
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

    # =====================================================# EXPENSE CATEGORY ADMIN
# =====================================================
@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(
    admin.ModelAdmin
):

    list_display = (
        "display_order",
        "name",
        "code",
        "is_active",
        "updated_at",
    )
    list_display_links = (
        "name",
    )

    list_editable = (
        "display_order",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "code",
    )

    ordering = (
        "display_order",
        "name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


# =====================================================# DAILY BRANCH EXPENSE ADMIN
# =====================================================
@admin.register(DailyBranchExpense)
class DailyBranchExpenseAdmin(
    admin.ModelAdmin
):

    list_display = (
        "expense_date",
        "branch",
        "category",
        "amount",
        "payment_mode",
        "remark",
        "is_cancelled",
        "created_by",
        "created_at",
    )

    list_filter = (
        "branch",
        "category",
        "payment_mode",
        "is_cancelled",
        "expense_date",
    )

    search_fields = (
        "remark",
        "short_notes",
        "created_by__username",
        "category__name",
    )

    date_hierarchy = "expense_date"

    ordering = (
        "-expense_date",
        "-created_at",
    )

    readonly_fields = (
        "created_by",
        "updated_by",
        "cancelled_by",
        "cancelled_at",
        "created_at",
        "updated_at",
    )

    def has_delete_permission(
        self,
        request,
        obj=None
    ):

        # Financial records must not be
        # permanently deleted.
        return False


# =====================================================# DAILY EXPENSE AUDIT LOG ADMIN
# =====================================================
@admin.register(DailyExpenseAuditLog)
class DailyExpenseAuditLogAdmin(
    admin.ModelAdmin
):

    list_display = (
        "expense",
        "action",
        "performed_by",
        "performed_at",
    )

    list_filter = (
        "action",
        "performed_at",
    )

    search_fields = (
        "expense__remark",
        "performed_by__username",
    )

    readonly_fields = (
        "expense",
        "action",
        "previous_data",
        "new_data",
        "performed_by",
        "performed_at",
    )

    ordering = (
        "-performed_at",
    )

    def has_add_permission(
        self,
        request
    ):
        return False

    def has_change_permission(
        self,
        request,
        obj=None
    ):
        return False

    def has_delete_permission(
        self,
        request,
        obj=None
    ):
        return False
