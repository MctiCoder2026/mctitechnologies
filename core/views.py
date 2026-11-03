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
    StaffAttendance,
    Attendance,
    BranchLocation,

)
from .forms import JobPostForm
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from django.db.models import Q, Sum, Count, Max
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Enrollment
from .forms import EnrollmentForm
from local_site.models import Branch as LocalBranch


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
    OutreachContact,
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

    if student.status != "active":
        return JsonResponse({"success": False,
            "message": "Attendance is available for active students only."},
            status=403)

    latitude = request.POST.get("latitude")
    longitude = request.POST.get("longitude")

    if not latitude or not longitude:
        return JsonResponse({
            "success": False,
            "message": "Location not received."
        }, status=400)

    # Validate GPS coordinates before attendance processing.
    from math import isfinite

    try:
        latitude_value = float(latitude)
        longitude_value = float(longitude)
    except (TypeError, ValueError, OverflowError):
        return JsonResponse({
            "success": False,
            "message": "Invalid GPS coordinates."
        }, status=400)

    if not (
        isfinite(latitude_value)
        and isfinite(longitude_value)
        and -90 <= latitude_value <= 90
        and -180 <= longitude_value <= 180
    ):
        return JsonResponse({
            "success": False,
            "message": "Invalid GPS coordinates."
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

    # Home Branch Only attendance policy
    home_branch = (student.branch or "").strip()

    if not home_branch:
        return JsonResponse({
            "success": False,
            "message": "Your home branch is not assigned. Contact your centre."
        }, status=403)

    matched_branch = BranchLocation.objects.filter(
        branch_name__iexact=home_branch,
        is_active=True
    ).first()

    if not matched_branch:
        return JsonResponse({
            "success": False,
            "message": "Your registered branch GPS is unavailable."
        }, status=403)

    matched_distance = calculate_distance_meters(
        latitude,
        longitude,
        matched_branch.latitude,
        matched_branch.longitude
    )

    if matched_distance > matched_branch.radius_meters:
        matched_branch = None

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


def can_view_business_amounts(user):
    if not user.is_authenticated or not user.is_active:
        return False
    if user.is_superuser:
        return True
    if not user.is_staff:
        return False
    try:
        profile = user.staff_profile
    except StaffProfile.DoesNotExist:
        return False
    accounts = {
        "mcti@ghansoli": "ghansoli",
        "mcti@kamothe": "kamothe",
        "mcti@koperkhairane": "koperkhairane",
        "mcti@nerul": "nerul",
        "mcti@panvel": "panvel",
    }
    expected_branch = accounts.get(user.username.strip().lower())
    return bool(
        profile.is_active
        and expected_branch
        and (profile.branch or "").strip().lower() == expected_branch
    )

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

# ============================================================
# OUTREACH DASHBOARD
# Kharghar / Panvel / Koperkhairane only
# ============================================================

def _normalize_outreach_mobile(value):
    """
    Normalize Indian mobile numbers for duplicate detection.
    Keeps the last 10 digits when country code 91 is present.
    """
    digits = "".join(
        ch for ch in str(value or "")
        if ch.isdigit()
    )

    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[-10:]

    return digits


def _get_outreach_import_branch(request):
    """
    Branch staff: automatically locked to own branch.
    Admin/HO: branch must be explicitly selected.
    """
    allowed_branches = {
        "kharghar",
        "panvel",
        "koperkhairane",
        "kamothe",
        "ghansoli",
        "nerul",
    }

    if is_admin_user(request.user):
        branch = request.POST.get(
            "branch",
            ""
        ).strip().lower()

        if branch in allowed_branches:
            return branch

        return None

    branch = get_user_branch(request.user)

    if branch in allowed_branches:
        return branch

    return None


@login_required(login_url="staff_login")
def outreach_download_template(request):

    allowed_branches = {
        "kharghar",
        "panvel",
        "koperkhairane",
        "kamothe",
        "ghansoli",
        "nerul",
    }

    if (
        not is_admin_user(request.user)
        and get_user_branch(request.user) not in allowed_branches
    ):
        return redirect("branch_dashboard")

    from openpyxl import Workbook

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Outreach Contacts"

    headers = [
        "Name",
        "Mobile",
        "Contact Type",
        "Old Course",
        "Admission Year",
        "Organization",
        "Permission",
        "Notes",
    ]

    sheet.append(headers)

    # Example row
    sheet.append([
        "Example Student",
        "9876543210",
        "Old Student",
        "Advanced Excel",
        "2025",
        "",
        "Unknown",
        "Example only - delete before import",
    ])

    for column in sheet.columns:
        max_length = max(
            len(str(cell.value or ""))
            for cell in column
        )

        sheet.column_dimensions[
            column[0].column_letter
        ].width = min(max_length + 4, 35)

    response = HttpResponse(
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="MCTI_Outreach_Import_Template.xlsx"'

    workbook.save(response)

    return response


@login_required(login_url="staff_login")
def outreach_import_preview(request):

    if request.method != "POST":
        return redirect("outreach_dashboard")

    branch = _get_outreach_import_branch(request)

    if not branch:
        messages.error(
            request,
            "Please select an allowed outreach branch."
        )
        return redirect("outreach_dashboard")

    upload = request.FILES.get("outreach_file")

    if not upload:
        messages.error(
            request,
            "Please select an Excel file."
        )
        return redirect("outreach_dashboard")

    if not upload.name.lower().endswith(".xlsx"):
        messages.error(
            request,
            "Only .xlsx Excel files are supported."
        )
        return redirect("outreach_dashboard")

    from openpyxl import load_workbook
    from datetime import datetime, date
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile
    import uuid

    # Save uploaded Excel temporarily so it survives
    # the Preview -> Confirm Import flow.
    temp_name = (
        "outreach_temp/"
        + str(request.user.id)
        + "_"
        + uuid.uuid4().hex
        + ".xlsx"
    )

    temp_path = default_storage.save(
        temp_name,
        ContentFile(upload.read())
    )

    try:
        workbook = load_workbook(
            default_storage.open(
                temp_path,
                "rb"
            ),
            read_only=True,
            data_only=True
        )
    except Exception:
        if default_storage.exists(temp_path):
            default_storage.delete(temp_path)

        messages.error(
            request,
            "The Excel file could not be read."
        )
        return redirect("outreach_dashboard")

    if "ADMISSION" in workbook.sheetnames:
        sheet = workbook["ADMISSION"]
    else:
        sheet = workbook.active

    rows = sheet.iter_rows(values_only=True)

    try:
        raw_headers = next(rows)
    except StopIteration:
        workbook.close()

        if default_storage.exists(temp_path):
            default_storage.delete(temp_path)

        messages.error(
            request,
            "The Excel file is empty."
        )
        return redirect("outreach_dashboard")

    def clean_header(value):
        return " ".join(
            str(value or "")
            .strip()
            .lower()
            .split()
        )

    headers = [
        clean_header(value)
        for value in raw_headers
    ]

    header_map = {
        header: index
        for index, header in enumerate(headers)
        if header
    }

    def first_header(*names):
        for name in names:
            name = clean_header(name)
            if name in header_map:
                return name
        return None

    name_header = first_header(
        "Name",
        "Candidate Name"
    )

    mobile_header = first_header(
        "Mobile",
        "Contact No.",
        "Contact No",
        "Contact Number"
    )

    date_header = first_header(
        "Date",
        "Admission Date"
    )

    year_header = first_header(
        "Admission Year"
    )

    if not name_header or not mobile_header:
        workbook.close()

        if default_storage.exists(temp_path):
            default_storage.delete(temp_path)

        messages.error(
            request,
            "Excel format not recognized."
        )

        return redirect("outreach_dashboard")

    def raw_cell(row, header_name):

        if not header_name:
            return None

        index = header_map.get(header_name)

        if index is None or index >= len(row):
            return None

        return row[index]

    total_rows = 0
    ready_rows = 0
    invalid_rows = 0
    duplicate_rows = 0

    year_counts = {}

    # Detect duplicates inside the Excel itself too.
    seen_in_file = set()

    for row in rows:

        # Ignore completely blank rows.
        if not any(
            value not in (None, "")
            for value in row
        ):
            continue

        total_rows += 1

        name_value = raw_cell(
            row,
            name_header
        )

        name = str(
            name_value or ""
        ).strip()

        mobile_value = raw_cell(
            row,
            mobile_header
        )

        if mobile_value is None:
            raw_mobile = ""

        elif isinstance(mobile_value, float):
            raw_mobile = str(
                int(mobile_value)
            )

        else:
            raw_mobile = str(
                mobile_value
            ).strip()

        normalized_mobile = (
            _normalize_outreach_mobile(
                raw_mobile
            )
        )

        if (
            not name
            or len(normalized_mobile) != 10
        ):
            invalid_rows += 1
            continue

        duplicate_in_db = (
            OutreachContact.objects
            .filter(
                normalized_mobile=normalized_mobile
            )
            .exists()
        )

        duplicate_in_file = (
            normalized_mobile in seen_in_file
        )

        if duplicate_in_db or duplicate_in_file:
            duplicate_rows += 1

        seen_in_file.add(
            normalized_mobile
        )

        ready_rows += 1

        admission_year = None

        if year_header:

            value = raw_cell(
                row,
                year_header
            )

            if value not in (None, ""):
                try:
                    admission_year = int(
                        float(value)
                    )
                except (ValueError, TypeError):
                    pass

        elif date_header:

            value = raw_cell(
                row,
                date_header
            )

            if isinstance(
                value,
                (datetime, date)
            ):
                admission_year = value.year

            elif value:

                value = str(value).strip()

                for fmt in (
                    "%d/%m/%Y",
                    "%d-%m-%Y",
                    "%Y-%m-%d",
                    "%d/%m/%y",
                    "%d-%m-%y",
                ):
                    try:
                        admission_year = (
                            datetime.strptime(
                                value,
                                fmt
                            ).year
                        )
                        break
                    except ValueError:
                        continue

        year_key = (
            str(admission_year)
            if admission_year
            else "Unknown"
        )

        year_counts[year_key] = (
            year_counts.get(
                year_key,
                0
            )
            + 1
        )

    workbook.close()

    branch_names = {
        "kharghar": "Kharghar",
        "panvel": "Panvel",
        "koperkhairane": "Koperkhairane",
    }

    year_counts = sorted(
        year_counts.items(),
        key=lambda item: (
            item[0] == "Unknown",
            item[0]
        )
    )

    context = {
        "filename": upload.name,
        "temp_path": temp_path,
        "branch": branch,
        "branch_name": branch_names.get(
            branch,
            branch
        ),
        "total_rows": total_rows,
        "ready_rows": ready_rows,
        "invalid_rows": invalid_rows,
        "duplicate_rows": duplicate_rows,
        "year_counts": year_counts,
    }

    return render(
        request,
        "core/outreach_import_preview.html",
        context
    )


@login_required(login_url="staff_login")
def outreach_import(request):

    if request.method != "POST":
        return redirect("outreach_dashboard")

    branch = _get_outreach_import_branch(request)

    if not branch:
        messages.error(
            request,
            "Please select an allowed outreach branch."
        )
        return redirect("outreach_dashboard")

    from django.core.files.storage import default_storage
    from openpyxl import load_workbook
    from datetime import datetime, date

    temp_path = request.POST.get(
        "temp_path",
        ""
    ).strip()

    # Security:
    # Only allow this user's temporary outreach upload.
    expected_prefix = (
        "outreach_temp/"
        + str(request.user.id)
        + "_"
    )

    if (
        not temp_path
        or not temp_path.startswith(expected_prefix)
        or not temp_path.lower().endswith(".xlsx")
        or not default_storage.exists(temp_path)
    ):
        messages.error(
            request,
            "Preview file expired or is invalid. Please upload the Excel again."
        )
        return redirect("outreach_dashboard")

    try:
        file_handle = default_storage.open(
            temp_path,
            "rb"
        )

        workbook = load_workbook(
            file_handle,
            read_only=True,
            data_only=True
        )

    except Exception:

        if default_storage.exists(temp_path):
            default_storage.delete(temp_path)

        messages.error(
            request,
            "The Excel file could not be read."
        )

        return redirect("outreach_dashboard")

    if "ADMISSION" in workbook.sheetnames:
        sheet = workbook["ADMISSION"]
    else:
        sheet = workbook.active

    rows = sheet.iter_rows(
        values_only=True
    )

    try:
        raw_headers = next(rows)

    except StopIteration:

        workbook.close()
        file_handle.close()

        if default_storage.exists(temp_path):
            default_storage.delete(temp_path)

        messages.error(
            request,
            "The Excel file is empty."
        )

        return redirect("outreach_dashboard")

    def clean_header(value):
        return " ".join(
            str(value or "")
            .strip()
            .lower()
            .split()
        )

    headers = [
        clean_header(value)
        for value in raw_headers
    ]

    header_map = {
        header: index
        for index, header in enumerate(headers)
        if header
    }

    def first_header(*names):

        for name in names:

            normalized = clean_header(
                name
            )

            if normalized in header_map:
                return normalized

        return None

    name_header = first_header(
        "Name",
        "Candidate Name"
    )

    mobile_header = first_header(
        "Mobile",
        "Contact No.",
        "Contact No",
        "Contact Number"
    )

    course_header = first_header(
        "Old Course",
        "Admission for Course(s)",
        "Admission for Course",
        "Course"
    )

    year_header = first_header(
        "Admission Year"
    )

    date_header = first_header(
        "Date",
        "Admission Date"
    )

    notes_header = first_header(
        "Notes",
        "Address"
    )

    if not name_header or not mobile_header:

        workbook.close()
        file_handle.close()

        if default_storage.exists(temp_path):
            default_storage.delete(temp_path)

        messages.error(
            request,
            "Excel format not recognized."
        )

        return redirect("outreach_dashboard")

    def raw_cell(row, header_name):

        if not header_name:
            return None

        index = header_map.get(
            header_name
        )

        if (
            index is None
            or index >= len(row)
        ):
            return None

        return row[index]

    def text_cell(row, header_name):

        value = raw_cell(
            row,
            header_name
        )

        if value is None:
            return ""

        return str(value).strip()

    imported = 0
    duplicates = 0
    skipped = 0

    for row in rows:

        # Ignore completely blank rows.
        if not any(
            value not in (None, "")
            for value in row
        ):
            continue

        name = text_cell(
            row,
            name_header
        )

        mobile_value = raw_cell(
            row,
            mobile_header
        )

        if mobile_value is None:
            raw_mobile = ""

        elif isinstance(
            mobile_value,
            float
        ):
            raw_mobile = str(
                int(mobile_value)
            )

        else:
            raw_mobile = str(
                mobile_value
            ).strip()

        normalized_mobile = (
            _normalize_outreach_mobile(
                raw_mobile
            )
        )

        if (
            not name
            or len(normalized_mobile) != 10
        ):
            skipped += 1
            continue

        duplicate_exists = (
            OutreachContact.objects
            .filter(
                normalized_mobile=normalized_mobile
            )
            .exists()
        )

        if duplicate_exists:
            duplicates += 1

        admission_year = None

        if year_header:

            value = raw_cell(
                row,
                year_header
            )

            if value not in (
                None,
                ""
            ):
                try:
                    admission_year = int(
                        float(value)
                    )
                except (
                    ValueError,
                    TypeError
                ):
                    pass

        elif date_header:

            value = raw_cell(
                row,
                date_header
            )

            if isinstance(
                value,
                (datetime, date)
            ):
                admission_year = value.year

            elif value:

                value = str(
                    value
                ).strip()

                for fmt in (
                    "%d/%m/%Y",
                    "%d-%m-%Y",
                    "%Y-%m-%d",
                    "%d/%m/%y",
                    "%d-%m-%y",
                ):

                    try:
                        admission_year = (
                            datetime.strptime(
                                value,
                                fmt
                            ).year
                        )
                        break

                    except ValueError:
                        continue

        OutreachContact.objects.create(
            name=name,
            mobile=raw_mobile,
            normalized_mobile=normalized_mobile,
            branch=branch,
            contact_type="old_student",

            old_course=text_cell(
                row,
                course_header
            ),

            old_admission_year=admission_year,

            permission_status="unknown",

            notes=text_cell(
                row,
                notes_header
            ),

            created_by=request.user,
        )

        imported += 1

    workbook.close()
    file_handle.close()

    # Import successful: remove temporary Excel.
    if default_storage.exists(temp_path):
        default_storage.delete(temp_path)

    messages.success(
        request,
        (
            f"Old student import completed: "
            f"{imported} imported, "
            f"{duplicates} duplicate mobile(s) detected, "
            f"{skipped} skipped."
        )
    )

    return redirect(
        "outreach_dashboard"
    )


@login_required(login_url="staff_login")
def outreach_dashboard(request):

    allowed_branches = [
        "kharghar",
        "panvel",
        "koperkhairane",
        "kamothe",
        "ghansoli",
        "nerul",
    ]

    user_branch = get_user_branch(request.user)

    # HO/Admin can view all outreach branches.
    if is_admin_user(request.user):
        contacts = OutreachContact.objects.filter(
            branch__in=allowed_branches
        )

        selected_branch = request.GET.get(
            "branch",
            ""
        ).strip().lower()

        if selected_branch in allowed_branches:
            contacts = contacts.filter(
                branch=selected_branch
            )

    else:
        # Branch staff can only access their own outreach data.
        if user_branch not in allowed_branches:
            messages.error(
                request,
                "Marketing Outreach is not configured for your branch."
            )
            return redirect("branch_dashboard")

        selected_branch = user_branch

        contacts = OutreachContact.objects.filter(
            branch=user_branch
        )

    search = request.GET.get(
        "search",
        ""
    ).strip()

    status = request.GET.get(
        "status",
        ""
    ).strip()

    contact_type = request.GET.get(
        "contact_type",
        ""
    ).strip()

    if search:
        contacts = contacts.filter(
            Q(name__icontains=search)
            | Q(mobile__icontains=search)
            | Q(email__icontains=search)
            | Q(old_course__icontains=search)
            | Q(organization_name__icontains=search)
        )

    valid_statuses = {
        value
        for value, label in OutreachContact.STATUS_CHOICES
    }

    if status in valid_statuses:
        contacts = contacts.filter(
            status=status
        )

    valid_types = {
        value
        for value, label in OutreachContact.CONTACT_TYPE_CHOICES
    }

    if contact_type in valid_types:
        contacts = contacts.filter(
            contact_type=contact_type
        )

    # Counts respect branch access but intentionally ignore
    # search/status/type filters for dashboard summary cards.
    if is_admin_user(request.user):
        summary_qs = OutreachContact.objects.filter(
            branch__in=allowed_branches
        )

        if selected_branch in allowed_branches:
            summary_qs = summary_qs.filter(
                branch=selected_branch
            )
    else:
        summary_qs = OutreachContact.objects.filter(
            branch=user_branch
        )

    context = {
        "contacts": contacts.order_by("-created_at"),
        "search": search,
        "selected_status": status,
        "selected_type": contact_type,
        "selected_branch": selected_branch,
        "allowed_branches": allowed_branches,
        "status_choices": OutreachContact.STATUS_CHOICES,
        "contact_type_choices": OutreachContact.CONTACT_TYPE_CHOICES,
        "total_contacts": summary_qs.count(),
        "new_count": summary_qs.filter(status="new").count(),
        "contacted_count": summary_qs.filter(status="contacted").count(),
        "followup_count": summary_qs.filter(status="followup").count(),
        "interested_count": summary_qs.filter(status="interested").count(),
        "converted_count": summary_qs.filter(status="converted").count(),
        "is_outreach_admin": is_admin_user(request.user),
    }

    return render(
        request,
        "core/outreach_dashboard.html",
        context
    )




@login_required(login_url="staff_login")
def outreach_convert_to_enquiry(request, contact_id):

    if request.method != "POST":
        return redirect(
            "outreach_contact_detail",
            contact_id=contact_id
        )

    contact = get_object_or_404(
        OutreachContact,
        id=contact_id
    )

    admin_access = is_admin_user(request.user)
    user_branch = get_user_branch(request.user)

    # Branch security
    if not admin_access:
        if (
            not user_branch
            or contact.branch.strip().lower()
            != user_branch.strip().lower()
        ):
            return HttpResponseForbidden(
                "You cannot convert this outreach lead."
            )

    # Already converted through Outreach.
    if contact.converted_enquiry_id:

        contact.status = "converted"
        contact.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        messages.info(
            request,
            (
                "This Marketing Outreach lead is already linked "
                "to an Enquiry."
            )
        )

        return redirect(
            "enquiry_detail",
            enquiry_id=contact.converted_enquiry_id
        )

    # Convert only after branch qualifies the lead
    # and confirms the actual course interest.
    if contact.status not in {"interested", "visit_planned"}:
        messages.error(
            request,
            "Mark the lead as Interested or Visit Planned before converting."
        )
        return redirect(
            "outreach_contact_detail",
            contact_id=contact.id
        )

    if not contact.interested_course_id:
        messages.error(
            request,
            "Select the Interested Course before converting to Enquiry."
        )
        return redirect(
            "outreach_contact_detail",
            contact_id=contact.id
        )

    normalized_mobile = _normalize_outreach_mobile(
        contact.mobile
    )

    # First check whether this person already exists in CRM.
    existing_enquiry = None

    for enquiry in (
        Enquiry.objects
        .filter(mobile__isnull=False)
        .order_by("-created_at")
    ):
        if (
            _normalize_outreach_mobile(enquiry.mobile)
            == normalized_mobile
        ):
            existing_enquiry = enquiry
            break

    if existing_enquiry:

        # Preserve an existing CRM course choice. Only fill it when blank.
        if not existing_enquiry.course_id:
            existing_enquiry.course = contact.interested_course
            existing_enquiry.save(
                update_fields=["course"]
            )

        contact.converted_enquiry = existing_enquiry
        contact.status = "converted"
        contact.save(
            update_fields=[
                "converted_enquiry",
                "status",
                "updated_at",
            ]
        )

        EnquiryActivity.objects.create(
            enquiry=existing_enquiry,
            created_by=request.user,
            activity_type="note",
            message=(
                "Marketing Outreach linked to existing enquiry "
                f"from {contact.get_branch_display()}."
            ),
        )

        messages.success(
            request,
            (
                "Existing CRM Enquiry found. "
                "Marketing Outreach lead linked successfully."
            )
        )

        return redirect(
            "enquiry_detail",
            enquiry_id=existing_enquiry.id
        )

    # No CRM enquiry exists: create a fresh enquiry.
    enquiry = Enquiry.objects.create(
        name=contact.name,
        mobile=contact.mobile,
        email=contact.email or None,
        branch=contact.branch,
        course=contact.interested_course,
        status="new",
        followup_date=contact.followup_date,
        followup_notes=contact.notes or "",
        message=(
            "Converted from Marketing Outreach. "
            f"Source: {contact.source or 'Marketing Outreach'}"
        ),
    )

    EnquiryActivity.objects.create(
        enquiry=enquiry,
        created_by=request.user,
        activity_type="note",
        message=(
            "Created from Marketing Outreach "
            f"#{contact.id} by {request.user.username}."
        ),
    )

    contact.converted_enquiry = enquiry
    contact.status = "converted"
    contact.save(
        update_fields=[
            "converted_enquiry",
            "status",
            "updated_at",
        ]
    )

    messages.success(
        request,
        (
            f"{contact.name} converted to CRM Enquiry "
            f"#{enquiry.id} successfully."
        )
    )

    return redirect(
        "enquiry_detail",
        enquiry_id=enquiry.id
    )



@login_required(login_url="staff_login")
def outreach_contact_detail(request, contact_id):

    contact = get_object_or_404(
        OutreachContact,
        id=contact_id
    )

    admin_access = is_admin_user(request.user)
    user_branch = get_user_branch(request.user)

    # Branch staff can work only on their own outreach leads.
    if not admin_access:
        if (
            not user_branch
            or contact.branch.strip().lower()
            != user_branch.strip().lower()
        ):
            return HttpResponseForbidden(
                "You cannot access this outreach lead."
            )

    valid_statuses = {
        value
        for value, label in OutreachContact.STATUS_CHOICES
    }

    valid_permissions = {
        value
        for value, label in OutreachContact.PERMISSION_CHOICES
    }

    if request.method == "POST":

        status = request.POST.get(
            "status",
            contact.status
        ).strip()

        permission_status = request.POST.get(
            "permission_status",
            contact.permission_status
        ).strip()

        followup_date = request.POST.get(
            "followup_date",
            ""
        ).strip()

        notes = request.POST.get(
            "notes",
            ""
        ).strip()

        interested_course_id = request.POST.get(
            "interested_course",
            ""
        ).strip()

        interested_course = None

        if interested_course_id:
            try:
                interested_course = Course.objects.get(
                    id=interested_course_id,
                    is_active=True,
                )
            except (Course.DoesNotExist, ValueError):
                messages.error(
                    request,
                    "Invalid course selected."
                )
                return redirect(
                    "outreach_contact_detail",
                    contact_id=contact.id
                )

        if status not in valid_statuses:
            messages.error(
                request,
                "Invalid outreach status."
            )
            return redirect(
                "outreach_contact_detail",
                contact_id=contact.id
            )

        if permission_status not in valid_permissions:
            messages.error(
                request,
                "Invalid permission status."
            )
            return redirect(
                "outreach_contact_detail",
                contact_id=contact.id
            )

        contact.status = status
        contact.permission_status = permission_status
        contact.interested_course = interested_course
        contact.notes = notes

        if followup_date:
            try:
                from datetime import datetime
                contact.followup_date = datetime.strptime(
                    followup_date,
                    "%Y-%m-%d"
                ).date()
            except ValueError:
                messages.error(
                    request,
                    "Invalid follow-up date."
                )
                return redirect(
                    "outreach_contact_detail",
                    contact_id=contact.id
                )
        else:
            contact.followup_date = None

        if status in {
            "contacted",
            "followup",
            "interested",
            "visit_planned",
            "not_interested",
        }:
            contact.last_contacted_at = timezone.now()

        contact.save()

        messages.success(
            request,
            "Marketing Outreach lead updated successfully."
        )

        return redirect(
            "outreach_contact_detail",
            contact_id=contact.id
        )

    return render(
        request,
        "core/outreach_contact_detail.html",
        {
            "contact": contact,
            "status_choices": OutreachContact.STATUS_CHOICES,
            "permission_choices": OutreachContact.PERMISSION_CHOICES,
            "courses": Course.objects.filter(
                is_active=True
            ).order_by("title"),
            "is_outreach_admin": admin_access,
        }
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
        ("kharghar", "Kharghar-HO"),
        ("panvel", "Panvel"),
        ("koperkhairane", "Koperkhairane"),
        ("kamothe", "Kamothe"),
        ("ghansoli", "Ghansoli"),
        ("nerul", "Nerul-CO"),
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

    can_view_financials = can_view_business_amounts(request.user)

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



    branch_data = []

    # --------------------------------------------------------
    # OVERALL TOTALS
    # --------------------------------------------------------

    overall_enquiries = 0
    overall_converted = 0
    overall_cohort_converted = 0
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

        cohort_converted = enquiries.filter(
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

        # Conversions in this period, including older enquiries.
        # Count current linked admissions, not historical activity logs.
        converted = (
            admissions.filter(enquiry__isnull=False)
            .order_by()
            .values("enquiry_id")
            .distinct()
            .count()
        )

        active_students = Student.objects.filter(
            branch__iexact=branch_value,
            status="active"
        ).count()

        enrollments = Enrollment.objects.filter(
            branch__iexact=branch_value
        ).exclude(status="cancelled")

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

        from .collection_breakdown import breakdown
        collection_details = breakdown(branch_value, start_date, end_date)
        total_collection = collection_details["collection"]
        total_outstanding = collection_details["outstanding"]

        if total_enquiries > 0:

            conversion_rate = round(
                (
                    cohort_converted
                    / total_enquiries
                ) * 100,
                1
            )

        else:

            conversion_rate = 0

        overall_enquiries += total_enquiries
        overall_converted += converted
        overall_cohort_converted += cohort_converted
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

        if can_view_financials:
            branch_item.update(collection_details)
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
                overall_cohort_converted
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
        "assessment_followup": __import__("career_tools.assessment_report_views", fromlist=["assessment_followup_summary"]).assessment_followup_summary(request.user, start_date, end_date),
        "attendance_action_summary": __import__("core.attendance_dashboard_summary", fromlist=["attendance_action_summary"]).attendance_action_summary(request.user),
        "can_access_outreach": (
            admin_access
            or user_branch in {
                "kharghar",
                "panvel",
                "koperkhairane",
            }
        ),
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

    if not can_view_business_amounts(request.user):
        return redirect("branch_dashboard")
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


    if not can_view_business_amounts(request.user):
        return redirect("branch_dashboard")
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

        if balance_fee <= 0:
            counts["paid"] += 1
            continue

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
                    (max(
                        (p.payment_date for p in enrollment.fee_payments.all()
                         if p.payment_date),
                        default=enrollment_date
                    ))
                    + timedelta(days=30)
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

    eligible_student_ids = (
        Student.objects.filter(
            status="active",
            enrollments__status="active",
            enrollments__enrollment_date__lte=today,
        )
        .values_list("id", flat=True)
        .distinct()
    )

    students = Student.objects.filter(
        id__in=eligible_student_ids
    )

    records = Attendance.objects.filter(
        attendance_date=today,
        student_id__in=eligible_student_ids,
    )

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
        .filter(
            status="active",
            enrollments__status="active",
            enrollments__enrollment_date__lte=attendance_date,
        )
        .distinct()
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



def record_admin_attendance(request, source="admin_login"):
    user = request.user
    if not user.is_authenticated or not user.is_active or not is_admin_user(user):
        return
    try:
        profile = user.staff_profile
    except StaffProfile.DoesNotExist:
        return
    if not profile.is_active:
        return
    StaffAttendance.objects.get_or_create(
        staff=profile,
        attendance_date=timezone.localdate(),
        defaults={
            "first_login_time": timezone.now(),
            "status": "present",
            "branch": profile.branch,
            "ip_address": get_client_ip(request),
            "source": source,
        },
    )

def staff_login(request):
    if request.user.is_authenticated:
        if is_admin_user(request.user):
            record_admin_attendance(request, source="admin_session")
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
            record_admin_attendance(request)
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

        # --------------------------------------------------------
        # SUCCESSFUL STAFF LOGIN
        # Location restriction intentionally disabled.
        # Staff usage is tracked through login history and
        # one attendance record per staff member per day.
        # --------------------------------------------------------

        login(request, user)

        request.session["staff_verified_branch"] = profile.branch

        create_staff_login_log(
            request=request,
            entered_username=username,
            status="success",
            reason="Staff login successful.",
            user=user,
            branch=profile.branch,
        )

        StaffAttendance.objects.get_or_create(
            staff=profile,
            attendance_date=timezone.localdate(),
            defaults={
                "first_login_time": timezone.now(),
                "status": "present",
                "branch": profile.branch,
                "ip_address": get_client_ip(request),
                "source": "staff_login",
            },
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

        # ----------------------------------------------------
        # CAREER KIT RETURN ROUTING
        # ----------------------------------------------------

        career_next = request.session.pop(
            "career_login_next",
            None,
        )

        if career_next == "aptitude":
            return redirect(
                "career_tools:aptitude_test"
            )

        if career_next == "resume":
            return redirect(
                "career_tools:resume_builder"
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
            (payments.first().payment_date if payments.exists()
             else admission_date)
            + timedelta(days=30)
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

def robots_txt(request):
    host = request.get_host().split(":")[0].lower()

    if host in {
        "maharashtracomputer.com",
        "www.maharashtracomputer.com",
    }:
        sitemap_url = "https://maharashtracomputer.com/sitemap.xml"
    else:
        sitemap_url = "https://mctitechnologies.com/sitemap.xml"

    content = (
        "User-agent: *\n"
        "Allow: /\n\n"
        f"Sitemap: {sitemap_url}\n"
    )

    return HttpResponse(content, content_type="text/plain")


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


def franchise(request):
    from .models import FranchiseEnquiry

    success = False

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        mobile = request.POST.get("mobile", "").strip()
        email = request.POST.get("email", "").strip()
        city = request.POST.get("city", "").strip()
        state = request.POST.get("state", "").strip()
        profession_business = request.POST.get(
            "profession_business", ""
        ).strip()
        has_existing_institute = (
            request.POST.get("has_existing_institute") == "yes"
        )
        investment_range = request.POST.get(
            "investment_range",
            "undecided"
        )
        message = request.POST.get("message", "").strip()

        valid_investments = {
            choice[0]
            for choice in FranchiseEnquiry.INVESTMENT_CHOICES
        }

        if investment_range not in valid_investments:
            investment_range = "undecided"

        if name and mobile and city:
            FranchiseEnquiry.objects.create(
                name=name,
                mobile=mobile,
                email=email or None,
                city=city,
                state=state or None,
                profession_business=profession_business or None,
                has_existing_institute=has_existing_institute,
                investment_range=investment_range,
                message=message or None,
            )

            success = True

    return render(
        request,
        "core/franchise.html",
        {
            "success": success,
            "investment_choices": FranchiseEnquiry.INVESTMENT_CHOICES,
        },
    )


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

@login_required(login_url="staff_login")
def push_enquiry_to_outreach(request, enquiry_id):

    if not is_admin_user(request.user):
        return HttpResponseForbidden(
            "Power User / Head Office access required."
        )

    if request.method != "POST":
        return redirect("enquiry_dashboard")

    enquiry = get_object_or_404(
        Enquiry,
        id=enquiry_id
    )

    branch = (
        request.POST.get("branch", "")
        .strip()
        .lower()
    )

    allowed_branches = {
        "kharghar",
        "panvel",
        "koperkhairane",
        "kamothe",
        "ghansoli",
        "nerul",
    }

    if branch not in allowed_branches:
        messages.error(
            request,
            "Please select a valid branch."
        )
        return redirect("enquiry_dashboard")

    normalized_mobile = _normalize_outreach_mobile(
        enquiry.mobile
    )

    if len(normalized_mobile) != 10:
        messages.error(
            request,
            "Lead cannot be pushed because mobile number is invalid."
        )
        return redirect("enquiry_dashboard")

    contact = (
        OutreachContact.objects
        .filter(
            normalized_mobile=normalized_mobile
        )
        .first()
    )

    source_label = f"CRM Enquiry #{enquiry.id}"

    if contact:
        old_branch = contact.branch

        contact.branch = branch

        if not contact.email and enquiry.email:
            contact.email = enquiry.email

        if not contact.source:
            contact.source = source_label
        elif source_label not in contact.source:
            contact.source = (
                f"{contact.source} | {source_label}"
            )[:100]

        contact.notes = (
            (contact.notes or "")
            + (
                f"\nPushed from CRM Enquiry #{enquiry.id} "
                f"by {request.user.username}."
            )
        ).strip()

        contact.save()

        if old_branch != branch:
            messages.success(
                request,
                (
                    f"{enquiry.name} already existed in Marketing Outreach. "
                    f"Lead reassigned to {branch.replace('_', ' ').title()}."
                )
            )
        else:
            messages.info(
                request,
                (
                    f"{enquiry.name} is already in "
                    f"{branch.replace('_', ' ').title()} Marketing Outreach."
                )
            )

    else:
        OutreachContact.objects.create(
            name=enquiry.name,
            mobile=enquiry.mobile,
            normalized_mobile=normalized_mobile,
            email=enquiry.email,
            branch=branch,
            contact_type="other",
            source=source_label,
            permission_status="unknown",
            status="new",
            notes=(
                f"Pushed from CRM Enquiry #{enquiry.id} "
                f"by {request.user.username}."
            ),
            created_by=request.user,
        )

        messages.success(
            request,
            (
                f"{enquiry.name} pushed to "
                f"{branch.replace('_', ' ').title()} Marketing Outreach."
            )
        )

    return redirect("enquiry_dashboard")



# MCTI_ENQUIRY_XLSX_EXPORT_V1
@login_required

# MCTI_ENQUIRY_MONTH_FILTER_V1
def mcti_enquiry_month(request):
    from datetime import datetime
    value = request.GET.get("month", "").strip()
    if not value:
        return ""
    try:
        parsed = datetime.strptime(value, "%Y-%m")
        if parsed.strftime("%Y-%m") == value:
            return value
    except ValueError:
        pass
    return ""

def export_enquiries_excel(request):
    from io import BytesIO
    from django.http import HttpResponse, HttpResponseForbidden
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter
    from django.utils import timezone

    if is_admin_user(request.user):
        qs = Enquiry.objects.all()
    else:
        branch = get_user_branch(request.user)
        if not branch:
            return HttpResponseForbidden("Branch access required.")
        qs = Enquiry.objects.filter(branch__iexact=branch)

    qs = qs.exclude(
        message__icontains="MCTI AI Ready Maharashtra"
    )

    selected_month = mcti_enquiry_month(request)
    if selected_month:
        year, month = map(int, selected_month.split("-"))
        qs = qs.filter(created_at__year=year, created_at__month=month)

    export_type = request.GET.get("view", "active")
    if export_type not in ("active", "closed", "converted", "all"):
        export_type = "active"

    if export_type == "closed":
        qs = qs.filter(status="closed")
    elif export_type == "converted":
        qs = qs.filter(status="converted")
    elif export_type == "active":
        qs = qs.exclude(status__in=("closed", "converted"))

    search = request.GET.get("search", "").strip()
    if search:
        qs = qs.filter(
            Q(name__icontains=search) |
            Q(mobile__icontains=search) |
            Q(email__icontains=search)
        )

    status = request.GET.get("status", "").strip()
    if status:
        qs = qs.filter(status=status)

    assigned = request.GET.get("assigned_to", "").strip()
    if is_admin_user(request.user) and assigned.isdigit():
        qs = qs.filter(assigned_user_id=int(assigned))

    followup = request.GET.get("followup", "").strip()
    today = timezone.localdate()

    if followup == "today":
        qs = qs.filter(followup_date=today).exclude(
            status__in=("converted", "closed")
        )
    elif followup == "overdue":
        qs = qs.filter(followup_date__lt=today).exclude(
            status__in=("converted", "closed")
        )
    elif followup == "upcoming":
        qs = qs.filter(followup_date__gt=today).exclude(
            status__in=("converted", "closed")
        )

    qs = qs.select_related(
        "course", "assigned_user"
    ).order_by("-created_at", "-pk")

    wb = Workbook()
    ws = wb.active
    ws.title = "MCTI Enquiries"

    headers = [
        "Name", "Mobile Number", "Email", "Course",
        "Branch", "Status", "Follow-up Date",
        "Enquiry Date", "Assigned Staff"
    ]
    ws.append(headers)

    for cell in ws[1]:
        cell.fill = PatternFill(
            "solid", fgColor="F97316"
        )
        cell.font = Font(
            bold=True, color="FFFFFF"
        )
        cell.alignment = Alignment(
            horizontal="center"
        )

    for e in qs.iterator(chunk_size=500):
        created = timezone.localtime(e.created_at) if e.created_at else None
        assigned_name = ""
        if e.assigned_user:
            assigned_name = (
                e.assigned_user.get_full_name()
                or e.assigned_user.username
            )

        ws.append([
            e.name or "",
            str(e.mobile or ""),
            e.email or "",
            e.course.title if e.course else "",
            e.branch or "",
            e.get_status_display(),
            str(e.followup_date or ""),
            created.strftime("%d-%m-%Y %H:%M") if created else "",
            assigned_name
        ])

    widths = [28, 20, 32, 35, 20, 18, 20, 24, 28]
    for i, width in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = width

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    response = HttpResponse(
        output.getvalue(),
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )
    filename = (
        f"MCTI_Enquiries_{export_type}_"
        f"{timezone.localdate():%Y%m%d}.xlsx"
    )
    response["Content-Disposition"] = (
        f'attachment; filename="{filename}"'
    )
    response["Cache-Control"] = "private, no-store"
    return response


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
    enquiries = enquiries.exclude(message__icontains="MCTI AI Ready Maharashtra")

    available_months = [
        (d.strftime("%Y-%m"), d.strftime("%B %Y"))
        for d in enquiries.order_by().dates("created_at", "month", order="DESC")
    ]

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
        ).exclude(status__in=("converted", "closed"))

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

    count_queryset = count_queryset.exclude(message__icontains="MCTI AI Ready Maharashtra")

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

    # MCTI_ENQUIRY_ACTIVE_CLOSED_V1
    selected_month = mcti_enquiry_month(request)
    if selected_month:
        year, month = map(int, selected_month.split("-"))
        enquiries = enquiries.filter(
            created_at__year=year,
            created_at__month=month
        )

    enquiry_view = request.GET.get("view", "active")
    # MCTI_ENQUIRY_CONVERTED_TAB_V1
    if enquiry_view not in ("active", "closed", "converted"):
        enquiry_view = "active"

    if enquiry_view == "closed":
        enquiries = enquiries.filter(status="closed")
    elif enquiry_view == "converted":
        enquiries = enquiries.filter(status="converted")
    else:
        enquiries = enquiries.exclude(
            status__in=("closed", "converted")
        )

    from django.core.paginator import Paginator
    enquiry_page = Paginator(
        enquiries.order_by("-created_at", "-pk"), 100
    ).get_page(request.GET.get("page"))
    enquiry_page_params = request.GET.copy()
    enquiry_page_params.pop("page", None)
    enquiries = enquiry_page.object_list

    # MCTI_FOLLOWUP_MONTH_SCOPE_V2
    followup_month_queryset = count_queryset

    if selected_month:
        year, month = map(int, selected_month.split("-"))
        followup_month_queryset = count_queryset.filter(
            created_at__year=year,
            created_at__month=month
        )

    todays_followups = (
        followup_month_queryset
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
        followup_month_queryset
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
        followup_month_queryset
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


    from .enquiry_followup_tools import decorate_leads
    enquiries, todays_followups, overdue_followups = decorate_leads(
        (enquiries, todays_followups, overdue_followups), today
    )

    return render(
        request,
        "core/enquiry_dashboard.html",
        {
            "work_summary": __import__("core.enquiry_followup_tools", fromlist=["work_summary"]).work_summary(request, count_queryset),
            "total": total,
            "new": new,
            "contacted": contacted,
            "followup": followup,
            "converted": converted,
            "closed": closed,
            "enquiries": enquiries,
            "enquiry_page": enquiry_page,
            "selected_month": selected_month,
        "available_months": available_months,
        "enquiry_view": enquiry_view,
            "enquiry_page_query": enquiry_page_params.urlencode(),
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
        if hasattr(enquiry, "admission"):
            messages.error(
                request,
                "This enquiry already has an admission and must remain Converted."
            )
            return redirect("enquiry_dashboard")

        old_status = (
            enquiry.status
        )

        old_status_display = (
            enquiry.get_status_display()
        )

        if request.POST.get("status") == "converted":
            messages.error(
                request,
                "Please use Convert to Admission. "
                "An enquiry can be converted only after creating an admission."
            )
            return redirect("enquiry_dashboard")

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
@transaction.atomic
def enquiry_detail(
    request,
    enquiry_id
):

    enquiry_query = Enquiry.objects.select_related("course", "assigned_user")
    if request.method == "POST":
        enquiry_query = enquiry_query.select_for_update(of=("self",))
    enquiry = get_object_or_404(enquiry_query, id=enquiry_id)

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
                    assignment_form.save(commit=False)
                )

                new_staff = updated_enquiry.assigned_user
                old_branch = enquiry.branch or ""

                if new_staff:
                    new_branch = get_user_branch(new_staff)

                    if not new_branch:
                        messages.error(
                            request,
                            "Selected staff has no active branch. Assignment not saved."
                        )
                        return redirect(
                            "enquiry_detail",
                            enquiry_id=enquiry.id
                        )

                    updated_enquiry.branch = new_branch

                updated_enquiry.save()
                assignment_form.save_m2m()

                if old_branch != (updated_enquiry.branch or ""):
                    EnquiryActivity.objects.create(
                        enquiry=updated_enquiry,
                        activity_type="note",
                        message=(
                            f"Enquiry branch changed from "
                            f"{old_branch or 'Unassigned'} to "
                            f"{updated_enquiry.branch}."
                        ),
                        created_by=request.user
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

            old_status = enquiry.status
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

                updated_enquiry = form.save(commit=False)
                if hasattr(updated_enquiry, "admission"):
                    updated_enquiry.status = "converted"
                    updated_enquiry.followup_date = None
                if updated_enquiry.status in ("converted", "closed"):
                    updated_enquiry.followup_date = None
                else:
                    from datetime import timedelta
                    today = timezone.localdate()
                    selected_date = updated_enquiry.followup_date
                    if selected_date is None or (
                        selected_date == old_followup_date
                        and selected_date <= today
                    ):
                        updated_enquiry.followup_date = today + timedelta(days=2)
                    if updated_enquiry.status == "new":
                        updated_enquiry.status = "followup"
                updated_enquiry.save()
                form.save_m2m()

                if old_status != updated_enquiry.status:
                    EnquiryActivity.objects.create(
                        enquiry=updated_enquiry,
                        activity_type="status",
                        message=(
                            f"Lead status changed from {old_status} "
                            f"to {updated_enquiry.status}."
                        ),
                        created_by=request.user,
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

    career_profile = (
        enquiry.career_profiles
        .order_by("-created_at")
        .first()
    )

    aptitude_attempt = None
    career_recommendation = None

    if career_profile:

        aptitude_attempt = (
            career_profile.aptitude_attempts
            .filter(status="completed")
            .order_by(
                "-completed_at",
                "-id"
            )
            .first()
        )

        career_recommendation = (
            career_profile.career_recommendations
            .prefetch_related("items")
            .order_by("-created_at")
            .first()
        )

    branch_details = (
        LocalBranch.objects
        .filter(
            name__iexact=(
                enquiry.branch or ""
            ).strip(),
            is_active=True
        )
        .first()
    )

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
            "branch_details": branch_details,
            "career_profile": career_profile,
            "aptitude_attempt": aptitude_attempt,
            "career_recommendation": career_recommendation,
            "form": form,
            "assignment_form": assignment_form,
            "activities": activities,
            "is_admin": is_admin_user(
                request.user
            ),
        }
    )


# ============================================================
# DELETE DUMMY / DUPLICATE ENQUIRY
# ============================================================

@login_required
def delete_enquiry(request, enquiry_id):

    if not request.user.is_superuser:
        messages.error(
            request,
            "Only Power User can delete enquiries."
        )
        return redirect(
            "enquiry_detail",
            enquiry_id=enquiry_id
        )

    enquiry = get_object_or_404(
        Enquiry,
        id=enquiry_id
    )

    if request.method != "POST":
        return redirect(
            "enquiry_detail",
            enquiry_id=enquiry.id
        )

    if enquiry.status == "converted":
        messages.error(
            request,
            "Converted enquiries cannot be deleted."
        )
        return redirect(
            "enquiry_detail",
            enquiry_id=enquiry.id
        )

    enquiry_name = enquiry.name
    enquiry_mobile = enquiry.mobile
    enquiry_db_id = enquiry.id

    enquiry.delete()

    messages.success(
        request,
        f"Enquiry {enquiry_name} - {enquiry_mobile} "
        f"(ID {enquiry_db_id}) deleted successfully."
    )

    return redirect("enquiry_dashboard")


# ============================================================
# LOG CALL ACTIVITY
# ============================================================

@login_required
@transaction.atomic
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

        from .enquiry_followup_tools import schedule_action_followup
        schedule_action_followup(enquiry.pk, request.user, "call")
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
@transaction.atomic
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
        return redirect("enquiry_dashboard")

    if request.method == "POST":

        whatsapp_message = (
            request.POST.get("message", "").strip()
        )

        requested_campaign_key = (
            request.POST.get("campaign_key", "").strip()
        )

        allowed_campaign_keys = {
            "scholarshipOffer",
            "kamotheAnniversaryOldEnquiry",
            "kamotheAnniversaryExistingStudent",
        }

        campaign_key = (
            requested_campaign_key
            if requested_campaign_key in allowed_campaign_keys
            else None
        )

        # Campaign tracking is allowed only for Management
        # and participating branches. Nerul is excluded.
        if campaign_key and campaign_key != "scholarshipOffer" and not is_admin_user(request.user):
            try:
                staff_branch = request.user.staff_profile.branch
            except Exception:
                staff_branch = None

            participating_branches = {
                "kharghar",
                "panvel",
                "koperkhairane",
                "kamothe",
                "ghansoli",
                "head_office",
            }

            if staff_branch not in participating_branches:
                campaign_key = None

        EnquiryActivity.objects.create(
            enquiry=enquiry,
            activity_type="whatsapp",
            message=(
                whatsapp_message
                or "WhatsApp conversation initiated with this lead."
            ),
            campaign_key=campaign_key,
            created_by=request.user
        )

        from .enquiry_followup_tools import schedule_action_followup
        schedule_action_followup(
            enquiry.pk, request.user, "whatsapp", campaign_key,
        )

    return redirect(
        "enquiry_detail",
        enquiry_id=enquiry.id
    )

# ============================================================
# LEAD → ADMISSION
# ============================================================

@login_required
@transaction.atomic
def create_admission(
    request,
    enquiry_id
):

    enquiry_query = Enquiry.objects.all()
    if request.method == "POST":
        enquiry_query = enquiry_query.select_for_update()
    enquiry = get_object_or_404(enquiry_query, id=enquiry_id)

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
# MARK ADMISSION REPORTING YEAR
# ============================================================

@login_required
def mark_admission_year(request, admission_id):

    if request.method != "POST":
        return redirect("admission_list")

    # Reporting-year correction is a management-only action.
    if not request.user.is_superuser:
        return redirect("admission_list")

    year = request.POST.get("admission_year", "").strip()

    if not year.isdigit():
        return redirect("admission_list")

    year = int(year)

    if year < 2000 or year > 2100:
        return redirect("admission_list")

    # IMPORTANT:
    # QuerySet.update() intentionally bypasses Admission.save()
    # and post_save signals. Fees, receipts, enrollment and dates
    # remain completely untouched.
    Admission.objects.filter(
        pk=admission_id
    ).update(
        admission_year=year
    )

    return redirect("admission_list")


# ============================================================
# ADMISSION LIST
# ============================================================

@login_required
def admission_list(request):

    search = request.GET.get(
        "search",
        ""
    ).strip()

    admission_year = request.GET.get(
        "year",
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

    if admission_year.isdigit():
        admissions = admissions.filter(
            admission_date__year=int(admission_year)
        )

    admission_month = request.GET.get("month", "").strip()

    if admission_month.isdigit() and 1 <= int(admission_month) <= 12:
        admissions = admissions.filter(
            admission_date__month=int(admission_month)
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
            "admission_year": admission_year,
            "admission_month": admission_month,
            "admission_months": [
                (1, "January"), (2, "February"), (3, "March"),
                (4, "April"), (5, "May"), (6, "June"),
                (7, "July"), (8, "August"), (9, "September"),
                (10, "October"), (11, "November"), (12, "December")
            ],
            "admission_years": [2022, 2024, 2025, 2026],
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


    # BASIC_DETAILS_POWER_USER_LOCK
    if not request.user.is_active or not request.user.is_superuser:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden(
            "Only the power user can edit admission course and fees. "
            "Use Student Basic Details for name, birth date and photo."
        )

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
                # Preserve the student attendance status.

                student.save(
                    update_fields=[
                        "name",
                        "mobile",
                        "email",
                        "course",
                        "branch",
                        "joining_date",
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

    # Current fee position for this course/enrollment.
    # This intentionally uses all payments, so an older receipt also shows
    # the student's latest total paid and outstanding balance.
    if payment.enrollment_id:
        current_total_paid = (
            FeePayment.objects.filter(
                enrollment_id=payment.enrollment_id
            ).aggregate(total=Sum("amount"))["total"]
            or Decimal("0")
        )
        course_total_fee = payment.enrollment.final_fee
    else:
        current_total_paid = (
            FeePayment.objects.filter(
                student=payment.student,
                enrollment__isnull=True
            ).aggregate(total=Sum("amount"))["total"]
            or Decimal("0")
        )
        course_total_fee = (
            payment.student.admission.total_fee
            if payment.student.admission
            else Decimal("0")
        )

    current_balance = max(
        course_total_fee - current_total_paid,
        Decimal("0")
    )

    receipt_courses = list(
        payment.student.enrollments
        .filter(status__in=["active", "completed", "hold"])
        .select_related("course")
        .order_by("id")
    )

    return render(
        request,
        "core/fee_receipt.html",
        {
            "receipt_courses": receipt_courses,
            "payment": payment,
            "current_total_paid": current_total_paid,
            "current_balance": current_balance,
            "approved_corrections": payment.correction_requests.filter(
                status="approved"
            ).order_by("reviewed_at"),
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
            Q(enrollment__branch__iexact=user_branch)
            | Q(enrollment__isnull=True, student__branch__iexact=user_branch)
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

    from datetime import date
    from django.http import HttpResponseBadRequest, HttpResponseForbidden
    from .collection_breakdown import collection_groups

    selected_branch = request.GET.get("branch", "").strip().lower()
    collection_type = request.GET.get("collection_type", "").strip()
    start_raw = request.GET.get("start_date", "").strip()
    end_raw = request.GET.get("end_date", "").strip()
    collection_label = ""
    collection_total = None

    if selected_branch or collection_type or start_raw or end_raw:
        if not selected_branch or selected_branch not in CLOSING_BRANCHES:
            return HttpResponseBadRequest("Choose a valid branch.")
        if not request.user.is_superuser:
            if selected_branch != (user_branch or "").strip().lower():
                return HttpResponseForbidden("Other branch access denied.")
        start = end = None
        if start_raw or end_raw:
            try:
                start = date.fromisoformat(start_raw)
                end = date.fromisoformat(end_raw)
                if start > end:
                    raise ValueError()
            except ValueError:
                return HttpResponseBadRequest("Invalid date range.")
        kind = collection_type or "total"
        if kind not in ("total", "fresh", "old", "other"):
            return HttpResponseBadRequest("Invalid collection type.")
        _, groups = collection_groups(selected_branch, start, end)
        payments = payments.filter(pk__in=groups[kind].values("pk"))
        labels = {
            "total": "Total Collection", "fresh": "Fresh Billing Collection",
            "old": "Previous Billing Collection", "other": "Other / Unlinked Collection",
        }
        collection_label = labels[kind] + " — " + selected_branch.title()
        if start and end:
            collection_label += " | " + start.isoformat() + " to " + end.isoformat()

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
            "collection_label": collection_label,
            "collection_total": payments.aggregate(total=Sum("amount"))["total"] or 0,
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

    # Cancelled enrollment: block direct fee payment access.
    if enrollment.status == "cancelled":
        messages.error(
            request,
            "Fee collection is disabled for Left / Cancelled enrollments."
        )
        if student.admission_id:
            return redirect(
                "admission_detail",
                admission_id=student.admission_id
            )
        return redirect("student_list")

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

            with transaction.atomic():
                enrollment = Enrollment.objects.select_for_update().get(
                    pk=enrollment.pk
                )
                payment.enrollment = enrollment

                if (
                    enrollment.status != "active"
                    or payment.amount <= 0
                    or payment.amount > enrollment.balance_fee
                ):
                    form.add_error(
                        "amount",
                        "Invalid payment or insufficient enrollment balance."
                    )
                else:
                    from decimal import Decimal
                    from django.utils import timezone
                    from .models import EarlyFeeDiscountRequest

                    today = timezone.localdate()
                    balance = enrollment.balance_fee

                    approved = (
                        EarlyFeeDiscountRequest.objects
                        .select_for_update()
                        .filter(
                            enrollment=enrollment,
                            status="approved",
                            applied_amount=0,
                            proposed_payment_date__gte=today,
                            due_date_at_request__gt=today,
                            reviewed_at__date__lte=today,
                        )
                        .order_by("reviewed_at", "id")
                        .first()
                    )

                    # Expire unused approvals after their valid payment window.
                    EarlyFeeDiscountRequest.objects.filter(
                        enrollment=enrollment,
                        status="approved",
                        applied_amount=0,
                        proposed_payment_date__lt=today,
                    ).update(status="expired")

                    EarlyFeeDiscountRequest.objects.filter(
                        enrollment=enrollment,
                        status="approved",
                        applied_amount=0,
                        due_date_at_request__lte=today,
                    ).update(status="expired")

                    discount_applied = False

                    from .early_fee_discount import _due_date
                    current_due = _due_date(enrollment)

                    if (
                        approved
                        and today < current_due
                        and approved.amount < balance
                    ):
                        net_payable = balance - approved.amount

                        if payment.amount == net_payable:
                            enrollment.discount_amount += approved.amount
                            enrollment.final_fee -= approved.amount
                            enrollment.save(
                                update_fields=["discount_amount", "final_fee"]
                            )
                            approved.applied_amount = approved.amount
                            approved.status = "applied"
                            approved.save(update_fields=["applied_amount", "status"])
                            discount_applied = True

                    payment.save()

                    if enrollment.balance_fee <= 0:
                        EarlyFeeDiscountRequest.objects.filter(
                            enrollment=enrollment,
                            status="approved",
                            applied_amount=0,
                        ).update(status="expired")

                    if discount_applied:
                        messages.success(
                            request,
                            "HO-approved early payment discount applied successfully."
                        )

                    if student.admission:
                        return redirect(
                            "admission_detail",
                            admission_id=student.admission.id
                        )

                    return redirect("fee_payment_list")


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
# PUBLIC EMPLOYER JOB SUBMISSION
# ============================================================

def guest_job_post(request):
    from core.forms import GuestJobPostForm

    if request.method == "POST":
        form = GuestJobPostForm(request.POST)

        if form.is_valid():
            job = form.save(commit=False)
            job.submission_source = "guest_employer"
            job.approval_status = "pending"
            job.status = "draft"
            job.posted_by = None
            job.posted_branch = ""
            job.save()
            form.save_m2m()

            return render(
                request,
                "core/guest_job_success.html",
                {"job": job}
            )
    else:
        form = GuestJobPostForm()

    return render(
        request,
        "core/guest_job_post.html",
        {"form": form}
    )



# ============================================================
# GUEST JOB APPROVAL — BRANCH RESTRICTED
# ============================================================

@user_passes_test(staff_or_admin, login_url="staff_login")
def guest_job_approvals(request):

    if request.user.is_superuser:
        branch = None
    else:
        profile = StaffProfile.objects.filter(
            user=request.user,
            is_active=True
        ).first()

        if not profile:
            return HttpResponseForbidden("Staff access required.")

        branch = (
            None if profile.branch == "head_office"
            else profile.branch
        )

    jobs = JobPost.objects.filter(
        submission_source="guest_employer"
    ).select_related(
        "verified_by"
    ).order_by("-created_at")

    if branch:
        jobs = jobs.filter(verification_branch=branch)

    return render(
        request,
        "core/guest_job_approvals.html",
        {"jobs": jobs, "branch": branch}
    )


@user_passes_test(staff_or_admin, login_url="staff_login")
def guest_job_review(request, job_id):
    from django.http import HttpResponseForbidden
    from django.utils import timezone
    from django.db import transaction

    if request.method != "POST":
        return HttpResponseForbidden("POST required.")

    with transaction.atomic():

        job = get_object_or_404(
            JobPost.objects.select_for_update(),
            id=job_id,
            submission_source="guest_employer"
        )

        if not request.user.is_superuser:
            profile = StaffProfile.objects.filter(
                user=request.user,
                is_active=True
            ).first()

            if not profile:
                return HttpResponseForbidden("Staff access required.")

            if (
                profile.branch != "head_office"
                and profile.branch != job.verification_branch
            ):
                return HttpResponseForbidden(
                    "This vacancy belongs to another branch."
                )

        if job.approval_status != "pending":
            return HttpResponseForbidden(
                "This job has already been reviewed."
            )

        action = request.POST.get("action", "").strip()
        remarks = request.POST.get("remarks", "").strip()

        if action not in ("approve", "reject"):
            return HttpResponseForbidden("Invalid action.")

        if not remarks:
            return HttpResponseForbidden(
                "Verification remarks are required."
            )

        if action == "approve":
            job.approval_status = "approved"
            job.status = "active"
        else:
            job.approval_status = "rejected"
            job.status = "draft"

        job.verified_by = request.user
        job.verified_at = timezone.now()
        job.verification_remarks = remarks
        job.save(update_fields=[
            "approval_status",
            "status",
            "verified_by",
            "verified_at",
            "verification_remarks",
            "updated_at",
        ])

        messages.success(
            request,
            "Guest job reviewed successfully."
        )

        return redirect("guest_job_approvals")


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

    can_review_guest_job = False

    if (
        job.submission_source == "guest_employer"
        and job.approval_status == "pending"
    ):
        if request.user.is_superuser:
            can_review_guest_job = True
        else:
            profile = StaffProfile.objects.filter(
                user=request.user,
                is_active=True
            ).first()

            if profile and (
                profile.branch == "head_office"
                or profile.branch == job.verification_branch
            ):
                can_review_guest_job = True

    return render(
        request,
        "core/job_detail.html",
        {
            "job": job,
            "can_review_guest_job": can_review_guest_job,
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
            status="active",
            approval_status="approved"
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

def account_deletion(request):
    return render(request, "core/account_deletion.html")

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
def add_student_enrollment(request, student_id):
    from django.db import transaction
    from django.db.models import Sum
    from .student_reward_points import RewardEnrollmentForm, reward_balance
    from .models import StudentRewardEntry

    student = get_object_or_404(Student, id=student_id)

    if not request.user.is_authenticated or not request.user.is_active:
        return redirect("staff_login")

    if not request.user.is_superuser:
        user_branch = get_user_branch(request.user)
        if not user_branch:
            auth_logout(request)
            return redirect("staff_login")
        if (student.branch or "").strip().lower() != user_branch.strip().lower():
            return redirect("student_list")

    if request.method == "POST":
        with transaction.atomic():
            student = Student.objects.select_for_update().get(pk=student.pk)
            if not request.user.is_superuser:
                if (
                    (student.branch or "").strip().lower()
                    != (get_user_branch(request.user) or "").strip().lower()
                ):
                    return redirect("student_list")

            form = RewardEnrollmentForm(request.POST, student=student)
            if form.is_valid():
                enrollment = form.save(commit=False)
                enrollment.student = student
                enrollment.created_by = request.user

                if not request.user.is_superuser:
                    enrollment.branch = get_user_branch(request.user)
                elif not enrollment.branch:
                    enrollment.branch = student.branch

                enrollment.save()
                points = enrollment.reward_points_used
                if points:
                    StudentRewardEntry.objects.create(
                        student=student,
                        enrollment=enrollment,
                        points=-points,
                        description=(
                            f"Next course discount: {enrollment.enrollment_number}"
                        ),
                        created_by=request.user,
                    )

                initial_payment = form.cleaned_data.get("initial_payment") or 0
                if initial_payment > 0:
                    FeePayment.objects.create(
                        student=student,
                        enrollment=enrollment,
                        amount=initial_payment,
                        payment_mode=form.cleaned_data.get("payment_mode") or "",
                        remarks=(
                            f"Initial payment for {enrollment.course.title} "
                            f"({enrollment.enrollment_number})"
                        ),
                        collected_by=request.user,
                    )

                if student.admission_id:
                    return redirect(
                        "admission_detail", admission_id=student.admission_id
                    )
                return redirect("student_list")
    else:
        form = RewardEnrollmentForm(
            student=student,
            initial={"branch": student.branch, "status": "active"},
        )

    entries = StudentRewardEntry.objects.filter(student=student)
    return render(request, "core/add_student_enrollment.html", {
        "student": student,
        "form": form,
        "reward_balance": reward_balance(student),
        "reward_history": entries[:20],
        "reward_earned": entries.filter(points__gt=0).aggregate(
            total=Sum("points")
        )["total"] or 0,
        "reward_used": -(entries.filter(points__lt=0).aggregate(
            total=Sum("points")
        )["total"] or 0),
        "course_fees": {
            str(course.id): str(course.fee or 0)
            for course in Course.objects.all()
        },
    })

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
        ).exclude(status="cancelled").aggregate(
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


    from .collection_breakdown import breakdown as collection_breakdown
    details = collection_breakdown(branch, start_date, end_date)
    collection_amount = details["collection"]

    return {
        "fresh_collection_snapshot": details["fresh_collection"],
        "old_collection_snapshot": details["old_collection"],
        "other_collection_snapshot": details["other_collection"],
        "fresh_pending_snapshot": details["outstanding"],
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


    # Submitted, validated and closed snapshots must remain unchanged.
    if closing.status != "draft":
        return

    for name in (
        "fresh_collection_snapshot",
        "old_collection_snapshot",
        "other_collection_snapshot",
        "fresh_pending_snapshot",
    ):
        setattr(closing, name, figures[name])

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
                "fresh_collection_snapshot",
                "old_collection_snapshot",
                "other_collection_snapshot",
                "fresh_pending_snapshot",
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

                    from .monthly_share_calculation import calculate_partner_shares
                    partners = list(partners.order_by("pk"))
                    share_amounts = {
                        row["partner"].pk: row["amount"]
                        for row in calculate_partner_shares(closing.cash_profit - closing.reserve_fund_amount, partners)
                    }

                    for partner in partners:

                        share_amount = share_amounts[partner.pk]

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

# ============================================================
# STAFF USAGE & ATTENDANCE REPORT
# Power User / Head Office only
# ============================================================

@login_required
def staff_usage_report(request):
    if request.user.is_authenticated and request.user.is_active and request.user.is_superuser:
        return redirect("team_monitoring")
    return redirect("branch_dashboard")


# ============================================================
# STAFF USAGE & ATTENDANCE REPORT
# Power User / Head Office only
# ============================================================

@login_required
def staff_usage_report(request):
    if request.user.is_authenticated and request.user.is_active and request.user.is_superuser:
        return redirect("team_monitoring")
    return redirect("branch_dashboard")

# ============================================================
# FRANCHISE ENQUIRY MANAGEMENT
# Separate from Student Enquiry CRM
# ============================================================

@login_required
def franchise_enquiry_list(request):
    from .models import FranchiseEnquiry

    # Franchise pipeline is management/admin only.
    if not is_admin_user(request.user):
        return redirect("management_dashboard")

    enquiries = FranchiseEnquiry.objects.all()

    status = request.GET.get("status", "").strip()
    search = request.GET.get("q", "").strip()

    if status:
        enquiries = enquiries.filter(status=status)

    if search:
        enquiries = enquiries.filter(
            Q(name__icontains=search)
            | Q(mobile__icontains=search)
            | Q(city__icontains=search)
            | Q(state__icontains=search)
        )

    context = {
        "enquiries": enquiries,
        "status_choices": FranchiseEnquiry.STATUS_CHOICES,
        "selected_status": status,
        "search": search,
        "total_count": FranchiseEnquiry.objects.count(),
        "new_count": FranchiseEnquiry.objects.filter(
            status="new"
        ).count(),
        "interested_count": FranchiseEnquiry.objects.filter(
            status="interested"
        ).count(),
        "qualified_count": FranchiseEnquiry.objects.filter(
            status="qualified"
        ).count(),
    }

    return render(
        request,
        "core/franchise_enquiry_list.html",
        context
    )

# ============================================================
# FRANCHISE ENQUIRY DETAIL / FOLLOW-UP
# ============================================================

@login_required
def franchise_enquiry_detail(request, enquiry_id):
    from .models import FranchiseEnquiry
    from django.shortcuts import get_object_or_404

    # Franchise pipeline is management/admin only.
    if not is_admin_user(request.user):
        return redirect("management_dashboard")

    enquiry = get_object_or_404(
        FranchiseEnquiry,
        id=enquiry_id
    )

    if request.method == "POST":

        status = request.POST.get(
            "status",
            enquiry.status
        ).strip()

        followup_date = request.POST.get(
            "followup_date",
            ""
        ).strip()

        followup_notes = request.POST.get(
            "followup_notes",
            ""
        ).strip()

        valid_statuses = {
            choice[0]
            for choice in FranchiseEnquiry.STATUS_CHOICES
        }

        if status in valid_statuses:
            enquiry.status = status

        enquiry.followup_date = (
            followup_date or None
        )

        enquiry.followup_notes = (
            followup_notes or None
        )

        enquiry.save(
            update_fields=[
                "status",
                "followup_date",
                "followup_notes",
                "updated_at",
            ]
        )

        return redirect(
            "franchise_enquiry_detail",
            enquiry_id=enquiry.id
        )

    return render(
        request,
        "core/franchise_enquiry_detail.html",
        {
            "enquiry": enquiry,
            "status_choices": FranchiseEnquiry.STATUS_CHOICES,
        }
    )


# ============================================================
# AI READY MAHARASHTRA REPORT — HO / SUPERUSER ONLY
# ============================================================


def _auto_assign_pushed_assessments(contact):
    """Assign eligible completed assessments for a newly pushed marketing lead."""
    from career_tools.models import (
        AssessmentBranchAssignment,
        AssessmentBranchAssignmentLog,
        AptitudeAttempt,
    )
    from assessments.models import AssessmentAttempt, ScholarshipResult

    candidates = []

    if contact.source_type == "ai_ready":
        candidates = list(
            AssessmentAttempt.objects.filter(
                pk=contact.source_record_id,
                status="completed",
                assessment__slug__in=[
                    "ai-ready-maharashtra-2026",
                    "ai-ready-maharashtra-2026-marathi",
                ],
            ).values_list("pk", flat=True)
        )
        kind = "ai"

    elif contact.source_type == "aptitude":
        candidates = list(
            AptitudeAttempt.objects.filter(
                profile_id=contact.source_record_id,
                status="completed",
            ).values_list("pk", flat=True)
        )
        kind = "aptitude"

    elif contact.source_type == "scholarship":
        candidates = list(
            ScholarshipResult.objects.filter(
                pk=contact.source_record_id,
                attempt__status="completed",
                attempt__assessment__slug="mcti-scholarship-test-2026",
            ).values_list("attempt_id", flat=True)
        )
        kind = "scholarship"

    elif contact.source_type == "ssc":
        from assessments.branch_sync import sync_mobile
        return sync_mobile(contact.normalized_mobile or contact.mobile)

    else:
        return 0

    created_count = 0

    for attempt_id in set(candidates):
        assignment, created = AssessmentBranchAssignment.objects.get_or_create(
            kind=kind,
            attempt_id=attempt_id,
            defaults={
                "branch": contact.branch,
                "assigned_by": contact.pushed_by,
            },
        )

        if not created:
            if assignment.branch != contact.branch:
                raise ValueError(
                    f"Assessment {kind}:{attempt_id} already belongs to "
                    f"{assignment.branch}; cannot silently transfer."
                )
            continue

        AssessmentBranchAssignmentLog.objects.create(
            kind=kind,
            attempt_id=attempt_id,
            old_branch="",
            new_branch=contact.branch,
            changed_by=contact.pushed_by,
        )
        created_count += 1

    return created_count


@login_required(login_url="staff_login")
@transaction.atomic
def push_marketing_lead_to_outreach(request, source_type, source_id):

    if not is_admin_user(request.user):
        return HttpResponseForbidden(
            "Only Power User / Head Office can distribute marketing leads."
        )

    if request.method != "POST":
        return redirect("marketing_lead_distribution")

    allowed_branches = {
        "kharghar",
        "panvel",
        "koperkhairane",
        "kamothe",
        "ghansoli",
        "nerul",
    }

    allowed_sources = {
        "ai_ready",
        "aptitude",
        "scholarship",
        "ssc",
    }

    source_type = (source_type or "").strip().lower()
    branch = request.POST.get("branch", "").strip().lower()

    if source_type not in allowed_sources:
        messages.error(request, "Invalid marketing lead source.")
        return redirect("marketing_lead_distribution")

    if branch not in allowed_branches:
        messages.error(request, "Please select a valid branch.")
        return redirect("marketing_lead_distribution")

    # Never create the same source record twice.
    existing = (
        OutreachContact.objects
        .filter(
            contact_type="marketing_lead",
            source_type=source_type,
            source_record_id=source_id,
        )
        .first()
    )

    if existing:
        messages.info(
            request,
            (
                f"{existing.name} is already pushed to "
                f"{existing.get_branch_display()} Marketing Outreach."
            )
        )
        return redirect("marketing_lead_distribution")

    name = ""
    mobile = ""
    email = ""
    source_label = ""
    notes = ""

    # --------------------------------------------------------
    # AI READY
    # --------------------------------------------------------
    if source_type == "ai_ready":
        from assessments.models import AssessmentAttempt

        obj = get_object_or_404(
            AssessmentAttempt.objects.select_related(
                "participant_profile",
                "assessment",
            ),
            id=source_id,
            assessment__slug__in=[
                "ai-ready-maharashtra-2026",
                "ai-ready-maharashtra-2026-marathi",
            ],
        )

        profile = getattr(obj, "participant_profile", None)

        name = obj.participant_name
        mobile = obj.participant_mobile
        email = obj.participant_email or ""
        source_label = "AI Ready Maharashtra"

        details = []
        if profile:
            if profile.city:
                details.append(f"City: {profile.city}")
            if profile.institution_name:
                details.append(
                    f"Institution: {profile.institution_name}"
                )
            if profile.career_interest:
                details.append(
                    f"Initial interest: {profile.career_interest}"
                )

        notes = " | ".join(details)

    # --------------------------------------------------------
    # CAREER / APTITUDE
    # --------------------------------------------------------
    elif source_type == "aptitude":
        from career_tools.models import CareerProfile

        obj = get_object_or_404(
            CareerProfile,
            id=source_id,
        )

        name = obj.full_name
        mobile = obj.mobile
        email = obj.email or ""
        source_label = "Career / Aptitude"

        details = []
        if obj.city:
            details.append(f"City: {obj.city}")
        if obj.career_interest:
            details.append(
                f"Initial interest: {obj.career_interest}"
            )
        if obj.preferred_job_role:
            details.append(
                f"Job role: {obj.preferred_job_role}"
            )

        notes = " | ".join(details)

    # --------------------------------------------------------
    # SCHOLARSHIP
    # --------------------------------------------------------
    elif source_type == "scholarship":
        from assessments.models import ScholarshipResult

        obj = get_object_or_404(
            ScholarshipResult.objects.select_related(
                "attempt",
                "attempt__participant_profile",
            ),
            id=source_id,
            attempt__assessment__slug="mcti-scholarship-test-2026",
        )

        profile = getattr(
            obj.attempt,
            "participant_profile",
            None,
        )

        name = obj.attempt.participant_name
        mobile = obj.attempt.participant_mobile
        email = obj.attempt.participant_email or ""
        source_label = "Scholarship"

        details = [
            f"Scholarship: {obj.scholarship_percentage}%"
        ]

        if obj.selected_course:
            details.append(
                f"Initial course: {obj.selected_course}"
            )

        if profile and profile.city:
            details.append(f"City: {profile.city}")

        notes = " | ".join(details)

    # --------------------------------------------------------
    # SSC PRACTICE
    # --------------------------------------------------------
    elif source_type == "ssc":
        from exam_preparation.models import SSCStudent

        obj = get_object_or_404(
            SSCStudent,
            id=source_id,
        )

        name = obj.full_name
        mobile = obj.mobile
        email = ""
        source_label = "SSC Practice"

        details = []
        if obj.city:
            details.append(f"City: {obj.city}")
        if obj.school_name:
            details.append(f"School: {obj.school_name}")

        notes = " | ".join(details)

    normalized_mobile = _normalize_outreach_mobile(mobile)

    if len(normalized_mobile) != 10:
        messages.error(
            request,
            (
                f"Cannot push {name or 'lead'}: "
                "valid 10-digit mobile number not found."
            )
        )
        return redirect("marketing_lead_distribution")

    contact = OutreachContact.objects.create(
        name=name,
        mobile=mobile,
        normalized_mobile=normalized_mobile,
        email=email or None,
        branch=branch,
        contact_type="marketing_lead",
        source=source_label,
        source_type=source_type,
        source_record_id=source_id,
        pushed_by=request.user,
        pushed_at=timezone.now(),
        permission_status="unknown",
        status="new",
        notes=notes,
        created_by=request.user,
    )

    assigned_count = _auto_assign_pushed_assessments(contact)

    messages.success(
        request,
        (
            f"{contact.name} pushed to "
            f"{contact.get_branch_display()} Marketing Outreach."
        )
    )

    return redirect("marketing_lead_distribution")



@login_required(login_url="staff_login")
def bulk_push_marketing_leads(request):
    """HO-only bulk distribution. Each lead is its own atomic transaction."""
    from django.db import connection, transaction
    from django.views.decorators.http import require_POST
    from assessments.models import AssessmentAttempt, ScholarshipResult
    from career_tools.models import CareerProfile
    from exam_preparation.models import SSCStudent

    if not is_admin_user(request.user):
        return HttpResponseForbidden("HO / Power User only")
    if request.method != "POST":
        return HttpResponseForbidden("POST required")

    branch = request.POST.get("branch", "").strip().lower()
    valid_branches = {"kharghar", "panvel", "koperkhairane", "kamothe", "ghansoli", "nerul"}
    if branch not in valid_branches:
        messages.error(request, "Select a valid destination branch.")
        return redirect("marketing_lead_distribution")

    selected = request.POST.getlist("lead_keys")
    if not selected or len(selected) > 100 or len(set(selected)) != len(selected):
        messages.error(request, "Select 1–100 unique leads.")
        return redirect("marketing_lead_distribution")

    import re
    keys=[]
    for key in selected:
        match=re.fullmatch(r"(ai_ready|aptitude|scholarship|ssc):(\d{1,12})", key)
        if not match or int(match.group(2)) < 1:
            messages.error(request, "Invalid lead selection. Nothing pushed.")
            return redirect("marketing_lead_distribution")
        keys.append((match.group(1), int(match.group(2))))

    counts={"created":0,"skipped":0,"failed":0,"assessments":0}
    for source_type, source_id in keys:
        try:
            with transaction.atomic():
                # Lock per source to prevent concurrent duplicate pushes.
                with connection.cursor() as cursor:
                    cursor.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))", [f"mcti_bulk_lead:{source_type}:{source_id}"])
                if OutreachContact.objects.filter(
                    contact_type="marketing_lead", source_type=source_type, source_record_id=source_id
                ).exists():
                    counts["skipped"] += 1
                    continue

                email=""; notes=""; label=""
                if source_type=="ai_ready":
                    obj=AssessmentAttempt.objects.select_related("participant_profile").get(
                        pk=source_id, assessment__slug__in=["ai-ready-maharashtra-2026","ai-ready-maharashtra-2026-marathi"])
                    name=obj.participant_name; mobile=obj.participant_mobile; email=obj.participant_email or ""
                    label="AI Ready Maharashtra"
                    profile=obj.participant_profile
                    if profile:
                        notes=" | ".join(x for x in [f"City: {profile.city}" if profile.city else "", f"Institution: {profile.institution_name}" if profile.institution_name else "", f"Initial interest: {profile.career_interest}" if profile.career_interest else ""] if x)
                elif source_type=="aptitude":
                    obj=CareerProfile.objects.get(pk=source_id)
                    name=obj.full_name; mobile=obj.mobile; email=obj.email or ""; label="Career / Aptitude"
                    notes=" | ".join(x for x in [f"City: {obj.city}" if obj.city else "", f"Initial interest: {obj.career_interest}" if obj.career_interest else "", f"Job role: {obj.preferred_job_role}" if obj.preferred_job_role else ""] if x)
                elif source_type=="scholarship":
                    obj=ScholarshipResult.objects.select_related("attempt","attempt__participant_profile").get(
                        pk=source_id, attempt__assessment__slug="mcti-scholarship-test-2026")
                    name=obj.attempt.participant_name; mobile=obj.attempt.participant_mobile
                    email=obj.attempt.participant_email or ""; label="Scholarship"
                    details=[f"Scholarship: {obj.scholarship_percentage}%"]
                    if obj.selected_course: details.append(f"Initial course: {obj.selected_course}")
                    profile=obj.attempt.participant_profile
                    if profile and profile.city: details.append(f"City: {profile.city}")
                    notes=" | ".join(details)
                else:
                    obj=SSCStudent.objects.get(pk=source_id)
                    name=obj.full_name; mobile=obj.mobile; label="SSC Practice"
                    notes=" | ".join(x for x in [f"City: {obj.city}" if obj.city else "", f"School: {obj.school_name}" if obj.school_name else ""] if x)

                normalized_mobile=_normalize_outreach_mobile(mobile)
                if len(normalized_mobile)!=10:
                    raise ValueError("Invalid mobile")
                contact=OutreachContact.objects.create(
                    name=name,mobile=mobile,normalized_mobile=normalized_mobile,
                    email=email or None,branch=branch,contact_type="marketing_lead",
                    source=label,source_type=source_type,source_record_id=source_id,
                    pushed_by=request.user,pushed_at=timezone.now(),
                    permission_status="unknown",status="new",notes=notes,created_by=request.user,
                )
                new_assignments=_auto_assign_pushed_assessments(contact)
                counts["created"]+=1
                counts["assessments"]+=new_assignments
        except Exception:
            counts["failed"]+=1
            # Details stay in server logs; avoid exposing personal data in UI.
            import logging
            logging.getLogger(__name__).exception("Bulk marketing push failed: %s:%s",source_type,source_id)

    messages.success(request,
        f"Bulk distribution: {counts['created']} pushed to {branch.title()}, "
        f"{counts['skipped']} already pushed, {counts['failed']} failed; "
        f"{counts['assessments']} assessment assignments created.")
    return redirect("marketing_lead_distribution")


@login_required(login_url="staff_login")
def marketing_lead_distribution(request):
    """
    HO / Power User lead review dashboard.

    Includes campaign / assessment leads only:
    - AI Ready Maharashtra
    - Career / Aptitude
    - Scholarship
    - SSC Practice

    Direct website enquiries are intentionally excluded.
    """

    if not is_admin_user(request.user):
        messages.error(
            request,
            "You do not have permission to access Marketing Lead Distribution."
        )
        return redirect("branch_dashboard")

    from assessments.models import (
        AssessmentAttempt,
        ScholarshipResult,
    )
    from career_tools.models import CareerProfile
    from exam_preparation.models import SSCStudent

    source_filter = request.GET.get("source", "").strip().lower()
    search = request.GET.get("q", "").strip()

    rows = []

    # ---------------------------------------------------------
    # AI READY
    # ---------------------------------------------------------
    if source_filter in ("", "ai_ready"):
        ai_qs = (
            AssessmentAttempt.objects
            .filter(
                assessment__slug__in=[
                    "ai-ready-maharashtra-2026",
                    "ai-ready-maharashtra-2026-marathi",
                ]
            )
            .select_related("participant_profile")
            .order_by("-started_at")
        )

        if search:
            ai_qs = ai_qs.filter(
                Q(participant_name__icontains=search)
                | Q(participant_mobile__icontains=search)
                | Q(participant_email__icontains=search)
                | Q(participant_profile__city__icontains=search)
            )

        for item in ai_qs[:200]:
            profile = getattr(item, "participant_profile", None)

            rows.append({
                "source": "ai_ready",
                "source_label": "AI Ready Maharashtra",
                "source_id": item.id,
                "name": item.participant_name,
                "mobile": item.participant_mobile,
                "email": item.participant_email,
                "city": profile.city if profile else "",
                "preferred_branch": "",
                "detail": item.get_status_display(),
                "created_at": item.started_at,
            })

    # ---------------------------------------------------------
    # CAREER / APTITUDE
    # ---------------------------------------------------------
    if source_filter in ("", "aptitude"):
        career_qs = CareerProfile.objects.all().order_by("-created_at")

        if search:
            career_qs = career_qs.filter(
                Q(full_name__icontains=search)
                | Q(mobile__icontains=search)
                | Q(email__icontains=search)
                | Q(city__icontains=search)
                | Q(career_interest__icontains=search)
            )

        for item in career_qs[:200]:
            rows.append({
                "source": "aptitude",
                "source_label": "Career / Aptitude",
                "source_id": item.id,
                "name": item.full_name,
                "mobile": item.mobile,
                "email": item.email,
                "city": item.city,
                "preferred_branch": item.preferred_branch,
                "detail": item.career_interest,
                "created_at": item.created_at,
            })

    # ---------------------------------------------------------
    # SCHOLARSHIP
    # ---------------------------------------------------------
    if source_filter in ("", "scholarship"):
        scholarship_qs = (
            ScholarshipResult.objects
            .select_related(
                "attempt",
                "attempt__participant_profile",
            )
            .filter(
                attempt__assessment__slug="mcti-scholarship-test-2026"
            )
            .order_by("-created_at")
        )

        if search:
            scholarship_qs = scholarship_qs.filter(
                Q(attempt__participant_name__icontains=search)
                | Q(attempt__participant_mobile__icontains=search)
                | Q(attempt__participant_email__icontains=search)
                | Q(preferred_branch__icontains=search)
            )

        for item in scholarship_qs[:200]:
            profile = getattr(
                item.attempt,
                "participant_profile",
                None
            )

            rows.append({
                "source": "scholarship",
                "source_label": "Scholarship",
                "source_id": item.id,
                "name": item.attempt.participant_name,
                "mobile": item.attempt.participant_mobile,
                "email": item.attempt.participant_email,
                "city": profile.city if profile else "",
                "preferred_branch": item.preferred_branch,
                "detail": f"{item.scholarship_percentage}% Scholarship",
                "created_at": item.created_at,
            })

    # ---------------------------------------------------------
    # SSC PRACTICE
    # ---------------------------------------------------------
    if source_filter in ("", "ssc"):
        ssc_qs = (
            SSCStudent.objects
            .select_related("preferred_branch")
            .order_by("-created_at")
        )

        if search:
            ssc_qs = ssc_qs.filter(
                Q(full_name__icontains=search)
                | Q(mobile__icontains=search)
                | Q(city__icontains=search)
                | Q(school_name__icontains=search)
            )

        for item in ssc_qs[:200]:
            rows.append({
                "source": "ssc",
                "source_label": "SSC Practice",
                "source_id": item.id,
                "name": item.full_name,
                "mobile": item.mobile,
                "email": "",
                "city": item.city,
                "preferred_branch": (
                    item.preferred_branch.branch_name
                    if item.preferred_branch
                    else ""
                ),
                "detail": item.school_name,
                "created_at": item.created_at,
            })

    rows.sort(
        key=lambda row: row["created_at"],
        reverse=True
    )

    rows = rows[:300]

    # Attach current Marketing Outreach routing state.
    # Keyed by source_type + source_record_id so the same source
    # record cannot accidentally be treated as a fresh lead.
    source_ids = {}
    for row in rows:
        source_ids.setdefault(row["source"], []).append(row["source_id"])

    pushed_lookup = {}

    for source_name, record_ids in source_ids.items():
        pushed_contacts = (
            OutreachContact.objects
            .filter(
                contact_type="marketing_lead",
                source_type=source_name,
                source_record_id__in=record_ids,
            )
            .select_related("converted_enquiry")
        )

        for contact in pushed_contacts:
            pushed_lookup[
                (contact.source_type, contact.source_record_id)
            ] = contact

    for row in rows:
        contact = pushed_lookup.get(
            (row["source"], row["source_id"])
        )

        row["outreach_contact"] = contact
        row["is_pushed"] = bool(contact)

    branch_choices = OutreachContact.BRANCH_CHOICES

    source_choices = [
        ("", "All Marketing Leads"),
        ("ai_ready", "AI Ready Maharashtra"),
        ("aptitude", "Career / Aptitude"),
        ("scholarship", "Scholarship"),
        ("ssc", "SSC Practice"),
    ]

    return render(
        request,
        "core/marketing_lead_distribution.html",
        {
            "rows": rows,
            "source_filter": source_filter,
            "search": search,
            "source_choices": source_choices,
            "branch_choices": branch_choices,
        },
    )


def ai_ready_report(request):

    if not is_admin_user(request.user):
        messages.error(
            request,
            "You do not have permission to access the AI Ready Maharashtra report."
        )
        return redirect("branch_dashboard")

    from assessments.models import (
        Assessment,
        AssessmentAttempt,
    )

    assessment = get_object_or_404(
        Assessment,
        slug="ai-ready-maharashtra-2026",
    )

    ai_ready_slugs = [
        "ai-ready-maharashtra-2026",
        "ai-ready-maharashtra-2026-marathi",
    ]

    attempts = (
        AssessmentAttempt.objects
        .filter(
            assessment__slug__in=ai_ready_slugs,
        )
        .select_related(
            "participant_profile",
            "result",
            "certificate",
        )
        .order_by("-started_at")
    )

    search = request.GET.get("search", "").strip()

    if search:
        attempts = attempts.filter(
            Q(participant_name__icontains=search)
            |
            Q(participant_mobile__icontains=search)
            |
            Q(participant_email__icontains=search)
            |
            Q(participant_profile__institution_name__icontains=search)
            |
            Q(participant_profile__district__icontains=search)
            |
            Q(participant_profile__city__icontains=search)
            |
            Q(participant_profile__career_interest__icontains=search)
        )

    status_filter = request.GET.get("status", "").strip()

    if status_filter:
        attempts = attempts.filter(
            status=status_filter
        )

    band_filter = request.GET.get("band", "").strip()

    if band_filter:
        attempts = attempts.filter(
            result__result_band=band_filter
        )

    total = AssessmentAttempt.objects.filter(
        assessment__slug__in=ai_ready_slugs
    ).count()

    completed = AssessmentAttempt.objects.filter(
        assessment__slug__in=ai_ready_slugs,
        status="completed",
    ).count()

    started = AssessmentAttempt.objects.filter(
        assessment__slug__in=ai_ready_slugs,
        status="started",
    ).count()

    certificates = AssessmentAttempt.objects.filter(
        assessment__slug__in=ai_ready_slugs,
        status="completed",
        certificate__is_valid=True,
    ).count()

    return render(
        request,
        "core/ai_ready_report.html",
        {
            "assessment": assessment,
            "attempts": attempts[:200],
            "total": total,
            "completed": completed,
            "started": started,
            "certificates": certificates,
            "search": search,
            "status_filter": status_filter,
            "band_filter": band_filter,
        },
    )


# ============================================================
# PUBLIC COURSE AUTOCOMPLETE
# Used by website enquiry form.
# Returns active courses matching the typed search term.
# ============================================================
def public_course_search(request):
    from django.http import JsonResponse
    from .models import Course

    q = request.GET.get("q", "").strip()

    if len(q) < 2:
        return JsonResponse({"results": []})

    courses = (
        Course.objects
        .filter(is_active=True, title__icontains=q)
        .order_by("display_order", "title")[:12]
    )

    return JsonResponse({
        "results": [
            {"id": course.id, "title": course.title}
            for course in courses
        ]
    })



# ============================================================
# MANAGEMENT - MARKETING ACTIVITY MONITOR
# ============================================================

@login_required
def marketing_activity_dashboard(request):

    if not is_admin_user(request.user):
        return redirect("management_dashboard")

    from django.db.models import Count, Max

    campaign_names = {
        "scholarshipOffer": "Scholarship Offer | 3 Oct Batch",
        "kamotheAnniversaryOldEnquiry":
            "Kamothe 1st Anniversary | Old Enquiry | 2-Day Scholarship",
        "kamotheAnniversaryExistingStudent":
            "Kamothe 1st Anniversary | Existing Student | 7-Day Upgrade",
    }

    campaign_keys = list(campaign_names.keys())

    activities = (
        EnquiryActivity.objects
        .filter(
            activity_type="whatsapp",
            campaign_key__in=campaign_keys,
        )
        .select_related(
            "enquiry",
            "created_by",
            "created_by__staff_profile",
        )
    )

    branch_order = [
        ("kharghar", "Kharghar"),
        ("panvel", "Panvel"),
        ("kamothe", "Kamothe"),
        ("koperkhairane", "Koperkhairane"),
        ("ghansoli", "Ghansoli"),
        ("nerul", "Nerul"),
        ("head_office", "Head Office"),
    ]

    branch_rows = []

    for branch_key, branch_name in branch_order:

        branch_qs = activities.filter(
            created_by__staff_profile__branch=branch_key
        )

        branch_rows.append({
            "branch_key": branch_key,
            "branch_name": branch_name,
            "message_count": branch_qs.count(),
            "unique_enquiries": (
                branch_qs.values("enquiry_id").distinct().count()
            ),
            "active_staff": (
                branch_qs.values("created_by_id").distinct().count()
            ),
            "last_activity": (
                branch_qs.aggregate(last=Max("created_at"))["last"]
            ),
        })

    campaign_rows = []

    for key, label in campaign_names.items():

        campaign_qs = activities.filter(campaign_key=key)

        campaign_rows.append({
            "key": key,
            "label": label,
            "message_count": campaign_qs.count(),
            "unique_enquiries": (
                campaign_qs.values("enquiry_id").distinct().count()
            ),
            "active_staff": (
                campaign_qs.values("created_by_id").distinct().count()
            ),
        })

    staff_rows = (
        activities
        .values(
            "created_by_id",
            "created_by__username",
            "created_by__first_name",
            "created_by__last_name",
            "created_by__staff_profile__branch",
        )
        .annotate(
            message_count=Count("id"),
            unique_enquiries=Count(
                "enquiry_id",
                distinct=True
            ),
            last_activity=Max("created_at"),
        )
        .order_by("-message_count", "created_by__username")
    )

    context = {
        "branch_rows": branch_rows,
        "campaign_rows": campaign_rows,
        "staff_rows": staff_rows,
        "total_messages": activities.count(),
        "total_enquiries": (
            activities.values("enquiry_id").distinct().count()
        ),
        "total_staff": (
            activities.values("created_by_id").distinct().count()
        ),
    }

    return render(
        request,
        "core/marketing_activity_dashboard.html",
        context
    )


# ============================================================
# MCTI SOCIAL CAUSE - FREE STUDENT HELP
# ============================================================

def free_student_help(request):
    return render(
        request,
        "core/free_student_help.html"
    )
