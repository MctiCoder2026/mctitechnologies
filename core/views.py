from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout as auth_logout
from django.contrib import messages
from .models import JobPost, StaffProfile
from .forms import JobPostForm
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import datetime, timedelta

from .forms import (
    EnquiryForm,
    EnquiryStatusForm,
    EnquiryFollowupForm,
    EnquiryAssignmentForm,
    AdmissionForm,
    AdmissionEditForm,
    FeePaymentForm,
    BusinessLeadForm,
    BusinessLeadAssignmentForm,
    BusinessLeadUpdateForm,
)

from .models import (
    Course,
    Enquiry,
    EnquiryActivity,
    Admission,
    Student,
    FeePayment,
    StaffProfile,
    Attendance,
    BusinessLead,
    BusinessLeadActivity,
)





# ============================================================
# BUSINESS LEAD DETAIL
# ============================================================

@login_required
def business_lead_detail(request, lead_id):

    lead = get_object_or_404(
        BusinessLead.objects.select_related("assigned_to"),
        id=lead_id
    )

    admin_access = is_admin_user(request.user)
    user_branch = get_user_branch(request.user)

    # HO/Admin can see every lead.
    # Branch staff can see only leads assigned to their branch.
    if not admin_access:

        if (
            not user_branch
            or not lead.assigned_branch
            or lead.assigned_branch.strip().lower()
            != user_branch.strip().lower()
        ):
            return redirect("business_lead_list")

    assignment_form = None
    update_form = BusinessLeadUpdateForm(
        instance=lead
    )

    if request.method == "POST":

        form_action = request.POST.get(
            "form_action",
            ""
        ).strip()

        # ----------------------------------------------------
        # HO ASSIGNMENT / REASSIGNMENT
        # ----------------------------------------------------
        if form_action == "assignment":

            if not admin_access:
                messages.error(
                    request,
                    "Only HO/Admin can assign or reassign business leads."
                )
                return redirect(
                    "business_lead_detail",
                    lead_id=lead.id
                )

            assignment_form = BusinessLeadAssignmentForm(
                request.POST,
                instance=lead
            )

            if assignment_form.is_valid():

                old_branch = (
                    lead.assigned_branch
                    or ""
                ).strip()

                old_staff = lead.assigned_to

                updated_lead = assignment_form.save()

                branch_display = (
                    updated_lead.assigned_branch
                    or "Unassigned"
                ).replace("_", " ").title()

                if updated_lead.assigned_to:
                    staff_display = (
                        updated_lead.assigned_to.get_full_name()
                        or updated_lead.assigned_to.username
                    )
                else:
                    staff_display = "Unassigned"

                changed = (
                    old_branch.lower()
                    != (
                        updated_lead.assigned_branch
                        or ""
                    ).strip().lower()
                    or old_staff != updated_lead.assigned_to
                )

                if changed:

                    BusinessLeadActivity.objects.create(
                        lead=updated_lead,
                        activity_type="assigned",
                        message=(
                            f"Lead assigned to {branch_display}"
                            f" / {staff_display}."
                        ),
                        created_by=request.user,
                    )

                    messages.success(
                        request,
                        "Business lead assignment updated successfully."
                    )

                else:

                    messages.info(
                        request,
                        "No assignment changes were made."
                    )

                return redirect(
                    "business_lead_detail",
                    lead_id=updated_lead.id
                )

        # ----------------------------------------------------
        # STATUS / FOLLOW-UP / VALUE UPDATE
        # ----------------------------------------------------
        elif form_action == "lead_update":

            update_form = BusinessLeadUpdateForm(
                request.POST,
                instance=lead
            )

            if update_form.is_valid():

                old_status = lead.status
                old_followup_date = lead.followup_date
                old_followup_notes = lead.followup_notes or ""
                old_estimated_value = lead.estimated_value
                old_final_value = lead.final_value

                updated_lead = update_form.save()

                activity_messages = []

                if old_status != updated_lead.status:
                    activity_messages.append(
                        f"Status changed from "
                        f"{dict(BusinessLead.STATUS_CHOICES).get(old_status, old_status)} "
                        f"to {updated_lead.get_status_display()}."
                    )

                if old_followup_date != updated_lead.followup_date:
                    activity_messages.append(
                        f"Follow-up date updated to "
                        f"{updated_lead.followup_date or 'Not Set'}."
                    )

                if old_followup_notes != (updated_lead.followup_notes or ""):
                    activity_messages.append(
                        "Follow-up notes updated."
                    )

                if old_estimated_value != updated_lead.estimated_value:
                    activity_messages.append(
                        f"Estimated value updated to "
                        f"₹{updated_lead.estimated_value or 0}."
                    )

                if old_final_value != updated_lead.final_value:
                    activity_messages.append(
                        f"Final value updated to "
                        f"₹{updated_lead.final_value or 0}."
                    )

                if activity_messages:

                    if updated_lead.status == "converted":
                        activity_type = "converted"
                    elif updated_lead.status == "proposal":
                        activity_type = "proposal"
                    elif (
                        old_followup_date != updated_lead.followup_date
                        or old_followup_notes
                        != (updated_lead.followup_notes or "")
                    ):
                        activity_type = "followup"
                    elif old_status != updated_lead.status:
                        activity_type = "status"
                    else:
                        activity_type = "note"

                    BusinessLeadActivity.objects.create(
                        lead=updated_lead,
                        activity_type=activity_type,
                        message=" ".join(activity_messages),
                        created_by=request.user,
                    )

                    messages.success(
                        request,
                        "Business lead updated successfully."
                    )

                else:

                    messages.info(
                        request,
                        "No lead changes were made."
                    )

                return redirect(
                    "business_lead_detail",
                    lead_id=updated_lead.id
                )

        else:

            messages.error(
                request,
                "Invalid business lead form submission."
            )

    if admin_access and assignment_form is None:
        assignment_form = BusinessLeadAssignmentForm(
            instance=lead
        )

    activities = (
        lead.activities
        .select_related("created_by")
        .all()
    )

    return render(
        request,
        "core/business_lead_detail.html",
        {
            "lead": lead,
            "activities": activities,
            "is_admin": admin_access,
            "assignment_form": assignment_form,
            "update_form": update_form,
        }
    )


# ============================================================
# PUBLIC BUSINESS CONTACT / SERVICE REQUIREMENT
# ============================================================

def business_contact(request):

    service = request.GET.get("service", "").strip().lower()

    valid_services = {
        "ai",
        "saas",
        "it",
        "corporate_training",
    }

    initial = {}

    if service in valid_services:
        initial["service"] = service

    if request.method == "POST":

        form = BusinessLeadForm(
            request.POST
        )

        if form.is_valid():

            lead = form.save()

            BusinessLeadActivity.objects.create(
                lead=lead,
                activity_type="created",
                message="Business enquiry submitted from website.",
                created_by=None,
            )

            return render(
                request,
                "core/business_contact_success.html",
                {
                    "lead": lead,
                }
            )

    else:

        form = BusinessLeadForm(
            initial=initial
        )

    return render(
        request,
        "core/business_contact.html",
        {
            "form": form,
            "selected_service": service,
        }
    )


# ============================================================
# ACCESS CONTROL
# ============================================================

def is_admin_user(user):

    if not user.is_authenticated:
        return False

    # Django superuser = full admin
    if user.is_superuser:
        return True

    # HO user must also be a Django staff user
    if not user.is_staff:
        return False

    try:
        profile = user.staff_profile
    except StaffProfile.DoesNotExist:
        return False

    if not profile.is_active:
        return False

    # Head Office staff gets HO/Admin level access
    return profile.branch == "head_office"


def get_user_branch(user):

    if not user.is_authenticated:
        return None

    if user.is_superuser:
        return None

    if not user.is_staff:
        return None

    try:
        profile = user.staff_profile
    except StaffProfile.DoesNotExist:
        return None

    if not profile.is_active:
        return None

    return profile.branch


def user_can_access_enquiry(user, enquiry):

    if is_admin_user(user):
        return True

    if not user.is_authenticated:
        return False

    user_branch = get_user_branch(user)

    if not user_branch:
        return False

    return (
        (enquiry.branch or "").strip().lower()
        == user_branch.strip().lower()
    )


def user_can_access_student(user, student):

    if is_admin_user(user):
        return True

    if not user.is_authenticated:
        return False

    if student.user_id == user.id:
        return True

    user_branch = get_user_branch(user)

    if not user_branch:
        return False

    return (
        (student.branch or "").strip().lower()
        == user_branch.strip().lower()
    )


def user_can_access_admission(user, admission):

    if is_admin_user(user):
        return True

    if not user.is_authenticated:
        return False

    if admission.user_id == user.id:
        return True

    user_branch = get_user_branch(user)

    if not user_branch:
        return False

    return (
        (admission.branch or "").strip().lower()
        == user_branch.strip().lower()
    )


# ============================================================
# PLACEMENT MANAGEMENT ACCESS
# ============================================================

def staff_or_admin(user):

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if not user.is_staff:
        return False

    return StaffProfile.objects.filter(
        user=user,
        is_active=True
    ).exists()


# ============================================================
# STUDENT PROFILE HELPER
# ============================================================

def get_logged_in_student(user):

    if not user.is_authenticated:
        return None

    admission = (
        Admission.objects
        .select_related(
            "student",
            "course",
            "enquiry",
        )
        .filter(user=user)
        .first()
    )

    if not admission:
        return None

    return getattr(
        admission,
        "student",
        None
    )


# ============================================================
# MANAGEMENT DASHBOARD
# ============================================================

@login_required
def management_dashboard(request):

    if not is_admin_user(request.user):
        return redirect(
            "branch_dashboard"
        )
    best_branch = None

    branch_summary = []

    branches = [
        ("kharghar", "Kharghar"),
        ("panvel", "Panvel"),
        ("koperkhairane", "Koperkhairane"),
        ("kamothe", "Kamothe"),
        ("ghansoli", "Ghansoli"),
        ("nerul", "Nerul"),
        ("head_office", "Head Office"),
        
    ]

    for branch_value, branch_name in branches:

        admissions = Admission.objects.filter(
            branch__iexact=branch_value
        ).count()

        collection = (
            FeePayment.objects
            .filter(
                student__branch__iexact=branch_value
            )
            .aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        branch_summary.append(
            {
                "branch": branch_name,
                "admissions": admissions,
                "collection": collection,
            }
        )

    active_branches = [
        item
        for item in branch_summary
        if (
            item["admissions"] > 0
            or item["collection"] > 0
        )
    ]

    if active_branches:

        best_branch = max(
            active_branches,
            key=lambda x: (
                x["admissions"],
                x["collection"]
            )
        )
    
    total_enquiries = Enquiry.objects.count()

    new_enquiries = Enquiry.objects.filter(
        status="new"
    ).count()

    converted_enquiries = Enquiry.objects.filter(
        status="converted"
    ).count()

    total_admissions = Admission.objects.count()

    total_students = Student.objects.filter(
        status="active"
    ).count()

    total_collected = (
        FeePayment.objects.aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    context = {
        "total_enquiries": total_enquiries,
        "new_enquiries": new_enquiries,
        "converted_enquiries": converted_enquiries,
        "total_admissions": total_admissions,
        "total_students": total_students,
        "total_collected": total_collected,
        "best_branch": best_branch,
    }

    return render(
        request,
        "core/management_dashboard.html",
        context
    )

@login_required
def branch_dashboard(request):

    today = timezone.localdate()

    date_filter = request.GET.get(
        "date_filter",
        "all"
    ).strip()

    custom_start = request.GET.get(
        "start_date",
        ""
    ).strip()

    custom_end = request.GET.get(
        "end_date",
        ""
    ).strip()

    start_date = None
    end_date = None

    # --------------------------------------------------------
    # DATE FILTER
    # --------------------------------------------------------

    if date_filter == "today":

        start_date = today
        end_date = today

    elif date_filter == "this_month":

        start_date = today.replace(
            day=1
        )

        end_date = today

    elif date_filter == "last_month":

        first_day_this_month = today.replace(
            day=1
        )

        last_day_last_month = (
            first_day_this_month
            - timedelta(days=1)
        )

        start_date = last_day_last_month.replace(
            day=1
        )

        end_date = last_day_last_month

    elif date_filter == "custom":

        if custom_start and custom_end:

            start_date = datetime.strptime(
                custom_start,
                "%Y-%m-%d"
            ).date()

            end_date = datetime.strptime(
                custom_end,
                "%Y-%m-%d"
            ).date()

    branches = [
        ("kharghar", "Kharghar"),
        ("panvel", "Panvel"),
        ("koperkhairane", "Koperkhairane"),
        ("kamothe", "Kamothe"),
        ("ghansoli", "Ghansoli"),
        ("nerul", "Nerul"),
        ("head_office", "Head Office"),
    ]

    # --------------------------------------------------------
    # BRANCH ACCESS
    # --------------------------------------------------------

    user_branch = get_user_branch(
        request.user
    )

    if not is_admin_user(request.user):

        if not user_branch:
            auth_logout(request)
            return redirect(
                "staff_login"
            )

        branches = [
            item
            for item in branches
            if item[0] == user_branch
        ]

    branch_data = []

    # --------------------------------------------------------
    # OVERALL TOTALS
    # --------------------------------------------------------

    overall_enquiries = 0
    overall_converted = 0
    overall_admissions = 0
    overall_collection = 0
    overall_active_students = 0

    # --------------------------------------------------------
    # BRANCH PERFORMANCE
    # --------------------------------------------------------

    for branch_value, branch_name in branches:

        enquiries = Enquiry.objects.filter(
            branch__iexact=branch_value
        )

        if start_date and end_date:

            enquiries = enquiries.filter(
                created_at__date__range=[
                    start_date,
                    end_date
                ]
            )

        total_enquiries = enquiries.count()

        converted = enquiries.filter(
            status="converted"
        ).count()

        admissions = Admission.objects.filter(
            branch__iexact=branch_value
        )

        if start_date and end_date:

            admissions = admissions.filter(
                admission_date__range=[
                    start_date,
                    end_date
                ]
            )

        total_admissions = admissions.count()

        active_students = Student.objects.filter(
            branch__iexact=branch_value,
            status="active"
        ).count()

        payments = FeePayment.objects.filter(
            student__branch__iexact=branch_value
        )

        if start_date and end_date:

            payments = payments.filter(
                payment_date__range=[
                    start_date,
                    end_date
                ]
            )

        total_collection = (
            payments.aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        if total_enquiries > 0:

            conversion_rate = round(
                (
                    converted
                    / total_enquiries
                ) * 100,
                1
            )

        else:

            conversion_rate = 0

        overall_enquiries += total_enquiries
        overall_converted += converted
        overall_admissions += total_admissions
        overall_collection += total_collection
        overall_active_students += active_students

        branch_data.append(
            {
                "branch": branch_name,
                "total_enquiries": total_enquiries,
                "converted": converted,
                "admissions": total_admissions,
                "collection": total_collection,
                "conversion_rate": conversion_rate,
                "active_students": active_students,
            }
        )

    # --------------------------------------------------------
    # BUSINESS LEADS FOR BRANCH DASHBOARD
    # --------------------------------------------------------

    business_leads = BusinessLead.objects.all()

    if not is_admin_user(request.user):
        business_leads = business_leads.filter(
            assigned_branch__iexact=user_branch
        )

    total_business_leads = business_leads.count()

    new_business_leads = business_leads.filter(
        status="new"
    ).count()

    followup_business_leads = business_leads.filter(
        status="followup"
    ).count()

    proposal_business_leads = business_leads.filter(
        status="proposal"
    ).count()

    converted_business_leads = business_leads.filter(
        status="converted"
    ).count()


    # --------------------------------------------------------
    # BEST & LOW PERFORMING BRANCH
    # --------------------------------------------------------

    active_branch_data = [
        item
        for item in branch_data
        if (
            item["total_enquiries"] > 0
            or item["admissions"] > 0
            or item["collection"] > 0
        )
    ]

    if active_branch_data:

        best_branch = max(
            active_branch_data,
            key=lambda x: (
                x["admissions"],
                x["collection"],
                x["conversion_rate"]
            )
        )

        attention_branch = min(
            active_branch_data,
            key=lambda x: (
                x["admissions"],
                x["collection"],
                x["conversion_rate"]
            )
        )

    else:

        best_branch = None
        attention_branch = None

    # --------------------------------------------------------
    # OVERALL CONVERSION %
    # --------------------------------------------------------

    if overall_enquiries > 0:

        overall_conversion_rate = round(
            (
                overall_converted
                / overall_enquiries
            ) * 100,
            1
        )

    else:

        overall_conversion_rate = 0

    return render(
        request,
        "core/branch_dashboard.html",
        {
            "branch_data": branch_data,
            "overall_enquiries": overall_enquiries,
            "overall_converted": overall_converted,
            "overall_admissions": overall_admissions,
            "overall_collection": overall_collection,
            "overall_active_students": overall_active_students,
            "overall_conversion_rate": overall_conversion_rate,

            "total_business_leads": total_business_leads,
            "new_business_leads": new_business_leads,
            "followup_business_leads": followup_business_leads,
            "proposal_business_leads": proposal_business_leads,
            "converted_business_leads": converted_business_leads,

            "best_branch": best_branch,
            "attention_branch": attention_branch,
            "date_filter": date_filter,
            "start_date": start_date,
            "end_date": end_date,
            "custom_start": custom_start,
            "custom_end": custom_end,
            "is_admin": is_admin_user(
                request.user
            ),
        }
    )


# ============================================================
# REPORTS DASHBOARD
# ============================================================

@login_required
def reports_dashboard(request):

    branches = [
        ("", "All Branches"),
        ("kharghar", "Kharghar"),
        ("panvel", "Panvel"),
        ("koperkhairane", "Koperkhairane"),
        ("kamothe", "Kamothe"),
        ("ghansoli", "Ghansoli"),
        ("nerul", "Nerul"),
        ("head_office", "Head Office"),
    ]

    today = timezone.localdate()

    branch_filter = request.GET.get(
        "branch",
        ""
    ).strip()


    if not request.user.is_superuser:

        user_branch = get_user_branch(
            request.user
        )

        if not user_branch:
            auth_logout(request)
            return redirect(
                "staff_login"
            )

        branch_filter = user_branch

        branches = [
            item
            for item in branches
            if item[0] == user_branch
        ]

    date_filter = request.GET.get(
        "date_filter",
        "all"
    ).strip()

    custom_start = request.GET.get(
        "start_date",
        ""
    ).strip()

    custom_end = request.GET.get(
        "end_date",
        ""
    ).strip()

    start_date = None
    end_date = None

    # --------------------------------------------------------
    # DATE FILTER
    # --------------------------------------------------------

    if date_filter == "today":
        start_date = today
        end_date = today

    elif date_filter == "this_month":
        start_date = today.replace(day=1)
        end_date = today

    elif date_filter == "last_month":
        first_day_this_month = today.replace(day=1)
        last_day_last_month = (
            first_day_this_month
            - timedelta(days=1)
        )
        start_date = last_day_last_month.replace(day=1)
        end_date = last_day_last_month

    elif date_filter == "custom":
        if custom_start and custom_end:
            start_date = datetime.strptime(
                custom_start,
                "%Y-%m-%d"
            ).date()

            end_date = datetime.strptime(
                custom_end,
                "%Y-%m-%d"
            ).date()

    # --------------------------------------------------------
    # BASE QUERYSETS
    # --------------------------------------------------------

    enquiries = Enquiry.objects.all()
    admissions = Admission.objects.all()
    payments = FeePayment.objects.all()

    # --------------------------------------------------------
    # BRANCH FILTER
    # --------------------------------------------------------

    if branch_filter:
        enquiries = enquiries.filter(
            branch__iexact=branch_filter
        )

        admissions = admissions.filter(
            branch__iexact=branch_filter
        )

        payments = payments.filter(
            student__branch__iexact=branch_filter
        )

    # --------------------------------------------------------
    # DATE FILTER
    # --------------------------------------------------------

    if start_date and end_date:
        enquiries = enquiries.filter(
            created_at__date__range=[
                start_date,
                end_date
            ]
        )

        admissions = admissions.filter(
            admission_date__range=[
                start_date,
                end_date
            ]
        )

        payments = payments.filter(
            payment_date__range=[
                start_date,
                end_date
            ]
        )

    # --------------------------------------------------------
    # TOTALS
    # --------------------------------------------------------

    total_enquiries = enquiries.count()

    total_converted = enquiries.filter(
        status="converted"
    ).count()

    total_admissions = admissions.count()

    total_collection = (
        payments.aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    if total_enquiries > 0:
        conversion_rate = round(
            (
                total_converted
                / total_enquiries
            ) * 100,
            1
        )
    else:
        conversion_rate = 0

    # --------------------------------------------------------
    # DETAILED REPORT
    # --------------------------------------------------------

    report_rows = []

    for enquiry in enquiries.select_related("course"):
        report_rows.append(
            {
                "date": enquiry.created_at.date(),
                "name": enquiry.name,
                "course": (
                    enquiry.course.title
                    if enquiry.course
                    else "-"
                ),
                "branch": enquiry.branch,
                "type": "Enquiry",
                "status": enquiry.get_status_display(),
                "amount": None,
            }
        )

    for admission in admissions.select_related("course"):
        report_rows.append(
            {
                "date": admission.admission_date,
                "name": admission.student_name,
                "course": (
                    admission.course.title
                    if admission.course
                    else "-"
                ),
                "branch": admission.branch,
                "type": "Admission",
                "status": admission.get_payment_status_display(),
                "amount": admission.total_fee,
            }
        )

    for payment in payments.select_related(
        "student",
        "student__course"
    ):
        report_rows.append(
            {
                "date": payment.payment_date,
                "name": payment.student.name,
                "course": (
                    payment.student.course.title
                    if payment.student.course
                    else "-"
                ),
                "branch": payment.student.branch,
                "type": "Collection",
                "status": payment.get_payment_mode_display(),
                "amount": payment.amount,
            }
        )

    report_rows.sort(
        key=lambda item: item["date"],
        reverse=True
    )

    # --------------------------------------------------------
    # ENQUIRY REPORT
    # --------------------------------------------------------

    enquiry_report = (
        enquiries
        .select_related(
            "course",
            "assigned_user"
        )
        .order_by("-created_at")
    )

    # --------------------------------------------------------
    # ADMISSION REPORT
    # --------------------------------------------------------

    admission_report = (
        admissions
        .select_related(
            "course",
            "created_by"
        )
        .order_by(
            "-admission_date",
            "-id"
        )
    )

    # --------------------------------------------------------
    # COLLECTION REPORT
    # --------------------------------------------------------

    collection_report = (
        payments
        .select_related(
            "student",
            "student__course",
            "collected_by"
        )
        .order_by(
            "-payment_date",
            "-id"
        )
    )

    return render(
        request,
        "core/reports_dashboard.html",
        {
            "branches": branches,
            "branch_filter": branch_filter,
            "date_filter": date_filter,
            "custom_start": custom_start,
            "custom_end": custom_end,
            "start_date": start_date,
            "end_date": end_date,
            "total_enquiries": total_enquiries,
            "total_converted": total_converted,
            "total_admissions": total_admissions,
            "total_collection": total_collection,
            "conversion_rate": conversion_rate,
            "report_rows": report_rows,
            "enquiry_report": enquiry_report,
            "admission_report": admission_report,
            "collection_report": collection_report,
        }
    )



# ============================================================
# EXPORT REPORTS TO EXCEL
# ============================================================

@login_required
def export_reports_excel(request):

    branch_filter = request.GET.get(
        "branch",
        ""
    ).strip()


    if not request.user.is_superuser:

        user_branch = get_user_branch(
            request.user
        )

        if not user_branch:
            auth_logout(request)
            return redirect(
                "staff_login"
            )

        branch_filter = user_branch

    date_filter = request.GET.get(
        "date_filter",
        "all"
    ).strip()

    custom_start = request.GET.get(
        "start_date",
        ""
    ).strip()

    custom_end = request.GET.get(
        "end_date",
        ""
    ).strip()

    today = timezone.localdate()

    start_date = None
    end_date = None

    if date_filter == "today":
        start_date = today
        end_date = today

    elif date_filter == "this_month":
        start_date = today.replace(day=1)
        end_date = today

    elif date_filter == "last_month":
        first_day_this_month = today.replace(day=1)

        last_day_last_month = (
            first_day_this_month
            - timedelta(days=1)
        )

        start_date = last_day_last_month.replace(day=1)
        end_date = last_day_last_month

    elif date_filter == "custom":
        if custom_start and custom_end:

            start_date = datetime.strptime(
                custom_start,
                "%Y-%m-%d"
            ).date()

            end_date = datetime.strptime(
                custom_end,
                "%Y-%m-%d"
            ).date()

    enquiries = Enquiry.objects.all()
    admissions = Admission.objects.all()

    payments = FeePayment.objects.select_related(
        "student",
        "student__course"
    )

    if branch_filter:

        enquiries = enquiries.filter(
            branch__iexact=branch_filter
        )

        admissions = admissions.filter(
            branch__iexact=branch_filter
        )

        payments = payments.filter(
            student__branch__iexact=branch_filter
        )

    if start_date and end_date:

        enquiries = enquiries.filter(
            created_at__date__range=[
                start_date,
                end_date
            ]
        )

        admissions = admissions.filter(
            admission_date__range=[
                start_date,
                end_date
            ]
        )

        payments = payments.filter(
            payment_date__range=[
                start_date,
                end_date
            ]
        )

    report_rows = []

    for enquiry in enquiries.select_related("course"):

        report_rows.append(
            {
                "date": enquiry.created_at.date(),
                "name": enquiry.name,
                "course": (
                    enquiry.course.title
                    if enquiry.course
                    else "-"
                ),
                "branch": enquiry.branch,
                "type": "Enquiry",
                "status": enquiry.get_status_display(),
                "amount": None,
            }
        )

    for admission in admissions.select_related("course"):

        report_rows.append(
            {
                "date": admission.admission_date,
                "name": admission.student_name,
                "course": (
                    admission.course.title
                    if admission.course
                    else "-"
                ),
                "branch": admission.branch,
                "type": "Admission",
                "status": admission.get_payment_status_display(),
                "amount": admission.total_fee,
            }
        )

    for payment in payments:

        report_rows.append(
            {
                "date": payment.payment_date,
                "name": payment.student.name,
                "course": (
                    payment.student.course.title
                    if payment.student.course
                    else "-"
                ),
                "branch": payment.student.branch,
                "type": "Collection",
                "status": payment.get_payment_mode_display(),
                "amount": payment.amount,
            }
        )

    report_rows.sort(
        key=lambda item: item["date"],
        reverse=True
    )

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "MCTI Report"

    sheet.merge_cells("A1:G1")

    title_cell = sheet["A1"]
    title_cell.value = "MCTI Technologies - Reports"

    title_cell.font = Font(
        bold=True,
        size=16,
        color="FFFFFF"
    )

    title_cell.fill = PatternFill(
        "solid",
        fgColor="111827"
    )

    title_cell.alignment = Alignment(
        horizontal="center"
    )

    headers = [
        "Date",
        "Name",
        "Course",
        "Branch",
        "Type",
        "Status / Mode",
        "Amount",
    ]

    sheet.append(
        ["", "", "", "", "", "", ""]
    )

    sheet.append(headers)

    for cell in sheet[3]:

        cell.font = Font(
            bold=True,
            color="FFFFFF"
        )

        cell.fill = PatternFill(
            "solid",
            fgColor="F97316"
        )

        cell.alignment = Alignment(
            horizontal="center"
        )

    for row in report_rows:

        sheet.append(
            [
                row["date"],
                row["name"],
                row["course"],
                row["branch"],
                row["type"],
                row["status"],
                (
                    row["amount"]
                    if row["amount"] is not None
                    else ""
                ),
            ]
        )

    for row in sheet.iter_rows(
        min_row=4,
        min_col=1,
        max_col=1
    ):
        row[0].number_format = "DD-MMM-YYYY"

    for row in sheet.iter_rows(
        min_row=4,
        min_col=7,
        max_col=7
    ):
        row[0].number_format = '₹#,##0.00'

    widths = {
        "A": 15,
        "B": 28,
        "C": 28,
        "D": 18,
        "E": 18,
        "F": 20,
        "G": 16,
    }

    for column, width in widths.items():
        sheet.column_dimensions[
            column
        ].width = width

    sheet.freeze_panes = "A4"

    response = HttpResponse(
        content_type=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        )
    )

    response["Content-Disposition"] = (
        'attachment; filename="MCTI_Report.xlsx"'
    )

    workbook.save(response)

    return response



# ============================================================
# FEE DUE DATE REPORT
# ============================================================

@login_required
def fee_due_report(request):

    today = timezone.localdate()

    status_filter = request.GET.get(
        "status",
        ""
    ).strip()

    branch_filter = request.GET.get(
        "branch",
        ""
    ).strip()

    search = request.GET.get(
        "search",
        ""
    ).strip()

    branches = [
        ("", "All Branches"),
        ("kharghar", "Kharghar"),
        ("panvel", "Panvel"),
        ("koperkhairane", "Koperkhairane"),
        ("kamothe", "Kamothe"),
        ("ghansoli", "Ghansoli"),
        ("nerul", "Nerul"),
        ("head_office", "Head Office"),
    ]

    # --------------------------------------------------------
    # ACCESS CONTROL
    # HO/Admin can see all branches.
    # Branch staff can see only their own branch.
    # --------------------------------------------------------

    if not is_admin_user(request.user):

        user_branch = get_user_branch(
            request.user
        )

        if not user_branch:
            auth_logout(request)
            return redirect(
                "staff_login"
            )

        branch_filter = user_branch

        branches = [
            item
            for item in branches
            if item[0] == user_branch
        ]

    admissions = (
        Admission.objects
        .select_related(
            "course",
            "student",
        )
        .order_by(
            "admission_date",
            "id",
        )
    )

    if branch_filter:
        admissions = admissions.filter(
            branch__iexact=branch_filter
        )

    if search:
        admissions = admissions.filter(
            Q(student_name__icontains=search)
            |
            Q(admission_number__icontains=search)
            |
            Q(student__name__icontains=search)
            |
            Q(student__mobile__icontains=search)
            |
            Q(course__title__icontains=search)
        )

    due_rows = []

    counts = {
        "overdue": 0,
        "today": 0,
        "upcoming": 0,
        "future": 0,
        "paid": 0,
    }

    total_outstanding = 0

    for admission in admissions:

        student = getattr(
            admission,
            "student",
            None
        )

        total_fee = (
            admission.total_fee
            or 0
        )

        paid_fee = 0

        if student:
            paid_fee = (
                FeePayment.objects
                .filter(
                    student=student
                )
                .aggregate(
                    total=Sum("amount")
                )["total"]
                or 0
            )

        balance_fee = max(
            total_fee - paid_fee,
            0
        )

        next_due_date = None
        due_key = "paid"
        due_status = "Fully Paid"
        days_remaining = None

        if balance_fee > 0:

            total_outstanding += balance_fee

            if admission.admission_date:

                admission_date = (
                    admission.admission_date
                )

                if hasattr(
                    admission_date,
                    "date"
                ):
                    admission_date = (
                        admission_date.date()
                    )

                next_due_date = (
                    admission_date
                    + timedelta(days=31)
                )

                days_remaining = (
                    next_due_date - today
                ).days

                if next_due_date < today:
                    due_key = "overdue"
                    due_status = "Overdue"

                elif next_due_date == today:
                    due_key = "today"
                    due_status = "Due Today"

                elif days_remaining <= 7:
                    due_key = "upcoming"
                    due_status = "Upcoming 7 Days"

                else:
                    due_key = "future"
                    due_status = "Future Due"

            else:
                due_key = "future"
                due_status = "Due Date Not Available"

        counts[due_key] += 1

        if (
            status_filter
            and due_key != status_filter
        ):
            continue

        due_rows.append(
            {
                "student": student,
                "student_name": (
                    getattr(
                        student,
                        "name",
                        None
                    )
                    or admission.student_name
                    or "-"
                ),
                "mobile": (
                    getattr(
                        student,
                        "mobile",
                        None
                    )
                    or "-"
                ),
                "admission": admission,
                "admission_number": (
                    admission.admission_number
                    or "-"
                ),
                "course": (
                    admission.course.title
                    if admission.course
                    else "-"
                ),
                "branch": (
                    admission.branch
                    or (
                        getattr(
                            student,
                            "branch",
                            None
                        )
                        if student
                        else ""
                    )
                    or "-"
                ),
                "total_fee": total_fee,
                "paid_fee": paid_fee,
                "balance_fee": balance_fee,
                "next_due_date": next_due_date,
                "due_key": due_key,
                "due_status": due_status,
                "days_remaining": days_remaining,
            }
        )

    # Most urgent records first.
    due_rows.sort(
        key=lambda row: (
            row["balance_fee"] <= 0,
            row["next_due_date"] is None,
            row["next_due_date"] or today,
            row["student_name"],
        )
    )

    return render(
        request,
        "core/fee_due_report.html",
        {
            "due_rows": due_rows,
            "counts": counts,
            "total_outstanding": total_outstanding,
            "today": today,
            "branches": branches,
            "branch_filter": branch_filter,
            "status_filter": status_filter,
            "search": search,
            "is_admin": is_admin_user(
                request.user
            ),
        }
    )




# ============================================================
# ATTENDANCE MODULE
# ============================================================

def _attendance_branches():
    return [
        ("kharghar", "Kharghar"),
        ("panvel", "Panvel"),
        ("koperkhairane", "Koperkhairane"),
        ("kamothe", "Kamothe"),
        ("ghansoli", "Ghansoli"),
        ("nerul", "Nerul"),
        ("head_office", "Head Office"),
    ]


def _attendance_access(request):
    """Return (is_admin, branch_filter, branches) for staff attendance pages."""
    admin_access = is_admin_user(request.user)
    branches = _attendance_branches()

    if admin_access:
        return True, "", [("", "All Branches")] + branches

    user_branch = get_user_branch(request.user)

    if not user_branch:
        return False, None, []

    return (
        False,
        user_branch,
        [item for item in branches if item[0] == user_branch],
    )


@login_required
def attendance_dashboard(request):

    today = timezone.localdate()
    admin_access, forced_branch, branches = _attendance_access(request)

    if forced_branch is None:
        auth_logout(request)
        return redirect("staff_login")

    branch_filter = request.GET.get("branch", "").strip()

    if not admin_access:
        branch_filter = forced_branch

    students = Student.objects.filter(status="active")
    records = Attendance.objects.filter(attendance_date=today)

    if branch_filter:
        students = students.filter(branch__iexact=branch_filter)
        records = records.filter(branch__iexact=branch_filter)

    total_students = students.count()
    marked_count = records.count()
    present_count = records.filter(status="present").count()
    absent_count = records.filter(status="absent").count()
    leave_count = records.filter(status="leave").count()
    pending_count = max(total_students - marked_count, 0)

    recent_records = (
        records
        .select_related("student", "course", "marked_by")
        .order_by("-updated_at")[:20]
    )

    return render(
        request,
        "core/attendance_dashboard.html",
        {
            "today": today,
            "branches": branches,
            "branch_filter": branch_filter,
            "is_admin": admin_access,
            "total_students": total_students,
            "marked_count": marked_count,
            "present_count": present_count,
            "absent_count": absent_count,
            "leave_count": leave_count,
            "pending_count": pending_count,
            "recent_records": recent_records,
        }
    )


@login_required
def mark_attendance(request):

    today = timezone.localdate()
    admin_access, forced_branch, branches = _attendance_access(request)

    if forced_branch is None:
        auth_logout(request)
        return redirect("staff_login")

    date_value = request.GET.get(
        "date",
        request.POST.get("attendance_date", today.isoformat())
    ).strip()

    try:
        attendance_date = datetime.strptime(
            date_value,
            "%Y-%m-%d"
        ).date()
    except (TypeError, ValueError):
        attendance_date = today

    branch_filter = request.GET.get(
        "branch",
        request.POST.get("branch", "")
    ).strip()

    course_filter = request.GET.get(
        "course",
        request.POST.get("course", "")
    ).strip()

    if not admin_access:
        branch_filter = forced_branch

    students = (
        Student.objects
        .filter(status="active")
        .select_related("course")
        .order_by("name")
    )

    if branch_filter:
        students = students.filter(branch__iexact=branch_filter)

    if course_filter:
        students = students.filter(course_id=course_filter)

    courses = Course.objects.filter(is_active=True).order_by("title")

    if branch_filter:
        active_course_ids = (
            Student.objects
            .filter(
                status="active",
                branch__iexact=branch_filter,
                course__isnull=False,
            )
            .values_list("course_id", flat=True)
            .distinct()
        )
        courses = courses.filter(id__in=active_course_ids)

    if request.method == "POST":

        saved_count = 0

        for student in students:

            status_value = request.POST.get(
                f"status_{student.id}",
                ""
            ).strip()

            if status_value not in {
                "present",
                "absent",
                "leave",
            }:
                continue

            remarks = request.POST.get(
                f"remarks_{student.id}",
                ""
            ).strip()

            Attendance.objects.update_or_create(
                student=student,
                attendance_date=attendance_date,
                defaults={
                    "status": status_value,
                    "branch": student.branch or "",
                    "course": student.course,
                    "remarks": remarks,
                    "marked_by": request.user,
                }
            )

            saved_count += 1

        messages.success(
            request,
            f"Attendance saved successfully for {saved_count} student(s)."
        )

        redirect_url = reverse(
            "mark_attendance"
        )

        query_parts = [
            f"date={attendance_date.isoformat()}"
        ]

        if branch_filter:
            query_parts.append(
                f"branch={branch_filter}"
            )

        if course_filter:
            query_parts.append(
                f"course={course_filter}"
            )

        return redirect(
            f"{redirect_url}?{'&'.join(query_parts)}"
        )

    existing_records = {
        record.student_id: record
        for record in Attendance.objects.filter(
            student__in=students,
            attendance_date=attendance_date,
        )
    }

    student_rows = []

    for student in students:
        student_rows.append(
            {
                "student": student,
                "record": existing_records.get(student.id),
            }
        )

    return render(
        request,
        "core/mark_attendance.html",
        {
            "attendance_date": attendance_date,
            "branches": branches,
            "branch_filter": branch_filter,
            "courses": courses,
            "course_filter": course_filter,
            "student_rows": student_rows,
            "is_admin": admin_access,
        }
    )


@login_required
def attendance_report(request):

    today = timezone.localdate()
    admin_access, forced_branch, branches = _attendance_access(request)

    if forced_branch is None:
        auth_logout(request)
        return redirect("staff_login")

    branch_filter = request.GET.get("branch", "").strip()
    course_filter = request.GET.get("course", "").strip()
    status_filter = request.GET.get("status", "").strip()
    search = request.GET.get("search", "").strip()
    start_date_value = request.GET.get("start_date", "").strip()
    end_date_value = request.GET.get("end_date", "").strip()

    if not admin_access:
        branch_filter = forced_branch

    start_date = today.replace(day=1)
    end_date = today

    if start_date_value:
        try:
            start_date = datetime.strptime(
                start_date_value,
                "%Y-%m-%d"
            ).date()
        except ValueError:
            pass

    if end_date_value:
        try:
            end_date = datetime.strptime(
                end_date_value,
                "%Y-%m-%d"
            ).date()
        except ValueError:
            pass

    records = (
        Attendance.objects
        .select_related(
            "student",
            "course",
            "marked_by",
        )
        .filter(
            attendance_date__range=[
                start_date,
                end_date,
            ]
        )
    )

    if branch_filter:
        records = records.filter(
            branch__iexact=branch_filter
        )

    if course_filter:
        records = records.filter(
            course_id=course_filter
        )

    if status_filter:
        records = records.filter(
            status=status_filter
        )

    if search:
        records = records.filter(
            Q(student__student_id__icontains=search)
            | Q(student__name__icontains=search)
            | Q(student__mobile__icontains=search)
            | Q(course__title__icontains=search)
        )

    records = records.order_by(
        "-attendance_date",
        "student__name",
    )

    total_records = records.count()
    present_count = records.filter(status="present").count()
    absent_count = records.filter(status="absent").count()
    leave_count = records.filter(status="leave").count()

    attendance_percentage = 0

    if total_records > 0:
        attendance_percentage = round(
            (present_count / total_records) * 100,
            1
        )

    courses = Course.objects.filter(
        is_active=True
    ).order_by("title")

    return render(
        request,
        "core/attendance_report.html",
        {
            "records": records,
            "branches": branches,
            "branch_filter": branch_filter,
            "courses": courses,
            "course_filter": course_filter,
            "status_filter": status_filter,
            "search": search,
            "start_date": start_date,
            "end_date": end_date,
            "total_records": total_records,
            "present_count": present_count,
            "absent_count": absent_count,
            "leave_count": leave_count,
            "attendance_percentage": attendance_percentage,
            "is_admin": admin_access,
        }
    )


# ============================================================
# STAFF LOGIN
# ============================================================

def staff_login(request):

    # --------------------------------------------------------
    # ALREADY LOGGED IN
    # --------------------------------------------------------

    if request.user.is_authenticated:

        if is_admin_user(request.user):
            return redirect(
                "management_dashboard"
            )

        if request.user.is_staff:

            branch = get_user_branch(
                request.user
            )

            if branch:
                return redirect(
                    "branch_dashboard"
                )

            auth_logout(request)

            return render(
                request,
                "core/staff_login.html",
                {
                    "error": (
                        "Branch is not assigned "
                        "to this staff account."
                    )
                }
            )

        # Student/other user should not enter staff portal
        auth_logout(request)

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        ).strip()

        if not username or not password:

            return render(
                request,
                "core/staff_login.html",
                {
                    "error": (
                        "Please enter username "
                        "and password."
                    )
                }
            )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is None:

            return render(
                request,
                "core/staff_login.html",
                {
                    "error": (
                        "Invalid username or password."
                    )
                }
            )

        if not user.is_active:

            return render(
                request,
                "core/staff_login.html",
                {
                    "error": (
                        "This account is inactive."
                    )
                }
            )

        if not (
            user.is_staff
            or user.is_superuser
        ):

            return render(
                request,
                "core/staff_login.html",
                {
                    "error": (
                        "You are not authorized as staff."
                    )
                }
            )

        login(
            request,
            user
        )

        if is_admin_user(user):
            return redirect(
                "management_dashboard"
            )

        branch = get_user_branch(
            user
        )

        if branch:
            return redirect(
                "branch_dashboard"
            )

        auth_logout(request)

        return render(
            request,
            "core/staff_login.html",
            {
                "error": (
                    "Branch is not assigned "
                    "to this staff account."
                )
            }
        )

    # --------------------------------------------------------
    # LOGIN PAGE
    # --------------------------------------------------------

    return render(
        request,
        "core/staff_login.html"
    )


# ============================================================
# STAFF LOGOUT
# ============================================================

@login_required
def staff_logout(request):

    auth_logout(request)

    return redirect(
        "staff_login"
    )


# ============================================================
# STUDENT LOGIN
# ============================================================

def student_login(request):

    # --------------------------------------------------------
    # ALREADY LOGGED IN
    # --------------------------------------------------------

    if request.user.is_authenticated:

        admission = (
            Admission.objects
            .filter(user=request.user)
            .first()
        )

        if admission:
            return redirect(
                "student_dashboard"
            )

        auth_logout(request)

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        ).strip()

        if not username or not password:

            return render(
                request,
                "core/student_login.html",
                {
                    "error": (
                        "Please enter username "
                        "and password."
                    )
                }
            )

        # ----------------------------------------------------
        # FIND USER
        # ----------------------------------------------------

        user = (
            User.objects
            .filter(
                username=username
            )
            .first()
        )

        if not user:

            return render(
                request,
                "core/student_login.html",
                {
                    "error": (
                        "Invalid username or password."
                    )
                }
            )

        # ----------------------------------------------------
        # ACTIVE CHECK
        # ----------------------------------------------------

        if not user.is_active:

            return render(
                request,
                "core/student_login.html",
                {
                    "error": (
                        "This account is inactive. "
                        "Please contact MCTI."
                    )
                }
            )

        # ----------------------------------------------------
        # PASSWORD CHECK
        # ----------------------------------------------------

        if not user.check_password(
            password
        ):

            return render(
                request,
                "core/student_login.html",
                {
                    "error": (
                        "Invalid username or password."
                    )
                }
            )

        # ----------------------------------------------------
        # CHECK ADMISSION
        # ----------------------------------------------------

        admission = (
            Admission.objects
            .select_related(
                "course",
                "student",
            )
            .filter(
                user=user
            )
            .first()
        )

        if not admission:

            return render(
                request,
                "core/student_login.html",
                {
                    "error": (
                        "This account is not connected "
                        "to a student admission."
                    )
                }
            )

        # ----------------------------------------------------
        # LOGIN USER
        # ----------------------------------------------------

        login(
            request,
            user,
            backend=(
                "django.contrib.auth.backends."
                "ModelBackend"
            )
        )

        return redirect(
            "student_dashboard"
        )

    # --------------------------------------------------------
    # LOGIN PAGE
    # --------------------------------------------------------

    return render(
        request,
        "core/student_login.html"
    )


# ============================================================
# STUDENT LOGOUT
# ============================================================

@login_required
def student_logout(request):

    auth_logout(request)

    return redirect(
        "student_login"
    )


# ============================================================
# STUDENT LIST
# ============================================================

@login_required
def student_list(request):

    search = request.GET.get(
        "search",
        ""
    ).strip()

    students = (
        Student.objects
        .select_related(
            "course",
            "admission",
            "user",
            "created_by",
        )
        .order_by(
            "-joining_date",
            "-id"
        )
    )


    if not request.user.is_superuser:

        user_branch = get_user_branch(
            request.user
        )

        if not user_branch:
            auth_logout(request)
            return redirect(
                "staff_login"
            )

        students = students.filter(
            branch__iexact=user_branch
        )

    if search:

        students = students.filter(
            Q(
                student_id__icontains=search
            )
            |
            Q(
                name__icontains=search
            )
            |
            Q(
                mobile__icontains=search
            )
            |
            Q(
                email__icontains=search
            )
            |
            Q(
                course__title__icontains=search
            )
            |
            Q(
                branch__icontains=search
            )
        )

    return render(
        request,
        "core/student_list.html",
        {
            "students": students,
            "search": search,
        }
    )



# ============================================================
# STAFF LIST
# ============================================================

@login_required
def staff_list(request):

    search = request.GET.get(
        "search",
        ""
    ).strip()

    # --------------------------------------------------------
    # STAFF USERS
    # --------------------------------------------------------

    staff_members = (
        User.objects
        .filter(
            Q(is_staff=True)
            |
            Q(is_superuser=True)
        )
        .select_related(
            "staff_profile"
        )
        .order_by(
            "-is_superuser",
            "username"
        )
    )


    if not request.user.is_superuser:

        user_branch = get_user_branch(
            request.user
        )

        if not user_branch:
            auth_logout(request)
            return redirect(
                "staff_login"
            )

        staff_members = staff_members.filter(
            staff_profile__branch__iexact=user_branch
        )

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    if search:

        staff_members = staff_members.filter(
            Q(
                username__icontains=search
            )
            |
            Q(
                first_name__icontains=search
            )
            |
            Q(
                last_name__icontains=search
            )
            |
            Q(
                email__icontains=search
            )
            |
            Q(
                staff_profile__branch__icontains=search
            )
            |
            Q(
                staff_profile__department__icontains=search
            )
            |
            Q(
                staff_profile__designation__icontains=search
            )
        )

    # --------------------------------------------------------
    # STAFF PERFORMANCE
    # --------------------------------------------------------

    for staff in staff_members:

        # Total assigned enquiries
        staff.total_assigned = (
            Enquiry.objects
            .filter(
                assigned_user=staff
            )
            .count()
        )

        # Total converted enquiries
        staff.total_converted = (
            Enquiry.objects
            .filter(
                assigned_user=staff,
                status="converted"
            )
            .count()
        )

        # Conversion percentage
        if staff.total_assigned > 0:

            staff.conversion_rate = round(
                (
                    staff.total_converted
                    / staff.total_assigned
                ) * 100,
                1
            )

        else:

            staff.conversion_rate = 0

        # Admissions created by staff
        staff.total_admissions = (
            Admission.objects
            .filter(
                created_by=staff
            )
            .count()
        )
        # Total fee collection by staff
        staff.total_collection = (
                FeePayment.objects
                .filter(
                    collected_by=staff
                )
                .aggregate(
                    total=Sum("amount")
                )["total"]
                or 0
            )

    return render(
        request,
        "core/staff_list.html",
        {
            "staff_members": staff_members,
            "search": search,
        }
    )



# ============================================================
# STUDENT DASHBOARD
# ============================================================

@login_required
def student_dashboard(request):

    admission = (
        Admission.objects
        .select_related(
            "course",
            "enquiry",
            "user",
            "student",
        )
        .filter(
            user=request.user
        )
        .first()
    )

    if not admission:

        auth_logout(request)

        return redirect(
            "student_login"
        )

    student = getattr(
        admission,
        "student",
        None
    )

    if not student:

        auth_logout(request)

        return redirect(
            "student_login"
        )

    # ======================================================
    # PAYMENT HISTORY
    # ======================================================

    payments = (
        FeePayment.objects
        .filter(
            student=student
        )
        .order_by(
            "-payment_date",
            "-id"
        )
    )

    # ======================================================
    # FEE CALCULATION
    # ======================================================

    total_fee = (
        admission.total_fee
        or 0
    )

    paid_fee = sum(
        payment.amount or 0
        for payment in payments
    )

    balance_fee = max(
        total_fee - paid_fee,
        0
    )

    # ======================================================
    # PAYMENT STATUS
    # ======================================================

    if paid_fee <= 0:

        payment_status = "Pending"

    elif paid_fee >= total_fee:

        payment_status = "Fully Paid"

    else:

        payment_status = "Partially Paid"

    # ======================================================
    # NEXT FEE DUE DATE
    # Admission Date + 31 Days
    # ======================================================

    next_due_date = None
    due_status = None
    days_remaining = None

    if admission.admission_date and balance_fee > 0:

        admission_date = admission.admission_date

        # If admission_date is DateTimeField
        if hasattr(
            admission_date,
            "date"
        ):
            admission_date = admission_date.date()

        next_due_date = (
            admission_date
            + timedelta(days=31)
        )

        today = timezone.localdate()

        days_remaining = (
            next_due_date - today
        ).days

        if next_due_date < today:

            due_status = "Overdue"

        elif next_due_date == today:

            due_status = "Due Today"

        elif days_remaining <= 7:

            due_status = "Upcoming"

        else:

            due_status = "Future"

    elif balance_fee <= 0:

        due_status = "Paid"

    # ======================================================
    # LATEST PAYMENT
    # ======================================================

    latest_payment = payments.first()

    # ======================================================
    # DASHBOARD
    # ======================================================

    return render(
        request,
        "core/student_dashboard.html",
        {
            "student": student,
            "admission": admission,
            "payments": payments,

            "total_fee": total_fee,
            "paid_fee": paid_fee,
            "balance_fee": balance_fee,
            "payment_status": payment_status,

            "next_due_date": next_due_date,
            "due_status": due_status,
            "days_remaining": days_remaining,

            "latest_payment": latest_payment,
        }
    )




# ============================================================
# STUDENT - MY ATTENDANCE
# ============================================================

@login_required
def student_attendance(request):

    admission = (
        Admission.objects
        .select_related(
            "student",
            "course",
        )
        .filter(
            user=request.user
        )
        .first()
    )

    if not admission:

        auth_logout(request)

        return redirect(
            "student_login"
        )

    student = getattr(
        admission,
        "student",
        None
    )

    if not student:

        auth_logout(request)

        return redirect(
            "student_login"
        )

    today = timezone.localdate()

    month_value = request.GET.get(
        "month",
        today.strftime("%Y-%m")
    ).strip()

    try:
        selected_month = datetime.strptime(
            month_value,
            "%Y-%m"
        ).date().replace(day=1)

    except ValueError:

        selected_month = today.replace(day=1)
        month_value = selected_month.strftime("%Y-%m")

    if selected_month.month == 12:

        next_month = selected_month.replace(
            year=selected_month.year + 1,
            month=1,
            day=1
        )

    else:

        next_month = selected_month.replace(
            month=selected_month.month + 1,
            day=1
        )

    records = (
        Attendance.objects
        .filter(
            student=student,
            attendance_date__gte=selected_month,
            attendance_date__lt=next_month,
        )
        .select_related(
            "course",
            "marked_by",
        )
        .order_by(
            "-attendance_date"
        )
    )

    total_days = records.count()

    present_count = records.filter(
        status="present"
    ).count()

    absent_count = records.filter(
        status="absent"
    ).count()

    leave_count = records.filter(
        status="leave"
    ).count()

    attendance_percentage = 0

    if total_days > 0:

        attendance_percentage = round(
            (
                present_count
                / total_days
            ) * 100,
            1
        )

    attendance_status = "No Attendance Yet"

    if total_days > 0:

        if attendance_percentage >= 75:

            attendance_status = "Good"

        else:

            attendance_status = "Low Attendance"

    return render(
        request,
        "core/student_attendance.html",
        {
            "student": student,
            "admission": admission,
            "records": records,
            "month_value": month_value,
            "selected_month": selected_month,
            "total_days": total_days,
            "present_count": present_count,
            "absent_count": absent_count,
            "leave_count": leave_count,
            "attendance_percentage": attendance_percentage,
            "attendance_status": attendance_status,
        }
    )


# ============================================================
# HOME
# ============================================================

def home(request):

    return render(
        request,
        "core/home.html"
    )


# ============================================================
# ABOUT
# ============================================================

def about(request):

    return render(
        request,
        "about.html"
    )


# ============================================================
# ACADEMY
# ============================================================

def academy(request):

    return render(
        request,
        "academy.html"
    )


# ============================================================
# COURSES
# ============================================================

def courses(request):

    courses = (
        Course.objects
        .filter(
            is_active=True
        )
        .order_by(
            "-created_at"
        )
    )

    return render(
        request,
        "courses.html",
        {
            "courses": courses
        }
    )


# ============================================================
# COURSE DETAIL
# ============================================================

def course_detail(request, slug):

    course = get_object_or_404(
        Course,
        slug=slug
    )

    return render(
        request,
        "course-detail.html",
        {
            "course": course
        }
    )


# ============================================================
# BUSINESS SOLUTIONS
# ============================================================

def business_solutions(request):

    return render(
        request,
        "business-solutions.html"
    )


# ============================================================
# AI
# ============================================================

def ai(request):

    return render(
        request,
        "ai.html"
    )


# ============================================================
# SAAS
# ============================================================

def saas(request):

    return render(
        request,
        "saas.html"
    )


# ============================================================
# CONTACT
# ============================================================

def contact(request):

    if request.method == "POST":

        form = EnquiryForm(
            request.POST
        )

        if form.is_valid():

            enquiry = form.save()

            EnquiryActivity.objects.create(
                enquiry=enquiry,
                activity_type="note",
                message=(
                    "New enquiry received "
                    "from website."
                ),
                created_by=(
                    request.user
                    if request.user.is_authenticated
                    else None
                )
            )

            return redirect(
                "contact_success"
            )

    else:

        form = EnquiryForm()

    return render(
        request,
        "core/contact.html",
        {
            "form": form
        }
    )


# ============================================================
# CONTACT SUCCESS
# ============================================================

def contact_success(request):

    return render(
        request,
        "core/contact_success.html"
    )


# ============================================================
# ENQUIRY DASHBOARD
# ============================================================

@login_required
def enquiry_dashboard(request):

    today = timezone.localdate()

    if is_admin_user(
        request.user
    ):

        enquiries = (
            Enquiry.objects
            .select_related(
                "course",
                "assigned_user"
            )
            .all()
        )

    else:

        user_branch = get_user_branch(
            request.user
        )

        if not user_branch:
            auth_logout(request)
            return redirect(
                "staff_login"
            )

        enquiries = (
            Enquiry.objects
            .select_related(
                "course",
                "assigned_user"
            )
            .filter(
                branch__iexact=user_branch
            )
        )

    search = request.GET.get(
        "search",
        ""
    ).strip()

    if search:

        enquiries = enquiries.filter(
            Q(
                name__icontains=search
            )
            |
            Q(
                mobile__icontains=search
            )
            |
            Q(
                email__icontains=search
            )
        )

    status_filter = request.GET.get(
        "status",
        ""
    ).strip()

    if status_filter:

        enquiries = enquiries.filter(
            status=status_filter
        )

    assigned_filter = request.GET.get(
        "assigned_to",
        ""
    ).strip()

    if (
        is_admin_user(request.user)
        and assigned_filter
    ):

        enquiries = enquiries.filter(
            assigned_user_id=assigned_filter
        )

    followup_filter = request.GET.get(
        "followup",
        ""
    ).strip()

    if followup_filter == "today":

        enquiries = enquiries.filter(
            followup_date=today
        )

    elif followup_filter == "overdue":

        enquiries = (
            enquiries
            .filter(
                followup_date__lt=today
            )
            .exclude(
                status="converted"
            )
            .exclude(
                status="closed"
            )
        )

    elif followup_filter == "upcoming":

        enquiries = (
            enquiries
            .filter(
                followup_date__gt=today
            )
            .exclude(
                status="converted"
            )
            .exclude(
                status="closed"
            )
        )

    if is_admin_user(
        request.user
    ):

        count_queryset = (
            Enquiry.objects.all()
        )

    else:

        count_queryset = (
            Enquiry.objects
            .filter(
                branch__iexact=user_branch
            )
        )

    total = (
        count_queryset.count()
    )

    new = (
        count_queryset
        .filter(
            status="new"
        )
        .count()
    )

    contacted = (
        count_queryset
        .filter(
            status="contacted"
        )
        .count()
    )

    followup = (
        count_queryset
        .filter(
            status="followup"
        )
        .count()
    )

    converted = (
        count_queryset
        .filter(
            status="converted"
        )
        .count()
    )

    closed = (
        count_queryset
        .filter(
            status="closed"
        )
        .count()
    )

    enquiries = (
        enquiries
        .order_by(
            "-created_at"
        )[:100]
    )

    todays_followups = (
        count_queryset
        .select_related(
            "course",
            "assigned_user"
        )
        .filter(
            followup_date=today
        )
        .exclude(
            status="converted"
        )
        .exclude(
            status="closed"
        )
        .order_by(
            "created_at"
        )
    )

    overdue_followups = (
        count_queryset
        .select_related(
            "course",
            "assigned_user"
        )
        .filter(
            followup_date__lt=today
        )
        .exclude(
            status="converted"
        )
        .exclude(
            status="closed"
        )
        .order_by(
            "followup_date"
        )
    )

    upcoming_followups = (
        count_queryset
        .filter(
            followup_date__gt=today
        )
        .exclude(
            status="converted"
        )
        .exclude(
            status="closed"
        )
        .count()
    )

    if is_admin_user(
        request.user
    ):

        assigned_staff = (
            User.objects
            .filter(
                is_active=True
            )
            .order_by(
                "first_name",
                "username"
            )
        )

    else:

        assigned_staff = []

    return render(
        request,
        "core/enquiry_dashboard.html",
        {
            "total": total,
            "new": new,
            "contacted": contacted,
            "followup": followup,
            "converted": converted,
            "closed": closed,
            "enquiries": enquiries,
            "todays_followups": todays_followups,
            "overdue_followups": overdue_followups,
            "upcoming_followups": upcoming_followups,
            "search": search,
            "status_filter": status_filter,
            "assigned_filter": assigned_filter,
            "followup_filter": followup_filter,
            "assigned_staff": assigned_staff,
            "is_admin": is_admin_user(
                request.user
            ),
        }
    )



# ============================================================
# UPDATE ENQUIRY STATUS
# ============================================================

@login_required
def update_enquiry_status(
    request,
    enquiry_id
):

    enquiry = get_object_or_404(
        Enquiry,
        id=enquiry_id
    )

    if not user_can_access_enquiry(
        request.user,
        enquiry
    ):

        return redirect(
            "enquiry_dashboard"
        )

    if request.method == "POST":

        old_status = (
            enquiry.status
        )

        old_status_display = (
            enquiry.get_status_display()
        )

        form = EnquiryStatusForm(
            request.POST,
            instance=enquiry
        )

        if form.is_valid():

            updated_enquiry = (
                form.save()
            )

            new_status = (
                updated_enquiry.status
            )

            new_status_display = (
                updated_enquiry
                .get_status_display()
            )

            if old_status != new_status:

                EnquiryActivity.objects.create(
                    enquiry=enquiry,
                    activity_type="status",
                    message=(
                        f"Status changed from "
                        f"{old_status_display} "
                        f"to "
                        f"{new_status_display}."
                    ),
                    created_by=request.user
                )

                if (
                    new_status
                    == "converted"
                ):

                    EnquiryActivity.objects.create(
                        enquiry=enquiry,
                        activity_type="converted",
                        message=(
                            "Lead converted successfully."
                        ),
                        created_by=request.user
                    )

    return redirect(
        "enquiry_dashboard"
    )


# ============================================================
# ENQUIRY DETAIL
# ============================================================

@login_required
def enquiry_detail(
    request,
    enquiry_id
):

    enquiry = get_object_or_404(
        Enquiry.objects.select_related(
            "course",
            "assigned_user"
        ),
        id=enquiry_id
    )

    if not user_can_access_enquiry(
        request.user,
        enquiry
    ):

        return redirect(
            "enquiry_dashboard"
        )

    if request.method == "POST":

        if "assigned_user" in request.POST:

            if not is_admin_user(
                request.user
            ):

                return redirect(
                    "enquiry_detail",
                    enquiry_id=enquiry.id
                )

            assignment_form = (
                EnquiryAssignmentForm(
                    request.POST,
                    instance=enquiry
                )
            )

            if assignment_form.is_valid():

                old_staff = (
                    enquiry.assigned_user
                )

                updated_enquiry = (
                    assignment_form.save()
                )

                new_staff = (
                    updated_enquiry
                    .assigned_user
                )

                if old_staff != new_staff:

                    if new_staff:

                        staff_name = (
                            new_staff.get_full_name()
                            or new_staff.username
                        )

                        message = (
                            f"Lead assigned to "
                            f"{staff_name}."
                        )

                    else:

                        message = (
                            "Lead assignment removed."
                        )

                    EnquiryActivity.objects.create(
                        enquiry=enquiry,
                        activity_type="note",
                        message=message,
                        created_by=request.user
                    )

                return redirect(
                    "enquiry_detail",
                    enquiry_id=enquiry.id
                )

        else:

            old_followup_date = (
                enquiry.followup_date
            )

            old_followup_notes = (
                enquiry.followup_notes
                or ""
            ).strip()

            form = EnquiryFollowupForm(
                request.POST,
                instance=enquiry
            )

            if form.is_valid():

                updated_enquiry = (
                    form.save()
                )

                new_followup_date = (
                    updated_enquiry
                    .followup_date
                )

                new_followup_notes = (
                    updated_enquiry
                    .followup_notes
                    or ""
                ).strip()

                if (
                    old_followup_date
                    != new_followup_date
                    or
                    old_followup_notes
                    != new_followup_notes
                ):

                    if new_followup_date:

                        followup_date_text = (
                            new_followup_date
                            .strftime(
                                "%d %b %Y"
                            )
                        )

                    else:

                        followup_date_text = (
                            "Not scheduled"
                        )

                    notes = (
                        new_followup_notes
                        or "No notes added."
                    )

                    EnquiryActivity.objects.create(
                        enquiry=enquiry,
                        activity_type="followup",
                        message=(
                            f"Follow-up scheduled for "
                            f"{followup_date_text}. "
                            f"Notes: {notes}"
                        ),
                        created_by=request.user
                    )

                return redirect(
                    "enquiry_detail",
                    enquiry_id=enquiry.id
                )

    else:

        form = EnquiryFollowupForm(
            instance=enquiry
        )

    if is_admin_user(
        request.user
    ):

        assignment_form = (
            EnquiryAssignmentForm(
                instance=enquiry
            )
        )

    else:

        assignment_form = None

    activities = (
        EnquiryActivity.objects
        .select_related(
            "created_by"
        )
        .filter(
            enquiry=enquiry
        )
        .order_by(
            "-created_at"
        )
    )

    return render(
        request,
        "core/enquiry_detail.html",
        {
            "enquiry": enquiry,
            "form": form,
            "assignment_form": assignment_form,
            "activities": activities,
            "is_admin": is_admin_user(
                request.user
            ),
        }
    )


# ============================================================
# LOG CALL ACTIVITY
# ============================================================

@login_required
def log_enquiry_call(
    request,
    enquiry_id
):

    enquiry = get_object_or_404(
        Enquiry,
        id=enquiry_id
    )

    if not user_can_access_enquiry(
        request.user,
        enquiry
    ):

        return redirect(
            "enquiry_dashboard"
        )

    if request.method == "POST":

        EnquiryActivity.objects.create(
            enquiry=enquiry,
            activity_type="call",
            message=(
                "Call initiated with this lead."
            ),
            created_by=request.user
        )

    return redirect(
        "enquiry_detail",
        enquiry_id=enquiry.id
    )


# ============================================================
# LOG WHATSAPP ACTIVITY
# ============================================================

@login_required
def log_enquiry_whatsapp(
    request,
    enquiry_id
):

    enquiry = get_object_or_404(
        Enquiry,
        id=enquiry_id
    )

    if not user_can_access_enquiry(
        request.user,
        enquiry
    ):

        return redirect(
            "enquiry_dashboard"
        )

    if request.method == "POST":

        EnquiryActivity.objects.create(
            enquiry=enquiry,
            activity_type="whatsapp",
            message=(
                "WhatsApp conversation initiated "
                "with this lead."
            ),
            created_by=request.user
        )

    return redirect(
        "enquiry_detail",
        enquiry_id=enquiry.id
    )


# ============================================================
# LEAD → ADMISSION
# ============================================================

@login_required
def create_admission(
    request,
    enquiry_id
):

    enquiry = get_object_or_404(
        Enquiry,
        id=enquiry_id
    )

    # --------------------------------------------------------
    # ACCESS
    # --------------------------------------------------------

    if not user_can_access_enquiry(
        request.user,
        enquiry
    ):

        return redirect(
            "enquiry_dashboard"
        )

    # --------------------------------------------------------
    # PREVENT DUPLICATE ADMISSION
    # --------------------------------------------------------

    if hasattr(
        enquiry,
        "admission"
    ):

        return redirect(
            "admission_detail",
            admission_id=(
                enquiry.admission.id
            )
        )

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    if request.method == "POST":

        form = AdmissionForm(
            request.POST,
            request.FILES,
            enquiry=enquiry
        )

        if form.is_valid():

            # ------------------------------------------------
            # SAVE ADMISSION
            # ------------------------------------------------

            admission = form.save(
                commit=False
            )

            # Branch must follow the branch selected in Enquiry.
            if not admission.branch:
                admission.branch = (
                    enquiry.branch
                    or get_user_branch(request.user)
                    or ""
                )


            admission.enquiry = enquiry

            admission.created_by = (
                request.user
            )

            # Save first so Admission Number is generated
            admission.save()

            # ------------------------------------------------
            # STUDENT LOGIN DETAILS
            # ------------------------------------------------

            student_username = (
                admission
                .admission_number
                .strip()
            )

            student_password = (
                admission.mobile.strip()
            )

            # ------------------------------------------------
            # FIND / CREATE DJANGO USER
            # ------------------------------------------------

            student_user = (
                User.objects
                .filter(
                    username=student_username
                )
                .first()
            )

            if student_user:

                student_user.set_password(
                    student_password
                )

            else:

                student_user = (
                    User.objects.create_user(
                        username=student_username,
                        email=(
                            admission.email
                            or ""
                        ),
                        password=student_password
                    )
                )

            # ------------------------------------------------
            # UPDATE USER PROFILE
            # ------------------------------------------------

            student_user.first_name = (
                admission.student_name
            )

            student_user.email = (
                admission.email
                or ""
            )

            student_user.is_active = True

            student_user.save()

            # ------------------------------------------------
            # CONNECT ADMISSION → USER
            # ------------------------------------------------

            admission.user = (
                student_user
            )

            admission.save()

            # ------------------------------------------------
            # CREATE / GET STUDENT PROFILE
            # ------------------------------------------------

            student, created = (
                Student.objects.get_or_create(
                    admission=admission,
                    defaults={
                        "user": student_user,
                        "student_id": (
                            admission.admission_number
                        ),
                        "name": (
                            admission.student_name
                        ),
                        "mobile": (
                            admission.mobile
                        ),
                        "email": (
                            admission.email
                            or ""
                        ),
                        "course": (
                            admission.course
                        ),
                        "branch": (
                            admission.branch
                            or ""
                        ),
                        "joining_date": (
                            admission.admission_date
                        ),
                        "status": "active",
                        "trainer": None,
                        "notes": (
                            admission.notes
                            or ""
                        ),
                        "created_by": (
                            request.user
                        ),
                    }
                )
            )

            # ------------------------------------------------
            # UPDATE STUDENT
            # ------------------------------------------------

            student.user = (
                student_user
            )

            student.student_id = (
                admission.admission_number
            )

            student.name = (
                admission.student_name
            )

            student.mobile = (
                admission.mobile
            )

            student.email = (
                admission.email
                or ""
            )

            student.course = (
                admission.course
            )

            student.branch = (
                admission.branch
                or ""
            )

            student.joining_date = (
                admission.admission_date
            )

            student.status = "active"

            student.notes = (
                admission.notes
                or ""
            )

            student.save()

            # ------------------------------------------------
            # UPDATE LEAD STATUS
            # ------------------------------------------------

            enquiry.status = (
                "converted"
            )

            enquiry.save(
                update_fields=[
                    "status"
                ]
            )

            # ------------------------------------------------
            # ACTIVITY
            # ------------------------------------------------

            EnquiryActivity.objects.create(
                enquiry=enquiry,
                activity_type="converted",
                message=(
                    f"Lead converted to Admission "
                    f"{admission.admission_number}."
                ),
                created_by=request.user
            )

            return redirect(
                "admission_detail",
                admission_id=admission.id
            )

    else:

        form = AdmissionForm(
            enquiry=enquiry
        )

    return render(
        request,
        "core/create_admission.html",
        {
            "enquiry": enquiry,
            "form": form,
        }
    )


# ============================================================
# ADMISSION LIST
# ============================================================

@login_required
def admission_list(request):

    search = request.GET.get(
        "search",
        ""
    ).strip()

    admissions = (
        Admission.objects
        .select_related(
            "course",
            "student",
            "user",
            "created_by",
        )
        .order_by(
            "-admission_date",
            "-id"
        )
    )


    if not request.user.is_superuser:

        user_branch = get_user_branch(
            request.user
        )

        if not user_branch:
            auth_logout(request)
            return redirect(
                "staff_login"
            )

        admissions = admissions.filter(
            branch__iexact=user_branch
        )

    if search:

        admissions = admissions.filter(
            Q(
                admission_number__icontains=search
            )
            |
            Q(
                student_name__icontains=search
            )
            |
            Q(
                mobile__icontains=search
            )
            |
            Q(
                email__icontains=search
            )
            |
            Q(
                course__title__icontains=search
            )
        )

    return render(
        request,
        "core/admission_list.html",
        {
            "admissions": admissions,
            "search": search,
        }
    )



# ============================================================
# ADMISSION DETAIL
# ============================================================

@login_required
def admission_detail(
    request,
    admission_id
):

    admission = get_object_or_404(
        Admission.objects.select_related(
            "course",
            "enquiry",
            "created_by",
            "student",
            "user"
        ),
        id=admission_id
    )

    if not user_can_access_admission(
        request.user,
        admission
    ):

        return redirect(
            "admission_list"
        )

    return render(
        request,
        "core/admission_detail.html",
        {
            "admission": admission,
            "is_admin": is_admin_user(
                request.user
            ),
        }
    )
@login_required
def edit_admission(
    request,
    admission_id
):

    admission = get_object_or_404(
        Admission,
        id=admission_id
    )

    # Old admissions may have blank branch even though the original
    # enquiry already has one. Backfill it automatically.
    if (
        not admission.branch
        and getattr(admission, "enquiry_id", None)
        and admission.enquiry
        and admission.enquiry.branch
    ):
        admission.branch = admission.enquiry.branch
        admission.save(
            update_fields=["branch"]
        )

        student = getattr(
            admission,
            "student",
            None
        )

        if student and not student.branch:
            student.branch = admission.branch
            student.save(
                update_fields=["branch"]
            )

    # HO / Admin only
    if not is_admin_user(request.user):
        return redirect(
            "admission_detail",
            admission_id=admission.id
        )

    if request.method == "POST":

        form = AdmissionEditForm(
            request.POST,
            request.FILES,
            instance=admission
        )

        if form.is_valid():

            admission = form.save()

            # Keep linked Student record synchronized with Admission.
            student = getattr(
                admission,
                "student",
                None
            )

            if student:

                student.name = admission.student_name
                student.mobile = admission.mobile
                student.email = admission.email
                student.course = admission.course
                student.branch = admission.branch
                student.joining_date = admission.admission_date
                student.status = "active"

                student.save(
                    update_fields=[
                        "name",
                        "mobile",
                        "email",
                        "course",
                        "branch",
                        "joining_date",
                        "status",
                    ]
                )

            return redirect(
                "admission_detail",
                admission_id=admission.id
            )

    else:

        form = AdmissionEditForm(
            instance=admission
        )

    return render(
        request,
        "core/edit_admission.html",
        {
            "form": form,
            "admission": admission,
        }
    )


# ============================================================
# FEE RECEIPT
# ============================================================

@login_required
def fee_receipt(
    request,
    receipt_number
):

    payment = get_object_or_404(
        FeePayment.objects.select_related(
            "student",
            "student__user"
        ),
        receipt_number=receipt_number
    )

    if not user_can_access_student(
        request.user,
        payment.student
    ):

        return redirect(
            "fee_payment_list"
        )

    return render(
        request,
        "core/fee_receipt.html",
        {
            "payment": payment
        }
    )



# ============================================================
# FEE PAYMENT LIST
# ============================================================

@login_required
def fee_payment_list(request):

    search = request.GET.get(
        "search",
        ""
    ).strip()

    student_id = request.GET.get(
        "student"
    )

    selected_student = None

    if student_id:

        selected_student = (
            Student.objects
            .select_related(
                "course"
            )
            .filter(
                id=student_id
            )
            .first()
        )

    payments = (
        FeePayment.objects
        .select_related(
            "student",
            "student__course"
        )
        .order_by(
            "-payment_date",
            "-id"
        )
    )


    if not request.user.is_superuser:

        user_branch = get_user_branch(
            request.user
        )

        if not user_branch:
            auth_logout(request)
            return redirect(
                "staff_login"
            )

        payments = payments.filter(
            student__branch__iexact=user_branch
        )

        if (
            selected_student
            and not user_can_access_student(
                request.user,
                selected_student
            )
        ):
            selected_student = None
            student_id = None

    if student_id:

        payments = payments.filter(
            student_id=student_id
        )

    if search:

        payments = payments.filter(
            Q(
                receipt_number__icontains=search
            )
            |
            Q(
                student__name__icontains=search
            )
            |
            Q(
                student__student_id__icontains=search
            )
            |
            Q(
                student__mobile__icontains=search
            )
        )

    return render(
        request,
        "core/fee_payment_list.html",
        {
            "payments": payments,
            "search": search,
            "selected_student": selected_student,
        }
    )



# ============================================================
# ADD FEE PAYMENT
# ============================================================

@login_required
def add_fee_payment(
    request,
    student_id
):

    student = get_object_or_404(
        Student,
        id=student_id
    )


    if not request.user.is_superuser:

        user_branch = get_user_branch(
            request.user
        )

        if not user_branch:
            auth_logout(request)
            return redirect(
                "staff_login"
            )

        if (
            (student.branch or "").strip().lower()
            != user_branch.strip().lower()
        ):
            return redirect(
                "student_list"
            )

    if request.method == "POST":

        form = FeePaymentForm(
            request.POST
        )

        if form.is_valid():

            payment = form.save(
                commit=False
            )

            payment.student = (
                student
            )

            payment.collected_by = (
                request.user
            )

            payment.save()

            if student.admission:

                return redirect(
                    "admission_detail",
                    admission_id=(
                        student.admission.id
                    )
                )

            return redirect(
                "fee_payment_list"
            )

    else:

        form = FeePaymentForm()

    return render(
        request,
        "core/add_fee_payment.html",
        {
            "student": student,
            "form": form,
        }
    )

@login_required
def student_quick_view(request):
        # Student Quick View is only for HO / Admin
    if not is_admin_user(request.user):
        return redirect("branch_dashboard")

    form_no = request.GET.get("form_no", "").strip()

    if not form_no:
        return render(
            request,
            "core/student_quick_view.html",
            {
                "error": None,
                "is_admin": is_admin_user(request.user),
                
            }
        )

    admission = Admission.objects.filter(
        admission_number__iexact=form_no
    ).first()

    if not admission:
        return render(
            request,
            "core/student_quick_view.html",
            {
                "error": "Student / Form Number not found.",
                "form_no": form_no,
                "is_admin": is_admin_user(request.user),
            }
        )

    # HO / Admin can view every branch
    if not is_admin_user(request.user):

        user_branch = get_user_branch(request.user)

        if not user_branch or admission.branch != user_branch:
            return render(
                request,
                "core/student_quick_view.html",
                {
                    "error": "You do not have permission to view this student.",
                    "form_no": form_no,
                    "is_admin": is_admin_user(request.user),
                }
            )

    return redirect(
        "admission_detail",
        admission_id=admission.id
    )
# ============================================================
# PLACEMENT / JOB MANAGEMENT
# ============================================================

@user_passes_test(
    staff_or_admin,
    login_url="staff_login"
)
def job_list(request):

    jobs = (
        JobPost.objects
        .select_related("posted_by")
        .prefetch_related("eligible_courses")
        .order_by("-created_at")
    )

    return render(
        request,
        "core/job_list.html",
        {
            "jobs": jobs,
        }
    )


@user_passes_test(
    staff_or_admin,
    login_url="staff_login"
)
def job_create(request):

    if request.method == "POST":

        form = JobPostForm(request.POST)

        if form.is_valid():

            job = form.save(commit=False)

            # Logged-in user who posted the job
            job.posted_by = request.user

            # Automatically detect staff branch
            try:
                staff_profile = StaffProfile.objects.get(
                    user=request.user
                )

                job.posted_branch = (
                    staff_profile.branch
                    or ""
                )

            except StaffProfile.DoesNotExist:

                # HO / Superuser
                if request.user.is_superuser:
                    job.posted_branch = "Head Office"
                else:
                    job.posted_branch = ""

            job.save()

            # Save eligible courses ManyToMany
            form.save_m2m()

            messages.success(
                request,
                "Job posted successfully."
            )

            return redirect(
                "job_list"
            )

    else:

        form = JobPostForm()

    return render(
        request,
        "core/job_form.html",
        {
            "form": form,
        }
    )


@user_passes_test(
    staff_or_admin,
    login_url="staff_login"
)
def job_detail(request, job_id):

    job = get_object_or_404(
        JobPost.objects
        .select_related("posted_by")
        .prefetch_related("eligible_courses"),
        id=job_id
    )

    return render(
        request,
        "core/job_detail.html",
        {
            "job": job,
        }
    )


@user_passes_test(
    staff_or_admin,
    login_url="staff_login"
)
def job_edit(request, job_id):

    job = get_object_or_404(
        JobPost,
        id=job_id
    )

    # Superuser can edit any job.
    # Staff can edit only their own job.
    if (
        not request.user.is_superuser
        and job.posted_by != request.user
    ):

        messages.error(
            request,
            "You can edit only jobs posted by you."
        )

        return redirect(
            "job_list"
        )

    if request.method == "POST":

        form = JobPostForm(
            request.POST,
            instance=job
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Job updated successfully."
            )

            return redirect(
                "job_detail",
                job_id=job.id
            )

    else:

        form = JobPostForm(
            instance=job
        )

    return render(
        request,
        "core/job_form.html",
        {
            "form": form,
            "job": job,
            "is_edit": True,
        }
    )
@login_required
def student_jobs(request):

    admission = (
        Admission.objects
        .select_related(
            "course",
            "student",
            "enquiry",
        )
        .filter(
            user=request.user
        )
        .first()
    )

    if not admission:

        return redirect("student_login")

    student = admission.student

    jobs = (
        JobPost.objects
        .filter(
            status="active"
        )
        .prefetch_related(
            "eligible_courses"
        )
        .order_by(
            "-created_at"
        )
    )

    student_course = admission.course

    # =========================================================
    # STUDENT MOBILE
    # Used to identify already submitted skill-upgrade enquiries
    # =========================================================

    student_mobile = (
        getattr(student, "mobile", None)
        or (
            admission.enquiry.mobile
            if admission.enquiry
            else ""
        )
        or ""
    )

    # Only open/pending enquiries should block another submission.
    open_skill_enquiries = []

    if student_mobile:

        open_skill_enquiries = list(
            Enquiry.objects
            .filter(
                mobile=student_mobile,
                status__in=[
                    "new",
                    "contacted",
                    "followup",
                ]
            )
            .only(
                "id",
                "course_id",
                "message",
                "status",
            )
        )

    for job in jobs:

        eligible_courses = list(
            job.eligible_courses.all()
        )

        # No eligible course selected means open for everyone
        if not eligible_courses:

            job.student_is_eligible = True

        elif student_course in eligible_courses:

            job.student_is_eligible = True

        else:

            job.student_is_eligible = False

        # -----------------------------------------------------
        # Mark each recommended course if an enquiry for this
        # same student + same course + same job is already open.
        # Template can then show "Enquiry Submitted ✓".
        # -----------------------------------------------------

        job_marker = f"Job: {job.title}"

        for course in eligible_courses:

            course.enquiry_submitted = any(
                enquiry.course_id == course.id
                and job_marker in (enquiry.message or "")
                for enquiry in open_skill_enquiries
            )

    return render(
        request,
        "core/student_jobs.html",
        {
            "admission": admission,
            "student": student,
            "jobs": jobs,
        }
    )
@login_required
def student_course_enquiry(
    request,
    job_id,
    course_id
):

    # =========================================================
    # FIND STUDENT ADMISSION
    # =========================================================

    admission = (
        Admission.objects
        .select_related(
            "course",
            "student",
            "enquiry",
        )
        .filter(
            user=request.user
        )
        .first()
    )

    if not admission:
        return redirect(
            "student_login"
        )

    # =========================================================
    # FIND ACTIVE JOB
    # =========================================================

    job = get_object_or_404(
        JobPost,
        id=job_id,
        status="active"
    )

    # =========================================================
    # FIND INTERESTED COURSE
    # =========================================================

    interested_course = get_object_or_404(
        Course,
        id=course_id,
        is_active=True
    )

    # Security check:
    # Selected course must actually belong to this job.
    if not job.eligible_courses.filter(
        id=interested_course.id
    ).exists():
        messages.error(
            request,
            "This course is not linked to the selected job."
        )
        return redirect(
            "student_jobs"
        )

    student = admission.student

    # =========================================================
    # POST - CREATE ENQUIRY
    # =========================================================

    if request.method == "POST":

        # -----------------------------------------------------
        # STUDENT DETAILS
        # -----------------------------------------------------

        student_name = (
            getattr(student, "name", None)
            or getattr(student, "full_name", None)
            or (
                admission.enquiry.name
                if admission.enquiry
                else request.user.username
            )
        )

        student_mobile = (
            getattr(student, "mobile", None)
            or (
                admission.enquiry.mobile
                if admission.enquiry
                else ""
            )
        )

        student_email = (
            getattr(student, "email", None)
            or (
                admission.enquiry.email
                if admission.enquiry
                else ""
            )
        )

        student_branch = (
            getattr(admission, "branch", None)
            or (
                admission.enquiry.branch
                if admission.enquiry
                else ""
            )
            or getattr(student, "branch", None)
            or ""
        )

        # =====================================================
        # DUPLICATE ENQUIRY CHECK
        # Same student + same course + same job
        # =====================================================

        duplicate_enquiry = (
            Enquiry.objects
            .filter(
                mobile=student_mobile,
                course=interested_course,
                message__icontains=(
                    f"Job: {job.title}"
                ),
                status__in=[
                    "new",
                    "contacted",
                    "followup",
                ]
            )
            .first()
        )

        if duplicate_enquiry:
            messages.info(
                request,
                (
                    f"Your enquiry for "
                    f"{interested_course.title} "
                    f"is already submitted. "
                    f"Our team will follow up with you."
                )
            )
            return redirect(
                "student_jobs"
            )

        # =====================================================
        # CREATE NEW ENQUIRY
        # =====================================================

        enquiry = Enquiry.objects.create(
            name=student_name,
            mobile=student_mobile,
            email=student_email,
            course=interested_course,
            branch=student_branch,
            message=(
                f"Student Placement Skill Upgrade Enquiry\n\n"
                f"Student Admission No: "
                f"{admission.admission_number}\n"
                f"Current Course: "
                f"{admission.course.title if admission.course else 'Not Assigned'}\n"
                f"Interested Course: "
                f"{interested_course.title}\n"
                f"Job: "
                f"{job.title}\n"
                f"Company: "
                f"{job.company_name}\n"
                f"Job Location: "
                f"{job.location or 'Not Mentioned'}\n"
                f"Reason: Student wants to learn "
                f"this course/skill to improve "
                f"eligibility for this job."
            ),
            status="new",
        )

        # =====================================================
        # CREATE ENQUIRY ACTIVITY
        # =====================================================

        EnquiryActivity.objects.create(
            enquiry=enquiry,
            activity_type="note",
            message=(
                "Skill upgrade enquiry generated "
                "from Student Placement Support."
            ),
            created_by=None,
        )

        messages.success(
            request,
            (
                f"Your enquiry for "
                f"{interested_course.title} "
                f"has been submitted successfully. "
                f"MCTI team will contact you."
            )
        )

        return redirect(
            "student_jobs"
        )

    # =========================================================
    # GET - CONFIRMATION PAGE
    # =========================================================

    return render(
        request,
        "core/student_course_enquiry.html",
        {
            "student": student,
            "admission": admission,
            "job": job,
            "interested_course": interested_course,
        }
    )
@login_required
def business_lead_list(request):

    is_admin = is_admin_user(request.user)
    user_branch = get_user_branch(request.user)

    leads = (
        BusinessLead.objects
        .select_related("assigned_to")
        .order_by("-created_at")
    )

    if not is_admin:

        if not user_branch:
            auth_logout(request)
            return redirect("staff_login")

        leads = leads.filter(
            assigned_branch__iexact=user_branch
        )

    status_filter = request.GET.get(
        "status",
        ""
    ).strip()

    service_filter = request.GET.get(
        "service",
        ""
    ).strip()

    search = request.GET.get(
        "search",
        ""
    ).strip()

    if status_filter:
        leads = leads.filter(
            status=status_filter
        )

    if service_filter:
        leads = leads.filter(
            service=service_filter
        )

    if search:
        leads = leads.filter(
            Q(name__icontains=search)
            |
            Q(company_name__icontains=search)
            |
            Q(mobile__icontains=search)
            |
            Q(email__icontains=search)
            |
            Q(project_requirement__icontains=search)
        )

    total_leads = leads.count()

    new_leads = leads.filter(
        status="new"
    ).count()

    contacted_leads = leads.filter(
        status="contacted"
    ).count()

    followup_leads = leads.filter(
        status="followup"
    ).count()

    proposal_leads = leads.filter(
        status="proposal"
    ).count()

    converted_leads = leads.filter(
        status="converted"
    ).count()

    return render(
        request,
        "core/business_lead_list.html",
        {
            "leads": leads,
            "total_leads": total_leads,
            "new_leads": new_leads,
            "contacted_leads": contacted_leads,
            "followup_leads": followup_leads,
            "proposal_leads": proposal_leads,
            "converted_leads": converted_leads,
            "status_filter": status_filter,
            "service_filter": service_filter,
            "search": search,
            "is_admin": is_admin,
        }
    )

def privacy_policy(request):
    return render(request, "core/privacy_policy.html")

def terms_and_conditions(request):
    return render(request, "core/terms_and_conditions.html")
def refund_policy(request):
    return render(request, "core/refund_policy.html")