import io
from datetime import timedelta

import qrcode

from django.contrib.admin.views.decorators import staff_member_required
from django.core import signing
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from core.models import Enquiry, EnquiryActivity

from .forms import QuickCareerEnquiryForm
from .models import CareerProfile
from .services import get_course_suggestions



def public_aptitude_qr(request):
    public_url = request.build_absolute_uri(
        reverse(
            "career_tools:public_aptitude_start"
        )
    )

    qr = qrcode.QRCode(
        version=1,
        box_size=12,
        border=4,
    )
    qr.add_data(public_url)
    qr.make(fit=True)

    qr_image = qr.make_image(
        fill_color="black",
        back_color="white",
    )

    buffer = io.BytesIO()
    qr_image.save(buffer, format="PNG")
    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type="image/png",
    )
    response["Content-Disposition"] = (
        'inline; filename="MCTI-Free-Aptitude-QR.png"'
    )
    response["Cache-Control"] = "public, max-age=86400"

    return response


@transaction.atomic
def public_aptitude_start(request):
    source = "MCTI Public Aptitude - College Outreach"

    if request.method == "POST":
        form = QuickCareerEnquiryForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            full_name = data["full_name"].strip()
            mobile = data["mobile"]
            branch = data["preferred_branch"]

            enquiry = (
                Enquiry.objects.filter(mobile=mobile)
                .order_by("-created_at")
                .first()
            )

            if enquiry is None:
                enquiry = Enquiry.objects.create(
                    name=full_name,
                    mobile=mobile,
                    branch=branch,
                    status="new",
                    followup_date=(
                        timezone.localdate()
                        + timedelta(days=1)
                    ),
                    message=(
                        "Lead captured through public "
                        "MCTI Aptitude QR."
                    ),
                )
            else:
                enquiry.name = full_name
                enquiry.branch = branch

                if enquiry.followup_date is None:
                    enquiry.followup_date = (
                        timezone.localdate()
                        + timedelta(days=1)
                    )

                if not enquiry.message:
                    enquiry.message = (
                        "Lead updated through public "
                        "MCTI Aptitude QR."
                    )

                enquiry.save(
                    update_fields=[
                        "name",
                        "branch",
                        "followup_date",
                        "message",
                    ]
                )

            profile = (
                CareerProfile.objects.filter(mobile=mobile)
                .order_by("-updated_at")
                .first()
            )

            if profile is None:
                profile = CareerProfile(
                    mobile=mobile,
                    is_guest=True,
                )

            profile.full_name = full_name
            profile.mobile = mobile
            profile.enquiry = enquiry
            profile.highest_qualification = (
                data["highest_qualification"]
            )
            profile.stream = data["stream"]
            profile.current_status = data["current_status"]
            profile.career_interest = data["career_interest"]
            profile.preferred_branch = branch
            profile.consent_given = data["consent_given"]

            if profile.student_id is None:
                profile.is_guest = True
                profile.source = source

            profile.save()

            suggestions = get_course_suggestions(profile)

            if suggestions and enquiry.course_id is None:
                enquiry.course = suggestions[0]["course"]
                enquiry.save(update_fields=["course"])

            course_names = ", ".join(
                item["course"].title
                for item in suggestions
            )

            EnquiryActivity.objects.create(
                enquiry=enquiry,
                created_by=None,
                activity_type="note",
                message=(
                    "Public Aptitude QR registration completed. "
                    f"Suggested courses: {course_names}"
                ),
            )

            request.session[
                "career_guest_profile_id"
            ] = profile.id

            return redirect(
                "career_tools:aptitude_test"
            )
    else:
        form = QuickCareerEnquiryForm()

    return render(
        request,
        "career_tools/public_aptitude_start.html",
        {
            "form": form,
            "source": source,
        },
    )


@staff_member_required
@transaction.atomic
def quick_career_enquiry(request):
    if request.method == "POST":
        form = QuickCareerEnquiryForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            full_name = data["full_name"].strip()
            mobile = data["mobile"]
            branch = data["preferred_branch"]

            enquiry = (
                Enquiry.objects.filter(mobile=mobile)
                .order_by("-created_at")
                .first()
            )

            if enquiry is None:
                enquiry = Enquiry.objects.create(
                    name=full_name,
                    mobile=mobile,
                    branch=branch,
                    status="new",
                    followup_date=(
                        timezone.localdate()
                        + timedelta(days=1)
                    ),
                    message=(
                        "Lead captured through "
                        "MCTI Quick Career Enquiry."
                    ),
                )
            else:
                enquiry.name = full_name
                enquiry.branch = branch

                if enquiry.followup_date is None:
                    enquiry.followup_date = (
                        timezone.localdate()
                        + timedelta(days=1)
                    )

                if not enquiry.message:
                    enquiry.message = (
                        "Lead updated through "
                        "MCTI Quick Career Enquiry."
                    )

                enquiry.save(
                    update_fields=[
                        "name",
                        "branch",
                        "followup_date",
                        "message",
                    ]
                )

            profile = (
                CareerProfile.objects.filter(mobile=mobile)
                .order_by("-updated_at")
                .first()
            )

            if profile is None:
                profile = CareerProfile(
                    mobile=mobile,
                    is_guest=True,
                )

            profile.full_name = full_name
            profile.mobile = mobile
            profile.enquiry = enquiry
            profile.highest_qualification = (
                data["highest_qualification"]
            )
            profile.stream = data["stream"]
            profile.current_status = data["current_status"]
            profile.career_interest = data["career_interest"]
            profile.preferred_branch = branch
            profile.consent_given = data["consent_given"]

            if profile.student_id is None:
                profile.is_guest = True
                profile.source = "MCTI Quick Career Enquiry"

            profile.save()

            suggestions = get_course_suggestions(profile)

            if suggestions and enquiry.course_id is None:
                enquiry.course = suggestions[0]["course"]
                enquiry.save(update_fields=["course"])

            course_names = ", ".join(
                item["course"].title
                for item in suggestions
            )

            EnquiryActivity.objects.create(
                enquiry=enquiry,
                created_by=request.user,
                activity_type="note",
                message=(
                    "Quick Career Enquiry completed. "
                    f"Suggested courses: {course_names}"
                ),
            )

            request.session[
                "career_guest_profile_id"
            ] = profile.id

            return redirect(
                "career_tools:quick_enquiry_result",
                profile_id=profile.id,
            )
    else:
        form = QuickCareerEnquiryForm()

    return render(
        request,
        "career_tools/quick_enquiry.html",
        {
            "form": form,
        },
    )


@staff_member_required
def quick_enquiry_result(request, profile_id):
    profile = (
        CareerProfile.objects
        .select_related("enquiry", "student")
        .filter(id=profile_id)
        .first()
    )

    if profile is None:
        return redirect(
            "career_tools:quick_career_enquiry"
        )

    suggestions = get_course_suggestions(profile)

    aptitude_token = signing.Signer(
        salt="mcti-career-aptitude"
    ).sign(str(profile.id))

    aptitude_url = request.build_absolute_uri(
        reverse(
            "career_tools:aptitude_access",
            kwargs={"token": aptitude_token},
        )
    )

    aptitude_qr_url = reverse(
        "career_tools:aptitude_qr",
        kwargs={"profile_id": profile.id},
    )

    return render(
        request,
        "career_tools/quick_enquiry_result.html",
        {
            "profile": profile,
            "enquiry": profile.enquiry,
            "suggestions": suggestions,
            "aptitude_url": aptitude_url,
            "aptitude_qr_url": aptitude_qr_url,
        },
    )

def aptitude_access(request, token):
    try:
        profile_id = signing.Signer(
            salt="mcti-career-aptitude"
        ).unsign(token)
    except signing.BadSignature:
        return render(
            request,
            "career_tools/invalid_aptitude_link.html",
            status=400,
        )

    profile = CareerProfile.objects.filter(
        id=profile_id
    ).first()

    if profile is None:
        return render(
            request,
            "career_tools/invalid_aptitude_link.html",
            status=404,
        )

    request.session[
        "career_guest_profile_id"
    ] = profile.id

    return redirect(
        "career_tools:aptitude_test"
    )


@staff_member_required
def aptitude_qr(request, profile_id):
    profile = CareerProfile.objects.filter(
        id=profile_id
    ).first()

    if profile is None:
        return HttpResponse(
            "Career profile not found.",
            status=404,
        )

    token = signing.Signer(
        salt="mcti-career-aptitude"
    ).sign(str(profile.id))

    aptitude_url = request.build_absolute_uri(
        reverse(
            "career_tools:aptitude_access",
            kwargs={"token": token},
        )
    )

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=3,
    )
    qr.add_data(aptitude_url)
    qr.make(fit=True)

    qr_image = qr.make_image(
        fill_color="#111111",
        back_color="white",
    )

    qr_buffer = io.BytesIO()
    qr_image.save(qr_buffer, format="PNG")

    response = HttpResponse(
        qr_buffer.getvalue(),
        content_type="image/png",
    )
    response["Content-Disposition"] = (
        f'inline; filename="mcti-aptitude-{profile.id}.png"'
    )
    return response
