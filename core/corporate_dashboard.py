from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import Lower, Trim
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from .models import Enquiry, Admission, Course

BRANCHES = (
    ("kharghar", "Kharghar"),
    ("panvel", "Panvel"),
    ("koperkhairane", "Koperkhairane"),
    ("kamothe", "Kamothe"),
    ("ghansoli", "Ghansoli"),
    ("nerul", "Nerul"),
)


def corporate_allowed(user):
    if not user.is_authenticated or not user.is_active:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(
        name="Corporate Dashboard"
    ).exists()


def corporate_data():
    today = timezone.localdate()
    month_start = today.replace(day=1)

    enquiries = Enquiry.objects.exclude(
        message__icontains="MCTI AI Ready Maharashtra"
    )
    admissions = Admission.objects.all()

    result = []

    for key, label in BRANCHES:
        eq = enquiries.annotate(
            normalized_branch=Lower(Trim("branch"))
        ).filter(normalized_branch=key)

        ad = admissions.annotate(
            normalized_branch=Lower(Trim("branch"))
        ).filter(normalized_branch=key)

        result.append({
            "branch": label,
            "enquiries": eq.count(),
            "admissions": ad.count(),
            "today_enquiries": eq.filter(
                created_at__date=today
            ).count(),
            "today_admissions": ad.filter(
                admission_date=today
            ).count(),
            "month_enquiries": eq.filter(
                created_at__date__gte=month_start
            ).count(),
            "month_admissions": ad.filter(
                admission_date__gte=month_start
            ).count(),
        })

    return {
        "branches": result,
        "total_enquiries": enquiries.count(),
        "total_admissions": admissions.count(),
        "today_enquiries": sum(
            x["today_enquiries"] for x in result
        ),
        "today_admissions": sum(
            x["today_admissions"] for x in result
        ),
        "updated_at": timezone.localtime().strftime(
            "%d %b %Y, %I:%M:%S %p"
        ),
    }


@login_required(login_url="/corporate/login/")
def corporate_dashboard(request):
    if not corporate_allowed(request.user):
        return JsonResponse(
            {"error": "Access denied"}, status=403
        )
    return render(
        request,
        "core/corporate_dashboard.html",
    )


@login_required(login_url="/corporate/login/")
def corporate_dashboard_api(request):
    if not corporate_allowed(request.user):
        return JsonResponse(
            {"error": "Access denied"}, status=403
        )
    return JsonResponse(corporate_data())

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods


@never_cache
@csrf_protect
@require_http_methods(["GET", "POST"])
def corporate_login(request):
    if corporate_allowed(request.user):
        return redirect("corporate_dashboard")

    error = ""

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None and corporate_allowed(user):
            login(request, user)
            return redirect("corporate_dashboard")

        error = "Invalid username or password."

    return render(
        request,
        "core/corporate_login.html",
        {"error": error},
    )


@never_cache
@csrf_protect
@require_http_methods(["POST"])
def corporate_logout(request):
    logout(request)
    return redirect("corporate_login")


from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db import transaction
import re


@login_required(login_url="/corporate/login/")
@never_cache
@csrf_protect
@require_http_methods(["GET", "POST"])
def corporate_walkin(request):
    if not corporate_allowed(request.user):
        return JsonResponse({"error": "Access denied"}, status=403)

    courses = Course.objects.filter(
        is_active=True
    ).order_by("title")

    branches = BRANCHES
    error = ""
    duplicate_count = 0

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        mobile = request.POST.get("mobile", "").strip()
        course_id = request.POST.get("course", "").strip()
        branch = request.POST.get("branch", "").strip().lower()
        remarks = request.POST.get("remarks", "").strip()

        if not name or len(name) > 150:
            error = "Enter a valid visitor name."
        elif not re.fullmatch(r"[6-9][0-9]{9}", mobile):
            error = "Enter a valid 10-digit Indian mobile number."
        elif branch not in dict(BRANCHES):
            error = "Select a valid training center."
        elif len(remarks) > 1000:
            error = "Remarks must be under 1000 characters."
        else:
            course = courses.filter(pk=course_id).first() if course_id.isdigit() else None

            if not course:
                error = "Select a valid active course."
            else:
                duplicate_count = Enquiry.objects.filter(
                    mobile=mobile
                ).count()

                if duplicate_count and request.POST.get("confirm_duplicate") != "yes":
                    error = (
                        "This mobile number already has "
                        + str(duplicate_count)
                        + " enquiry record(s). Review the warning and confirm "
                        "that you want to register another enquiry."
                    )
                else:
                    with transaction.atomic():
                        enquiry = Enquiry.objects.create(
                            name=name,
                            mobile=mobile,
                            course=course,
                            branch=branch,
                            status="new",
                            message=(
                                "Source: Nerul Corporate Office - Walk-in"
                                + ("\\nRemarks: " + remarks if remarks else "")
                            ),
                        )

                    confirmation = (
                        "Walk-in enquiry saved successfully. "
                        "Enquiry ID: " + str(enquiry.pk)
                    )

                    if duplicate_count:
                        confirmation += (
                            " Note: This mobile number has "
                            + str(duplicate_count)
                            + " previous enquiry record(s)."
                        )

                    messages.success(request, confirmation)
                    return redirect("corporate_walkin")

    return render(
        request,
        "core/corporate_walkin.html",
        {
            "courses": courses,
            "branches": branches,
            "error": error,
            "duplicate_count": duplicate_count,
        },
    )



@login_required(login_url="/corporate/login/")
@never_cache
@require_http_methods(["GET"])
def corporate_walkin_duplicate_check(request):
    if not corporate_allowed(request.user):
        return JsonResponse({"error": "Access denied"}, status=403)

    mobile = request.GET.get("mobile", "").strip()

    if not re.fullmatch(r"[6-9][0-9]{9}", mobile):
        return JsonResponse({
            "valid": False,
            "count": 0,
        })

    count = Enquiry.objects.filter(mobile=mobile).count()

    return JsonResponse({
        "valid": True,
        "count": count,
        "duplicate": count > 0,
    })


@login_required(login_url="/corporate/login/")
@never_cache
def corporate_walkin_report(request):
    if not corporate_allowed(request.user):
        return JsonResponse({"error": "Access denied"}, status=403)

    from django.db.models import Q
    from datetime import datetime as dt

    marker = "Source: Nerul Corporate Office - Walk-in"
    today = timezone.localdate()
    month_start = today.replace(day=1)

    selected_branch = request.GET.get("branch", "").strip().lower()
    selected_status = request.GET.get("status", "").strip().lower()
    date_from = request.GET.get("from", "").strip()
    date_to = request.GET.get("to", "").strip()

    qs = Enquiry.objects.filter(
        message__startswith=marker
    )

    if selected_branch in dict(BRANCHES):
        qs = qs.annotate(
            report_branch=Lower(Trim("branch"))
        ).filter(report_branch=selected_branch)
    else:
        selected_branch = ""

    valid_statuses = dict(Enquiry._meta.get_field("status").choices)
    if selected_status in valid_statuses:
        qs = qs.filter(status=selected_status)
    else:
        selected_status = ""

    def parse_date(value):
        try:
            return dt.strptime(value, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None

    start = parse_date(date_from)
    end = parse_date(date_to)

    if start:
        qs = qs.filter(created_at__date__gte=start)
    if end:
        qs = qs.filter(created_at__date__lte=end)

    converted_filter = Q(status="converted") | Q(admission__isnull=False)

    total = qs.count()
    converted = qs.filter(converted_filter).distinct().count()

    branch_stats = []
    for key, label in BRANCHES:
        branch_qs = qs.filter(branch__iexact=key)
        branch_stats.append({
            "name": label,
            "total": branch_qs.count(),
            "converted": branch_qs.filter(converted_filter).distinct().count(),
        })

    recent = qs.select_related("course").order_by("-created_at", "-id")[:50]

    return render(
        request,
        "core/corporate_walkin_report.html",
        {
            "total": total,
            "today_count": qs.filter(created_at__date=today).count(),
            "month_count": qs.filter(created_at__date__gte=month_start).count(),
            "converted": converted,
            "conversion_rate": round(converted * 100 / total, 1) if total else 0,
            "branch_stats": branch_stats,
            "recent": recent,
            "branches": BRANCHES,
            "statuses": Enquiry._meta.get_field("status").choices,
            "selected_branch": selected_branch,
            "selected_status": selected_status,
            "date_from": date_from,
            "date_to": date_to,
        },
    )
