import calendar

from decimal import Decimal
from django.db import transaction


from math import radians, sin, cos, sqrt, atan2

from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout as auth_logout
from django.contrib import messages
from .models import (
    JobPost,
    StaffProfile,
    StaffLoginLog,
    Attendance,
    BranchLocation,

)
from .forms import JobPostForm
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Q, Sum, Count, Max
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Enrollment
from .forms import EnrollmentForm


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
    MonthlyBranchClosingForm,
    DailyBranchExpenseForm,
    DailyExpenseCancelForm,
)

from .models import (
    Course,
    Stream,
    Enquiry,
    EnquiryActivity,
    Admission,
    Student,
    FeePayment,
    StaffProfile,
    Attendance,
    BusinessLead,
    BusinessLeadActivity,
    BranchPartner,
    MonthlyBranchClosing,
    MonthlyPartnerShare,
    ExpenseCategory,
    DailyBranchExpense,
    DailyExpenseAuditLog,
    MonthlyBranchClosing,
)

def calculate_distance_meters(lat1, lon1, lat2, lon2):
    earth_radius = 6371000  # meters

    lat1 = radians(float(lat1))
    lon1 = radians(float(lon1))
    lat2 = radians(float(lat2))
    lon2 = radians(float(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return earth_radius * c

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


@login_required
def mark_student_attendance(request):

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "Invalid request."
        }, status=405)

    student = getattr(
        request.user,
        "student_account",
        None
    )

    if not student:
        return JsonResponse({
            "success": False,
            "message": "Student account not found."
        }, status=403)

    latitude = request.POST.get("latitude")
    longitude = request.POST.get("longitude")

    if not latitude or not longitude:
        return JsonResponse({
            "success": False,
            "message": "Location not received."
        }, status=400)

    # --------------------------------------------------------
    # CHECK IF ATTENDANCE ALREADY EXISTS TODAY
    # --------------------------------------------------------

    today = timezone.localdate()

    existing_attendance = Attendance.objects.filter(
        student=student,
        attendance_date=today
    ).first()

    if existing_attendance:
        return JsonResponse({
            "success": True,
            "already_marked": True,
            "message": "Attendance already marked for today."
        })

    # --------------------------------------------------------
    # FIND NEAREST ACTIVE BRANCH
    # --------------------------------------------------------

    matched_branch = None
    matched_distance = None

    branches = BranchLocation.objects.filter(
        is_active=True
    )

    for branch in branches:

        distance = calculate_distance_meters(
            latitude,
            longitude,
            branch.latitude,
            branch.longitude
        )

        if distance <= branch.radius_meters:

            if (
                matched_distance is None
                or distance < matched_distance
            ):
                matched_branch = branch
                matched_distance = distance

    if not matched_branch:
        return JsonResponse({
            "success": False,
            "message": "You are outside the allowed branch radius."
        })

    # --------------------------------------------------------
    # MARK ATTENDANCE
    # --------------------------------------------------------

    attendance, created = Attendance.objects.get_or_create(
        student=student,
        attendance_date=today,
        defaults={
            "status": "present",
            "branch": matched_branch.branch_name,
            "course": student.course,
            "first_login_time": timezone.now(),
            "latitude": latitude,
            "longitude": longitude,
            "source": "auto",
        }
    )

    if not created:
        return JsonResponse({
            "success": True,
            "already_marked": True,
            "message": "Attendance already marked for today."
        })

    return JsonResponse({
        "success": True,
        "already_marked": False,
        "branch": matched_branch.branch_name,
        "distance_meters": round(
            matched_distance,
            2
        ),
        "message": "Attendance marked successfully."
    })

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

    admin_access = is_admin_user(
        request.user
    )

    can_view_financials = admin_access

    if not admin_access:

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

        try:
            staff_profile = request.user.staff_profile
            can_view_financials = (
                staff_profile.designation
                .strip()
                .lower()
                == "branch head"
            )
        except StaffProfile.DoesNotExist:
            can_view_financials = False

    branch_data = []

    # --------------------------------------------------------
    # OVERALL TOTALS
    # --------------------------------------------------------

    overall_enquiries = 0
    overall_converted = 0
    overall_admissions = 0
    overall_billing = 0
    overall_collection = 0
    overall_outstanding = 0
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

        enrollments = Enrollment.objects.filter(
            branch__iexact=branch_value
        )

        if start_date and end_date:

            enrollments = enrollments.filter(
                enrollment_date__range=[
                    start_date,
                    end_date
                ]
            )

        total_billing = (
            enrollments.aggregate(
                total=Sum("final_fee")
            )["total"]
            or 0
        )

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

        total_outstanding = (
            total_billing
            - total_collection
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
        overall_billing += total_billing
        overall_collection += total_collection
        overall_outstanding += total_outstanding
        overall_active_students += active_students

        branch_item = {
            "branch": branch_name,
            "total_enquiries": total_enquiries,
            "converted": converted,
            "admissions": total_admissions,
            "conversion_rate": conversion_rate,
            "active_students": active_students,
        }

        if can_view_financials:
            branch_item.update(
                {
                    "billing": total_billing,
                    "collection": total_collection,
                    "outstanding": total_outstanding,
                }
            )

        branch_data.append(branch_item)

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
            or item.get("collection", 0) > 0
        )
    ]

    if active_branch_data:

        best_branch = max(
            active_branch_data,
            key=lambda x: (
                x["admissions"],
                x.get("collection", 0),
                x["conversion_rate"]
            )
        )

        attention_branch = min(
            active_branch_data,
            key=lambda x: (
                x["admissions"],
                x.get("collection", 0),
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

    context = {
        "branch_data": branch_data,
        "overall_enquiries": overall_enquiries,
        "overall_converted": overall_converted,
        "overall_admissions": overall_admissions,
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
        "is_admin": admin_access,
        "can_view_financials": can_view_financials,
    }

    if can_view_financials:
        context.update(
            {
                "overall_billing": overall_billing,
                "overall_collection": overall_collection,
                "overall_outstanding": overall_outstanding,
            }
        )

    return render(
        request,
        "core/branch_dashboard.html",
        context,
    )


# ============================================================
# REPORTS DASHBOARD
# ============================================================

@login_required
def reports_dashboard(request):

    # Office staff must not access reports or financial analytics.
    if not request.user.is_superuser:
        try:
            viewer_profile = request.user.staff_profile
        except StaffProfile.DoesNotExist:
            auth_logout(request)
            return redirect("staff_login")

        if viewer_profile.designation.strip().lower() != "branch head":
            return redirect("branch_dashboard")

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

    # --------------------------------------------------------
    # ENROLLMENTS
    # --------------------------------------------------------

    enrollments = (
        Enrollment.objects
        .select_related(
            "student",
            "student__admission",
            "course",
        )
        .prefetch_related(
            "fee_payments"
        )
        .filter(
            status="active"
        )
        .order_by(
            "enrollment_date",
            "id",
        )
    )

    if branch_filter:

        enrollments = enrollments.filter(
            branch__iexact=branch_filter
        )

    if search:

        enrollments = enrollments.filter(
            Q(student__name__icontains=search)
            |
            Q(student__student_id__icontains=search)
            |
            Q(student__mobile__icontains=search)
            |
            Q(course__title__icontains=search)
            |
            Q(enrollment_number__icontains=search)
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

    for enrollment in enrollments:

        student = enrollment.student

        total_fee = (
            enrollment.final_fee
            or 0
        )

        paid_fee = sum(
            payment.amount
            for payment in enrollment.fee_payments.all()
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

            enrollment_date = (
                enrollment.enrollment_date
            )

            if enrollment_date:

                if hasattr(
                    enrollment_date,
                    "date"
                ):
                    enrollment_date = (
                        enrollment_date.date()
                    )

                next_due_date = (
                    enrollment_date
                    + timedelta(days=31)
                )

                days_remaining = (
                    next_due_date
                    - today
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
            and
            due_key != status_filter
        ):
            continue

        admission = getattr(
            student,
            "admission",
            None
        )

        due_rows.append(
            {
                "student": student,
                "student_name": (
                    student.name
                    or "-"
                ),
                "mobile": (
                    student.mobile
                    or "-"
                ),
                "admission": admission,
                "admission_number": (
                    admission.admission_number
                    if admission
                    else "-"
                ),
                "enrollment": enrollment,
                "enrollment_number": (
                    enrollment.enrollment_number
                    or "-"
                ),
                "course": (
                    enrollment.course.title
                    if enrollment.course
                    else "-"
                ),
                "branch": (
                    enrollment.branch
                    or student.branch
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

    due_rows.sort(
        key=lambda row: (
            row["balance_fee"] <= 0,
            row["next_due_date"] is None,
            row["next_due_date"] or today,
            row["student_name"],
            row["course"],
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

            existing = Attendance.objects.filter(
                student=student,
                attendance_date=attendance_date,
            ).first()

            if existing:
                current_remarks = existing.remarks or ""

                if (
                    existing.status == status_value
                    and current_remarks == remarks
                ):
                    continue

                existing.status = status_value
                existing.branch = student.branch or ""
                existing.course = student.course
                existing.remarks = remarks
                existing.marked_by = request.user
                existing.source = "admin" if admin_access else "staff"
                existing.save()

            else:
                Attendance.objects.create(
                    student=student,
                    attendance_date=attendance_date,
                    status=status_value,
                    branch=student.branch or "",
                    course=student.course,
                    remarks=remarks,
                    marked_by=request.user,
                    source="admin" if admin_access else "staff",
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
def get_client_ip(request):
    forwarded_for = request.META.get(
        "HTTP_X_FORWARDED_FOR",
        ""
    )

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


def create_staff_login_log(
    request,
    entered_username,
    status,
    reason,
    user=None,
    branch="",
    latitude=None,
    longitude=None,
    distance_meters=None,
):
    StaffLoginLog.objects.create(
        user=user,
        entered_username=entered_username,
        branch=branch,
        status=status,
        reason=reason,
        latitude=latitude,
        longitude=longitude,
        distance_meters=distance_meters,
        ip_address=get_client_ip(request),
        user_agent=request.META.get(
            "HTTP_USER_AGENT",
            ""
        )[:1000],
    )


def staff_login(request):
    if request.user.is_authenticated:
        if is_admin_user(request.user):
            return redirect("management_dashboard")
        if request.user.is_staff:
            branch = get_user_branch(request.user)
            if branch:
                return redirect("branch_dashboard")
            auth_logout(request)
            return render(
                request,
                "core/staff_login.html",
                {"error": "Branch is not assigned to this staff account."},
            )
        auth_logout(request)

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        latitude_value = request.POST.get("latitude", "").strip()
        longitude_value = request.POST.get("longitude", "").strip()

        if not username or not password:
            create_staff_login_log(
                request=request,
                entered_username=username,
                status="denied",
                reason="Username or password missing.",
            )
            return render(
                request,
                "core/staff_login.html",
                {
                    "error": "Please enter username and password.",
                    "entered_username": username,
                },
            )

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is None:
            create_staff_login_log(
                request=request,
                entered_username=username,
                status="denied",
                reason="Invalid username or password.",
            )
            return render(
                request,
                "core/staff_login.html",
                {
                    "error": "Invalid username or password.",
                    "entered_username": username,
                },
            )

        if not user.is_active:
            create_staff_login_log(
                request=request,
                entered_username=username,
                status="denied",
                reason="User account is inactive.",
                user=user,
            )
            return render(
                request,
                "core/staff_login.html",
                {
                    "error": "This account is inactive.",
                    "entered_username": username,
                },
            )

        if not (user.is_staff or user.is_superuser):
            create_staff_login_log(
                request=request,
                entered_username=username,
                status="denied",
                reason="User is not authorized as staff.",
                user=user,
            )
            return render(
                request,
                "core/staff_login.html",
                {
                    "error": "You are not authorized as staff.",
                    "entered_username": username,
                },
            )

        if is_admin_user(user):
            login(request, user)
            create_staff_login_log(
                request=request,
                entered_username=username,
                status="success",
                reason="Administrator login successful.",
                user=user,
                branch="head_office",
            )
            return redirect("management_dashboard")

        try:
            profile = user.staff_profile
        except StaffProfile.DoesNotExist:
            create_staff_login_log(
                request=request,
                entered_username=username,
                status="denied",
                reason="Staff profile is not assigned.",
                user=user,
            )
            return render(
                request,
                "core/staff_login.html",
                {
                    "error": "Staff profile is not assigned to this account.",
                    "entered_username": username,
                },
            )

        if not profile.is_active:
            create_staff_login_log(
                request=request,
                entered_username=username,
                status="denied",
                reason="Staff profile is inactive.",
                user=user,
                branch=profile.branch,
            )
            return render(
                request,
                "core/staff_login.html",
                {
                    "error": "This staff profile is inactive.",
                    "entered_username": username,
                },
            )

        login_latitude = None
        login_longitude = None
        login_distance = None

        if profile.requires_location_login:
            if not latitude_value or not longitude_value:
                create_staff_login_log(
                    request=request,
                    entered_username=username,
                    status="denied",
                    reason="Location permission was not provided.",
                    user=user,
                    branch=profile.branch,
                )
                return render(
                    request,
                    "core/staff_login.html",
                    {
                        "error": "Location permission is required. Please allow location and login again.",
                        "entered_username": username,
                    },
                )

            try:
                login_latitude = float(latitude_value)
                login_longitude = float(longitude_value)
                if not (
                    -90 <= login_latitude <= 90
                    and -180 <= login_longitude <= 180
                ):
                    raise ValueError
            except (TypeError, ValueError):
                create_staff_login_log(
                    request=request,
                    entered_username=username,
                    status="denied",
                    reason="Invalid GPS coordinates received.",
                    user=user,
                    branch=profile.branch,
                )
                return render(
                    request,
                    "core/staff_login.html",
                    {
                        "error": "Invalid location received. Please refresh and try again.",
                        "entered_username": username,
                    },
                )

            branch_location = (
                BranchLocation.objects.filter(is_active=True)
                .filter(
                    Q(branch_name__iexact=profile.branch)
                    | Q(branch_name__iexact=profile.get_branch_display())
                )
                .first()
            )

            if not branch_location:
                create_staff_login_log(
                    request=request,
                    entered_username=username,
                    status="denied",
                    reason="Assigned branch GPS location is not configured.",
                    user=user,
                    branch=profile.branch,
                    latitude=login_latitude,
                    longitude=login_longitude,
                )
                return render(
                    request,
                    "core/staff_login.html",
                    {
                        "error": "Branch location is not configured. Please contact the administrator.",
                        "entered_username": username,
                    },
                )

            login_distance = calculate_distance_meters(
                login_latitude,
                login_longitude,
                branch_location.latitude,
                branch_location.longitude,
            )

            if login_distance > branch_location.radius_meters:
                create_staff_login_log(
                    request=request,
                    entered_username=username,
                    status="denied",
                    reason="Login attempted outside assigned branch radius.",
                    user=user,
                    branch=profile.branch,
                    latitude=login_latitude,
                    longitude=login_longitude,
                    distance_meters=round(login_distance, 2),
                )
                return render(
                    request,
                    "core/staff_login.html",
                    {
                        "error": "Login is allowed only from your assigned branch location.",
                        "entered_username": username,
                    },
                )

        login(request, user)
        request.session["staff_location_verified"] = bool(
            profile.requires_location_login
        )
        request.session["staff_verified_branch"] = profile.branch

        if profile.requires_location_login:
            request.session.set_expiry(60 * 60 * 8)

        create_staff_login_log(
            request=request,
            entered_username=username,
            status="success",
            reason="Staff login successful.",
            user=user,
            branch=profile.branch,
            latitude=login_latitude,
            longitude=login_longitude,
            distance_meters=(
                round(login_distance, 2)
                if login_distance is not None
                else None
            ),
        )

        return redirect("branch_dashboard")

    return render(request, "core/staff_login.html")


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

    # Office staff must not access staff performance or financial data.
    if not request.user.is_superuser:
        try:
            viewer_profile = request.user.staff_profile
        except StaffProfile.DoesNotExist:
            auth_logout(request)
            return redirect("staff_login")

        if viewer_profile.designation.strip().lower() != "branch head":
            return redirect("branch_dashboard")

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

    host = request.get_host().split(":")[0].lower()

    if host in {
        "maharashtracomputer.com",
        "www.maharashtracomputer.com",
    }:
        from local_site.views import local_home
        return local_home(request)

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
        .prefetch_related(
            "streams"
        )
        .order_by(
            "display_order",
            "title"
        )
    )

    trending_courses = (
        Course.objects
        .filter(
            is_active=True,
            is_trending=True
        )
        .prefetch_related(
            "streams"
        )
        .order_by(
            "display_order",
            "title"
        )
    )

    streams = (
        Stream.objects
        .filter(
            is_active=True
        )
        .order_by(
            "display_order",
            "name"
        )
    )

    return render(
        request,
        "courses.html",
        {
            "courses": courses,
            "trending_courses": trending_courses,
            "streams": streams,
            "total_courses": courses.count(),
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

    # --------------------------------------------------------
    # CAREER KIT STATUS
    # --------------------------------------------------------

    enquiries = enquiries.annotate(
        career_profile_id=Max(
            "career_profiles__id"
        ),
        completed_aptitude_count=Count(
            "career_profiles__aptitude_attempts",
            filter=Q(
                career_profiles__aptitude_attempts__status=(
                    "completed"
                )
            ),
            distinct=True,
        ),
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
# DELETE DUPLICATE / DUMMY ADMISSION
# ============================================================

@login_required
def delete_admission(request, admission_id):

    if not request.user.is_superuser:
        messages.error(
            request,
            "Only Super Admin can delete admissions."
        )
        return redirect("admission_list")

    if request.method != "POST":
        return redirect("admission_list")

    admission = get_object_or_404(
        Admission,
        id=admission_id
    )

    admission_number = admission.admission_number
    admission_db_id = admission.id

    admission.delete()

    messages.success(
        request,
        f"Admission {admission_number} "
        f"(ID {admission_db_id}) deleted successfully."
    )

    return redirect("admission_list")



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
# ============================================================
# ADD FEE PAYMENT - ENROLLMENT WISE
# ============================================================

@user_passes_test(
    staff_or_admin,
    login_url="staff_login"
)
def add_enrollment_fee_payment(
    request,
    enrollment_id
):

    enrollment = get_object_or_404(
        Enrollment.objects.select_related(
            "student",
            "course",
            "student__admission",
        ),
        id=enrollment_id
    )

    student = enrollment.student

    # --------------------------------------------------------
    # BRANCH PERMISSION
    # --------------------------------------------------------

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
            (enrollment.branch or student.branch or "")
            .strip()
            .lower()
            !=
            user_branch.strip().lower()
        ):

            return redirect(
                "student_list"
            )

    # --------------------------------------------------------
    # PAYMENT ALREADY COMPLETE
    # --------------------------------------------------------

    if enrollment.balance_fee <= 0:

        if student.admission:

            return redirect(
                "admission_detail",
                admission_id=student.admission.id
            )

        return redirect(
            "student_list"
        )

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    if request.method == "POST":

        form = FeePaymentForm(
            request.POST
        )

        if form.is_valid():

            payment = form.save(
                commit=False
            )

            payment.student = student
            payment.enrollment = enrollment
            payment.collected_by = request.user

            if payment.amount > enrollment.balance_fee:

                form.add_error(
                    "amount",
                    (
                        "Payment cannot be greater "
                        "than enrollment balance."
                    )
                )

            else:

                payment.save()

                if student.admission:

                    return redirect(
                        "admission_detail",
                        admission_id=student.admission.id
                    )

                return redirect(
                    "fee_payment_list"
                )

    else:

        form = FeePaymentForm()

    return render(
        request,
        "core/add_enrollment_fee_payment.html",
        {
            "student": student,
            "enrollment": enrollment,
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
# ============================================================
# ADD NEW COURSE / STUDENT ENROLLMENT
# ============================================================

@user_passes_test(
    staff_or_admin,
    login_url="staff_login"
)
def add_student_enrollment(
    request,
    student_id
):

    student = get_object_or_404(
        Student,
        id=student_id
    )

    # --------------------------------------------------------
    # BRANCH PERMISSION
    # --------------------------------------------------------

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
            !=
            user_branch.strip().lower()
        ):

            return redirect(
                "student_list"
            )

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    if request.method == "POST":

        form = EnrollmentForm(
            request.POST
        )

        if form.is_valid():

            enrollment = form.save(
                commit=False
            )

            enrollment.student = student
            enrollment.created_by = request.user

            # Branch staff cannot move enrollment
            # to another branch manually.
            if not request.user.is_superuser:

                enrollment.branch = (
                    get_user_branch(
                        request.user
                    )
                )

            elif not enrollment.branch:

                enrollment.branch = (
                    student.branch
                )

            enrollment.save()

            # ------------------------------------------------
            # INITIAL PAYMENT
            # ------------------------------------------------

            initial_payment = (
                form.cleaned_data.get(
                    "initial_payment"
                )
                or 0
            )

            payment_mode = (
                form.cleaned_data.get(
                    "payment_mode"
                )
                or ""
            )

            if initial_payment > 0:

                FeePayment.objects.create(
                    student=student,
                    enrollment=enrollment,
                    amount=initial_payment,
                    payment_mode=payment_mode,
                    remarks=(
                        "Initial payment for "
                        f"{enrollment.course.title} "
                        f"({enrollment.enrollment_number})"
                    ),
                    collected_by=request.user,
                )

            return redirect(
                "admission_detail",
                admission_id=student.admission.id
            )

    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------

    else:

        initial_data = {
            "branch": student.branch,
            "status": "active",
        }

        form = EnrollmentForm(
            initial=initial_data
        )

    return render(
    request,
    "core/add_student_enrollment.html",
    {
        "student": student,
        "form": form,
        "course_fees": {
            str(course.id): str(course.fee or 0)
            for course in Course.objects.all()
        },
    }
)

# ============================================================
# MONTHLY BRANCH CLOSING
# ============================================================

CLOSING_BRANCHES = {
    "kharghar": "Kharghar",
    "panvel": "Panvel",
    "koperkhairane": "Koperkhairane",
    "kamothe": "Kamothe",
    "ghansoli": "Ghansoli",
    "nerul": "Nerul",
    "head_office": "Head Office",
}


def _can_manage_branch_closing(
    user,
    branch
):

    if is_admin_user(user):
        return True

    user_branch = get_user_branch(user)

    if not user_branch:
        return False

    if (
        user_branch.strip().lower()
        != branch.strip().lower()
    ):
        return False

    try:
        profile = user.staff_profile
    except StaffProfile.DoesNotExist:
        return False

    return profile.is_active


def _monthly_crm_figures(
    branch,
    year,
    month
):

    start_date = datetime(
        year,
        month,
        1
    ).date()

    last_day = calendar.monthrange(
        year,
        month
    )[1]

    end_date = datetime(
        year,
        month,
        last_day
    ).date()

    # --------------------------------------------------------
    # ADMISSIONS
    # --------------------------------------------------------

    admissions_count = (
        Admission.objects.filter(
            branch__iexact=branch,
            admission_date__range=[
                start_date,
                end_date,
            ]
        ).count()
    )

    # --------------------------------------------------------
    # BILLING
    # --------------------------------------------------------

    billing_amount = (
        Enrollment.objects.filter(
            branch__iexact=branch,
            enrollment_date__range=[
                start_date,
                end_date,
            ]
        ).aggregate(
            total=Sum("final_fee")
        )["total"]
        or Decimal("0.00")
    )

    # --------------------------------------------------------
    # COLLECTION
    # --------------------------------------------------------

    payments = FeePayment.objects.filter(
        payment_date__range=[
            start_date,
            end_date,
        ]
    ).filter(
        Q(
            enrollment__branch__iexact=branch
        )
        |
        Q(
            enrollment__isnull=True,
            student__branch__iexact=branch
        )
    )

    collection_amount = (
        payments.aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    # --------------------------------------------------------
    # DAILY EXPENSES
    # --------------------------------------------------------

    daily_expense_rows = (
        DailyBranchExpense.objects
        .filter(
            branch__iexact=branch,
            expense_date__range=[
                start_date,
                end_date,
            ],
            is_cancelled=False,
        )
        .values(
            "category__code"
        )
        .annotate(
            total=Sum("amount")
        )
    )

    expense_by_code = {
        row["category__code"]: (
            row["total"]
            or Decimal("0.00")
        )
        for row in daily_expense_rows
    }

    def expense_total(code):

        return expense_by_code.get(
            code,
            Decimal("0.00")
        )

    other_expense_amount = sum(
        [
            expense_total(
                "repairs_maintenance"
            ),
            expense_total(
                "refreshment"
            ),
            expense_total(
                "professional_fee"
            ),
            expense_total(
                "other"
            ),
        ],
        Decimal("0.00")
    )

    return {
        "admissions_count": (
            admissions_count
        ),
        "billing_amount": (
            billing_amount
        ),
        "collection_amount": (
            collection_amount
        ),
        "rent_expense": expense_total(
            "office_rent"
        ),
        "electricity_expense": expense_total(
            "electricity"
        ),
        "staff_salary_expense": expense_total(
            "staff_salary"
        ),
        "government_fee_expense": expense_total(
            "government_fee"
        ),
        "computer_maintenance_expense": expense_total(
            "computer_maintenance"
        ),
        "internet_expense": expense_total(
            "internet"
        ),
        "mobile_recharge_expense": expense_total(
            "mobile_recharge"
        ),
        "advertisement_expense": expense_total(
            "advertisement"
        ),
        "stationery_expense": expense_total(
            "stationery"
        ),
        "housekeeping_expense": expense_total(
            "housekeeping"
        ),
        "travelling_expense": expense_total(
            "travelling"
        ),
        "miscellaneous_expense": expense_total(
            "miscellaneous"
        ),
        "other_expense": (
            other_expense_amount
        ),
    }
MONTHLY_EXPENSE_SNAPSHOT_FIELDS = [
    "rent_expense",
    "electricity_expense",
    "staff_salary_expense",
    "government_fee_expense",
    "computer_maintenance_expense",
    "internet_expense",
    "mobile_recharge_expense",
    "advertisement_expense",
    "stationery_expense",
    "housekeeping_expense",
    "travelling_expense",
    "miscellaneous_expense",
    "other_expense",
]


def _apply_monthly_closing_figures(
    closing,
    figures,
    save=True
):

    closing.admissions_count = (
        figures["admissions_count"]
    )

    closing.billing_amount = (
        figures["billing_amount"]
    )

    closing.collection_amount = (
        figures["collection_amount"]
    )

    for field_name in (
        MONTHLY_EXPENSE_SNAPSHOT_FIELDS
    ):

        setattr(
            closing,
            field_name,
            figures[field_name]
        )

    closing.other_expense_description = (
        "Auto-calculated from Daily "
        "Expense Register."
    )

    if save:

        closing.save(
            update_fields=[
                "admissions_count",
                "billing_amount",
                "collection_amount",
                *MONTHLY_EXPENSE_SNAPSHOT_FIELDS,
                "other_expense_description",
                "updated_at",
            ]
        )
@login_required
def monthly_closing_list(request):

    admin_access = is_admin_user(
        request.user
    )

    user_branch = get_user_branch(
        request.user
    )

    if not admin_access and not user_branch:

        auth_logout(request)

        return redirect(
            "staff_login"
        )

    closings = (
        MonthlyBranchClosing.objects
        .select_related(
            "created_by",
            "validated_by",
        )
        .prefetch_related(
            "partner_shares"
        )
    )

    if not admin_access:

        closings = closings.filter(
            branch__iexact=user_branch
        )

    selected_year = request.GET.get(
        "year",
        str(timezone.localdate().year)
    )

    try:
        selected_year = int(
            selected_year
        )
    except ValueError:
        selected_year = (
            timezone.localdate().year
        )

    closings = closings.filter(
        year=selected_year
    )

    return render(
        request,
        "core/monthly_closing_list.html",
        {
            "closings": closings,
            "selected_year": selected_year,
            "is_admin": admin_access,
            "user_branch": user_branch,
            "branches": CLOSING_BRANCHES,
            "current_year": timezone.localdate().year,
            "current_month": timezone.localdate().month,
        }
    )


@login_required
def monthly_closing_edit(
    request,
    branch,
    year,
    month
):

    branch = branch.strip().lower()

    if branch not in CLOSING_BRANCHES:

        messages.error(
            request,
            "Invalid branch."
        )

        return redirect(
            "monthly_closing_list"
        )

    if month < 1 or month > 12:

        messages.error(
            request,
            "Invalid month."
        )

        return redirect(
            "monthly_closing_list"
        )

    if not _can_manage_branch_closing(
        request.user,
        branch
    ):

        messages.error(
            request,
            "You cannot access this branch closing."
        )

        return redirect(
            "branch_dashboard"
        )

    closing, created = (
        MonthlyBranchClosing.objects
        .get_or_create(
            branch=branch,
            year=year,
            month=month,
            defaults={
                "created_by": request.user,
            }
        )
    )

    if closing.status == "draft":

        figures = _monthly_crm_figures(
            branch,
            year,
            month
        )

    _apply_monthly_closing_figures(
            closing,
            figures,
            save=True
        )

    if request.method == "POST":

        if closing.status != "draft":

            messages.error(
                request,
                (
                    "This report has already been "
                    "submitted and cannot be edited."
                )
            )

            return redirect(
                "monthly_closing_edit",
                branch=branch,
                year=year,
                month=month,
            )

        form = MonthlyBranchClosingForm(
            request.POST,
            instance=closing
        )

        if form.is_valid():

            closing = form.save(
                commit=False
            )

            figures = _monthly_crm_figures(
                branch,
                year,
                month
            )

            _apply_monthly_closing_figures(
                closing,
                figures,
                save=False
            )
            action = request.POST.get(
                "action",
                "save"
            )

            if action == "submit":

                partners = (
                    BranchPartner.objects
                    .filter(
                        branch=branch,
                        is_active=True
                    )
                )

                partner_total = (
                    partners.aggregate(
                        total=Sum(
                            "share_percentage"
                        )
                    )["total"]
                    or Decimal("0.00")
                )

                if not partners.exists():

                    messages.error(
                        request,
                        (
                            "Branch partners are not "
                            "configured. Contact Admin."
                        )
                    )

                elif partner_total != Decimal(
                    "100.00"
                ):

                    messages.error(
                        request,
                        (
                            "Active partner shares must "
                            "total exactly 100%."
                        )
                    )

                else:

                    closing.status = (
                        "submitted"
                    )

                    closing.submitted_at = (
                        timezone.now()
                    )

                    closing.save()

                    messages.success(
                        request,
                        (
                            "Monthly report submitted "
                            "to Admin successfully."
                        )
                    )

                    return redirect(
                        "monthly_closing_edit",
                        branch=branch,
                        year=year,
                        month=month,
                    )

            closing.save()

            if action != "submit":

                messages.success(
                    request,
                    "Draft saved successfully."
                )

                return redirect(
                    "monthly_closing_edit",
                    branch=branch,
                    year=year,
                    month=month,
                )

    else:

        form = MonthlyBranchClosingForm(
            instance=closing
        )

    partners = BranchPartner.objects.filter(
        branch=branch,
        is_active=True
    )

    return render(
        request,
        "core/monthly_closing_form.html",
        {
            "form": form,
            "closing": closing,
            "partners": partners,
            "branch_name": (
                CLOSING_BRANCHES[branch]
            ),
            "is_admin": is_admin_user(
                request.user
            ),
        }
    )


@login_required
def monthly_closing_admin_action(
    request,
    closing_id,
    action
):

    if not is_admin_user(request.user):

        messages.error(
            request,
            "Admin access required."
        )

        return redirect(
            "branch_dashboard"
        )

    if request.method != "POST":

        return redirect(
            "monthly_closing_list"
        )

    closing = get_object_or_404(
        MonthlyBranchClosing,
        pk=closing_id
    )

    if action == "validate":

        if closing.status != "submitted":

            messages.error(
                request,
                "Only submitted reports can be validated."
            )

        else:

            partners = BranchPartner.objects.filter(
                branch=closing.branch,
                is_active=True
            )

            total_percentage = (
                partners.aggregate(
                    total=Sum(
                        "share_percentage"
                    )
                )["total"]
                or Decimal("0.00")
            )

            if (
                not partners.exists()
                or total_percentage
                != Decimal("100.00")
            ):

                messages.error(
                    request,
                    (
                        "Active partner shares must "
                        "total exactly 100%."
                    )
                )

            else:

                with transaction.atomic():

                    closing.partner_shares.all().delete()

                    for partner in partners:

                        share_amount = (
                            closing.distributable_profit
                            * partner.share_percentage
                            / Decimal("100.00")
                        ).quantize(
                            Decimal("0.01")
                        )

                        MonthlyPartnerShare.objects.create(
                            closing=closing,
                            partner_name=(
                                partner.partner_name
                            ),
                            share_percentage=(
                                partner.share_percentage
                            ),
                            share_amount=share_amount,
                        )

                    closing.status = "validated"

                    closing.validated_by = (
                        request.user
                    )

                    closing.validated_at = (
                        timezone.now()
                    )

                    closing.save()

                messages.success(
                    request,
                    (
                        "Report validated and partner "
                        "shares calculated."
                    )
                )

    elif action == "close":

        if closing.status != "validated":

            messages.error(
                request,
                (
                    "Validate the report before "
                    "closing the month."
                )
            )

        else:

            closing.status = "closed"

            closing.closed_at = timezone.now()

            closing.save(
                update_fields=[
                    "status",
                    "closed_at",
                    "updated_at",
                ]
            )

            messages.success(
                request,
                (
                    "Month closed successfully. "
                    "The report is now locked."
                )
            )

    return redirect(
        "monthly_closing_edit",
        branch=closing.branch,
        year=closing.year,
        month=closing.month,
    )
# ============================================================
# DAILY BRANCH EXPENSE REGISTER
# ============================================================

def _expense_snapshot(expense):

    return {
        "branch": expense.branch,
        "expense_date": str(
            expense.expense_date
        ),
        "category": expense.category.name,
        "category_id": expense.category_id,
        "amount": str(expense.amount),
        "payment_mode": expense.payment_mode,
        "remark": expense.remark,
        "short_notes": expense.short_notes,
        "bill_receipt": (
            expense.bill_receipt.name
            if expense.bill_receipt
            else ""
        ),
        "is_cancelled": (
            expense.is_cancelled
        ),
        "cancel_reason": (
            expense.cancel_reason
        ),
    }


def _expense_month_is_locked(
    branch,
    expense_date
):

    return MonthlyBranchClosing.objects.filter(
        branch__iexact=branch,
        year=expense_date.year,
        month=expense_date.month,
        status__in=[
            "submitted",
            "validated",
            "closed",
        ]
    ).exists()


def _expense_redirect_url(
    branch,
    year,
    month
):

    return (
        reverse("daily_expense_list")
        + f"?branch={branch}"
        + f"&year={year}"
        + f"&month={month}"
    )


@login_required
def daily_expense_list(request):

    today = timezone.localdate()

    admin_access = is_admin_user(
        request.user
    )

    user_branch = get_user_branch(
        request.user
    )

    if admin_access:

        selected_branch = request.GET.get(
            "branch",
            "kharghar"
        ).strip().lower()

    else:

        if not user_branch:

            auth_logout(request)

            return redirect(
                "staff_login"
            )

        selected_branch = (
            user_branch.strip().lower()
        )

    if selected_branch not in CLOSING_BRANCHES:

        selected_branch = (
            "kharghar"
            if admin_access
            else user_branch.strip().lower()
        )

    try:
        selected_year = int(
            request.GET.get(
                "year",
                today.year
            )
        )

        selected_month = int(
            request.GET.get(
                "month",
                today.month
            )
        )

    except (TypeError, ValueError):

        selected_year = today.year
        selected_month = today.month

    if (
        selected_month < 1
        or selected_month > 12
    ):

        selected_month = today.month

    month_start = datetime(
        selected_year,
        selected_month,
        1
    ).date()

    month_last_day = calendar.monthrange(
        selected_year,
        selected_month
    )[1]

    month_end = datetime(
        selected_year,
        selected_month,
        month_last_day
    ).date()

    month_expenses = (
        DailyBranchExpense.objects
        .select_related(
            "category",
            "created_by",
            "updated_by",
            "cancelled_by",
        )
        .filter(
            branch__iexact=selected_branch,
            expense_date__range=[
                month_start,
                month_end,
            ]
        )
    )

    active_month_expenses = (
        month_expenses.filter(
            is_cancelled=False
        )
    )

    month_total = (
        active_month_expenses.aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    today_total = (
        DailyBranchExpense.objects
        .filter(
            branch__iexact=selected_branch,
            expense_date=today,
            is_cancelled=False,
        )
        .aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    category_summary = (
        active_month_expenses
        .values(
            "category__name",
            "category__code",
        )
        .annotate(
            total=Sum("amount"),
            entry_count=Count("id"),
        )
        .order_by(
            "category__display_order",
            "category__name",
        )
    )

    category_filter = request.GET.get(
        "category",
        ""
    ).strip()

    payment_filter = request.GET.get(
        "payment_mode",
        ""
    ).strip()

    display_expenses = month_expenses

    if category_filter:

        display_expenses = (
            display_expenses.filter(
                category_id=category_filter
            )
        )

    if payment_filter:

        display_expenses = (
            display_expenses.filter(
                payment_mode=payment_filter
            )
        )

    closing = (
        MonthlyBranchClosing.objects
        .filter(
            branch__iexact=selected_branch,
            year=selected_year,
            month=selected_month,
        )
        .first()
    )

    month_is_locked = bool(
        closing
        and closing.status in [
            "submitted",
            "validated",
            "closed",
        ]
    )

    if request.method == "POST":

        if month_is_locked:

            messages.error(
                request,
                (
                    "This month is locked because "
                    "the monthly report has been submitted."
                )
            )

            return redirect(
                _expense_redirect_url(
                    selected_branch,
                    selected_year,
                    selected_month,
                )
            )

        form = DailyBranchExpenseForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            expense = form.save(
                commit=False
            )

            if (
                expense.expense_date.year
                != selected_year
                or expense.expense_date.month
                != selected_month
            ):

                messages.error(
                    request,
                    (
                        "Expense date must be within "
                        "the selected report month."
                    )
                )

            elif _expense_month_is_locked(
                selected_branch,
                expense.expense_date
            ):

                messages.error(
                    request,
                    (
                        "Expenses for this month "
                        "are already locked."
                    )
                )

            else:

                expense.branch = (
                    selected_branch
                )

                expense.created_by = (
                    request.user
                )

                expense.updated_by = (
                    request.user
                )

                expense.save()

                DailyExpenseAuditLog.objects.create(
                    expense=expense,
                    action="created",
                    previous_data={},
                    new_data=_expense_snapshot(
                        expense
                    ),
                    performed_by=request.user,
                )

                messages.success(
                    request,
                    "Daily expense added successfully."
                )

                return redirect(
                    _expense_redirect_url(
                        selected_branch,
                        selected_year,
                        selected_month,
                    )
                )

    else:

        initial_date = (
            today
            if (
                today.year == selected_year
                and today.month == selected_month
            )
            else month_start
        )

        form = DailyBranchExpenseForm(
            initial={
                "expense_date": initial_date,
            }
        )

    return render(
        request,
        "core/daily_expense_list.html",
        {
            "form": form,
            "expenses": display_expenses,
            "month_total": month_total,
            "today_total": today_total,
            "category_summary": category_summary,
            "categories": (
                ExpenseCategory.objects
                .filter(is_active=True)
            ),
            "payment_modes": (
                DailyBranchExpense
                .PAYMENT_MODE_CHOICES
            ),
            "selected_branch": selected_branch,
            "selected_branch_name": (
                CLOSING_BRANCHES[
                    selected_branch
                ]
            ),
            "selected_year": selected_year,
            "selected_month": selected_month,
            "branches": CLOSING_BRANCHES,
            "is_admin": admin_access,
            "month_is_locked": month_is_locked,
            "closing": closing,
            "category_filter": category_filter,
            "payment_filter": payment_filter,
        }
    )


@login_required
def daily_expense_edit(
    request,
    expense_id
):

    expense = get_object_or_404(
        DailyBranchExpense.objects
        .select_related("category"),
        pk=expense_id
    )

    if not _can_manage_branch_closing(
        request.user,
        expense.branch
    ):

        messages.error(
            request,
            "You cannot edit this branch expense."
        )

        return redirect(
            "branch_dashboard"
        )

    if expense.is_cancelled:

        messages.error(
            request,
            "Cancelled expense cannot be edited."
        )

        return redirect(
            _expense_redirect_url(
                expense.branch,
                expense.expense_date.year,
                expense.expense_date.month,
            )
        )

    if _expense_month_is_locked(
        expense.branch,
        expense.expense_date
    ):

        messages.error(
            request,
            (
                "This month is locked. "
                "Expense cannot be edited."
            )
        )

        return redirect(
            _expense_redirect_url(
                expense.branch,
                expense.expense_date.year,
                expense.expense_date.month,
            )
        )

    original_year = (
        expense.expense_date.year
    )

    original_month = (
        expense.expense_date.month
    )

    if request.method == "POST":

        previous_data = _expense_snapshot(
            expense
        )

        form = DailyBranchExpenseForm(
            request.POST,
            request.FILES,
            instance=expense
        )

        if form.is_valid():

            changed_expense = form.save(
                commit=False
            )

            if _expense_month_is_locked(
                expense.branch,
                changed_expense.expense_date
            ):

                messages.error(
                    request,
                    (
                        "The selected expense month "
                        "is already locked."
                    )
                )

            else:

                changed_expense.updated_by = (
                    request.user
                )

                changed_expense.save()

                DailyExpenseAuditLog.objects.create(
                    expense=changed_expense,
                    action="updated",
                    previous_data=previous_data,
                    new_data=_expense_snapshot(
                        changed_expense
                    ),
                    performed_by=request.user,
                )

                messages.success(
                    request,
                    "Expense updated successfully."
                )

                return redirect(
                    _expense_redirect_url(
                        changed_expense.branch,
                        changed_expense.expense_date.year,
                        changed_expense.expense_date.month,
                    )
                )

    else:

        form = DailyBranchExpenseForm(
            instance=expense
        )

    return render(
        request,
        "core/daily_expense_edit.html",
        {
            "form": form,
            "expense": expense,
            "original_year": original_year,
            "original_month": original_month,
        }
    )


@login_required
def daily_expense_cancel(
    request,
    expense_id
):

    expense = get_object_or_404(
        DailyBranchExpense.objects
        .select_related("category"),
        pk=expense_id
    )

    if not _can_manage_branch_closing(
        request.user,
        expense.branch
    ):

        messages.error(
            request,
            "You cannot cancel this branch expense."
        )

        return redirect(
            "branch_dashboard"
        )

    if expense.is_cancelled:

        messages.info(
            request,
            "Expense is already cancelled."
        )

        return redirect(
            _expense_redirect_url(
                expense.branch,
                expense.expense_date.year,
                expense.expense_date.month,
            )
        )

    if _expense_month_is_locked(
        expense.branch,
        expense.expense_date
    ):

        messages.error(
            request,
            (
                "This month is locked. "
                "Expense cannot be cancelled."
            )
        )

        return redirect(
            _expense_redirect_url(
                expense.branch,
                expense.expense_date.year,
                expense.expense_date.month,
            )
        )

    if request.method == "POST":

        form = DailyExpenseCancelForm(
            request.POST
        )

        if form.is_valid():

            previous_data = _expense_snapshot(
                expense
            )

            expense.is_cancelled = True

            expense.cancel_reason = (
                form.cleaned_data[
                    "cancel_reason"
                ]
            )

            expense.cancelled_by = (
                request.user
            )

            expense.cancelled_at = (
                timezone.now()
            )

            expense.updated_by = (
                request.user
            )

            expense.save()

            DailyExpenseAuditLog.objects.create(
                expense=expense,
                action="cancelled",
                previous_data=previous_data,
                new_data=_expense_snapshot(
                    expense
                ),
                performed_by=request.user,
            )

            messages.success(
                request,
                "Expense cancelled successfully."
            )

            return redirect(
                _expense_redirect_url(
                    expense.branch,
                    expense.expense_date.year,
                    expense.expense_date.month,
                )
            )

    else:

        form = DailyExpenseCancelForm()

    return render(
        request,
        "core/daily_expense_cancel.html",
        {
            "form": form,
            "expense": expense,
        }
    )