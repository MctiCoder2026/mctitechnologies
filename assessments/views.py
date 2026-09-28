from datetime import timedelta
import io
import uuid

import qrcode

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

from django.conf import settings
from django.http import HttpResponse

from django.db import transaction
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.models import Enquiry, EnquiryActivity

from .forms import AIReadyRegistrationForm
from .models import (
    Assessment,
    AssessmentAttempt,
    AssessmentParticipantProfile,
    AssessmentAnswer,
    AssessmentResult,
    AssessmentCertificate,
)


AI_READY_SLUG = "ai-ready-maharashtra-2026"


@transaction.atomic
def ai_ready_start(request):
    assessment = get_object_or_404(
        Assessment,
        slug=AI_READY_SLUG,
        is_active=True,
    )

    if request.method == "POST":
        form = AIReadyRegistrationForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            full_name = data["full_name"].strip()
            mobile = data["mobile"]
            email = data.get("email") or ""

            enquiry = (
                Enquiry.objects.filter(mobile=mobile)
                .order_by("-created_at")
                .first()
            )

            if enquiry is None:
                enquiry = Enquiry.objects.create(
                    name=full_name,
                    mobile=mobile,
                    email=email or None,
                    status="new",
                    followup_date=(
                        timezone.localdate()
                        + timedelta(days=1)
                    ),
                    message=(
                        "Lead captured through MCTI AI Ready "
                        "Maharashtra – AI Awareness Quiz 2026."
                    ),
                )
            else:
                update_fields = []

                if full_name and enquiry.name != full_name:
                    enquiry.name = full_name
                    update_fields.append("name")

                if email and not enquiry.email:
                    enquiry.email = email
                    update_fields.append("email")

                if enquiry.followup_date is None:
                    enquiry.followup_date = (
                        timezone.localdate()
                        + timedelta(days=1)
                    )
                    update_fields.append("followup_date")

                if update_fields:
                    enquiry.save(update_fields=update_fields)

            profile = AssessmentParticipantProfile.objects.create(
                assessment=assessment,
                full_name=full_name,
                mobile=mobile,
                email=email,
                qualification=data["qualification"],
                institution_name=data["institution_name"].strip(),
                district=data["district"].strip(),
                city=data["city"].strip(),
                current_status=data["current_status"],
                career_interest=data["career_interest"].strip(),
                enquiry=enquiry,
                consent_given=data["consent_given"],
            )

            attempt = AssessmentAttempt.objects.create(
                assessment=assessment,
                participant_profile=profile,
                participant_name=full_name,
                participant_mobile=mobile,
                participant_email=email,
                status="started",
            )

            EnquiryActivity.objects.create(
                enquiry=enquiry,
                created_by=None,
                activity_type="note",
                message=(
                    "Registered for MCTI AI Ready Maharashtra – "
                    "AI Awareness Quiz 2026. "
                    f"Assessment attempt ID: {attempt.id}"
                ),
            )

            request.session["ai_ready_attempt_id"] = attempt.id

            return redirect(
                "assessments:ai_ready_quiz",
                attempt_id=attempt.id,
            )

    else:
        form = AIReadyRegistrationForm()

    return render(
        request,
        "assessments/ai_ready_start.html",
        {
            "form": form,
            "assessment": assessment,
        },
    )


@transaction.atomic
def ai_ready_quiz(request, attempt_id):
    if request.session.get("ai_ready_attempt_id") != attempt_id:
        messages.error(
            request,
            "Please register first to access your AI Awareness Quiz."
        )
        return redirect("assessments:ai_ready_start")

    attempt = get_object_or_404(
        AssessmentAttempt.objects.select_related(
            "assessment",
            "participant_profile",
        ),
        id=attempt_id,
        assessment__slug=AI_READY_SLUG,
        status="started",
    )

    questions = list(
        attempt.assessment.questions.filter(
            is_active=True
        ).prefetch_related("options")
    )

    if request.method == "POST":
        submitted_answers = []

        for question in questions:
            option_id = request.POST.get(
                f"question_{question.id}"
            )

            if not option_id:
                messages.error(
                    request,
                    "Please answer all 25 questions before submitting."
                )
                return render(
                    request,
                    "assessments/ai_ready_quiz.html",
                    {
                        "attempt": attempt,
                        "assessment": attempt.assessment,
                        "questions": questions,
                    },
                )

            option = next(
                (
                    item
                    for item in question.options.all()
                    if str(item.id) == str(option_id)
                ),
                None,
            )

            if option is None:
                messages.error(
                    request,
                    "Invalid answer detected. Please try again."
                )
                return render(
                    request,
                    "assessments/ai_ready_quiz.html",
                    {
                        "attempt": attempt,
                        "assessment": attempt.assessment,
                        "questions": questions,
                    },
                )

            submitted_answers.append(
                (question, option)
            )

        score = 0
        total_marks = 0

        for question, option in submitted_answers:
            is_correct = option.is_correct
            marks_awarded = (
                question.marks if is_correct else 0
            )

            total_marks += question.marks
            score += marks_awarded

            AssessmentAnswer.objects.update_or_create(
                attempt=attempt,
                question=question,
                defaults={
                    "selected_option": option,
                    "is_correct": is_correct,
                    "marks_awarded": marks_awarded,
                },
            )

        percentage = (
            (score / total_marks) * 100
            if total_marks
            else 0
        )

        if score <= 8:
            band = "AI Explorer"
            title = "Your AI Journey Starts Here"
            message = (
                "You have started exploring AI. "
                "Build your understanding of everyday AI tools, "
                "prompting and responsible AI use."
            )
        elif score <= 15:
            band = "AI Learner"
            title = "You Are Building AI Awareness"
            message = (
                "You understand several important AI concepts. "
                "More hands-on practice can help you use AI "
                "with greater confidence."
            )
        elif score <= 20:
            band = "AI Ready"
            title = "You Are AI Ready"
            message = (
                "You have a strong practical understanding of AI "
                "and how it can support learning, productivity "
                "and career growth."
            )
        else:
            band = "AI Champion"
            title = "You Are an AI Champion"
            message = (
                "You demonstrate strong AI awareness, responsible "
                "usage knowledge and readiness for an AI-powered future."
            )

        AssessmentResult.objects.update_or_create(
            attempt=attempt,
            defaults={
                "result_band": band,
                "result_title": title,
                "result_message": message,
                "recommendation": (
                    "Continue building practical AI skills and join "
                    "the MCTI Free AI Masterclass for guided learning."
                ),
            },
        )

        attempt.score = score
        attempt.total_marks = total_marks
        attempt.percentage = percentage
        attempt.status = "completed"
        attempt.completed_at = timezone.now()
        attempt.save(
            update_fields=[
                "score",
                "total_marks",
                "percentage",
                "status",
                "completed_at",
            ]
        )

        return redirect(
            "assessments:ai_ready_result",
            attempt_id=attempt.id,
        )

    return render(
        request,
        "assessments/ai_ready_quiz.html",
        {
            "attempt": attempt,
            "assessment": attempt.assessment,
            "questions": questions,
        },
    )



def ai_ready_result(request, attempt_id):
    if request.session.get("ai_ready_attempt_id") != attempt_id:
        messages.error(
            request,
            "Please register first to access your AI Readiness result."
        )
        return redirect("assessments:ai_ready_start")

    attempt = get_object_or_404(
        AssessmentAttempt.objects.select_related(
            "assessment",
            "participant_profile",
            "result",
        ),
        id=attempt_id,
        assessment__slug=AI_READY_SLUG,
        status="completed",
    )

    return render(
        request,
        "assessments/ai_ready_result.html",
        {
            "attempt": attempt,
            "assessment": attempt.assessment,
            "result": attempt.result,
        },
    )


def _get_or_create_ai_certificate(attempt):
    """
    Return one permanent certificate for a completed AI Ready attempt.
    Repeated downloads reuse the same certificate and verification token.
    """
    if attempt.status != "completed":
        return None

    existing = AssessmentCertificate.objects.filter(
        attempt=attempt
    ).first()

    if existing:
        return existing

    certificate_id = f"MCTI-AI-2026-{attempt.id:06d}"

    return AssessmentCertificate.objects.create(
        attempt=attempt,
        certificate_id=certificate_id,
        verification_token=uuid.uuid4().hex,
    )


def ai_ready_certificate(request, attempt_id):
    if request.session.get("ai_ready_attempt_id") != attempt_id:
        messages.error(
            request,
            "Please register first to access your certificate."
        )
        return redirect("assessments:ai_ready_start")

    attempt = get_object_or_404(
        AssessmentAttempt.objects.select_related(
            "assessment",
            "participant_profile",
            "result",
        ),
        id=attempt_id,
        assessment__slug=AI_READY_SLUG,
        status="completed",
    )

    certificate = _get_or_create_ai_certificate(attempt)

    verification_url = request.build_absolute_uri(
        f"/assessment/certificate/verify/{certificate.verification_token}/"
    )

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=2,
    )
    qr.add_data(verification_url)
    qr.make(fit=True)

    qr_image = qr.make_image(
        fill_color="black",
        back_color="white",
    )

    qr_buffer = io.BytesIO()
    qr_image.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    qr_reader = ImageReader(qr_buffer)

    asset_dir = (
        settings.BASE_DIR
        / "lms"
        / "static"
        / "lms"
        / "certificate"
    )

    logo_path = asset_dir / "mcti_technologies_logo.png"
    signature_path = asset_dir / "director_signature.png"

    logo_reader = (
        ImageReader(str(logo_path))
        if logo_path.exists()
        else None
    )

    signature_reader = (
        ImageReader(str(signature_path))
        if signature_path.exists()
        else None
    )

    safe_name = (
        attempt.participant_name
        .replace(" ", "_")
        .replace("/", "-")
    )

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="MCTI_AI_Ready_Certificate_{safe_name}.pdf"'
    )

    page_width, page_height = landscape(A4)
    pdf = canvas.Canvas(response, pagesize=landscape(A4))

    # Background
    pdf.setFillColor(colors.HexColor("#FFFDF8"))
    pdf.rect(
        0, 0,
        page_width, page_height,
        fill=1,
        stroke=0,
    )

    # Subtle MCTI watermark pattern
    pdf.saveState()
    pdf.setFillColor(colors.HexColor("#F7E8D8"))
    pdf.setFont("Helvetica-Bold", 7)

    y = 45
    while y < page_height - 45:
        x = 45
        while x < page_width - 45:
            pdf.drawString(x, y, "MCTI")
            x += 55
        y += 28

    pdf.restoreState()

    # Borders
    pdf.setStrokeColor(colors.HexColor("#111827"))
    pdf.setLineWidth(4)
    pdf.rect(
        20, 20,
        page_width - 40,
        page_height - 40,
        fill=0,
        stroke=1,
    )

    pdf.setStrokeColor(colors.HexColor("#FF6B00"))
    pdf.setLineWidth(1.5)
    pdf.rect(
        30, 30,
        page_width - 60,
        page_height - 60,
        fill=0,
        stroke=1,
    )

    # Logo
    if logo_reader:
        pdf.drawImage(
            logo_reader,
            (page_width - 300) / 2,
            page_height - 125,
            width=300,
            height=92,
            preserveAspectRatio=True,
            mask="auto",
        )
    else:
        pdf.setFillColor(colors.HexColor("#FF6B00"))
        pdf.setFont("Helvetica-Bold", 24)
        pdf.drawCentredString(
            page_width / 2,
            page_height - 72,
            "MCTI TECHNOLOGIES",
        )

    # Certificate heading
    pdf.setFillColor(colors.HexColor("#111827"))
    pdf.setFont("Times-Bold", 30)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 150,
        "CERTIFICATE OF PARTICIPATION",
    )

    pdf.setFillColor(colors.HexColor("#FF6B00"))
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 174,
        "MCTI AI READY MAHARASHTRA 2026",
    )

    pdf.setFillColor(colors.HexColor("#475569"))
    pdf.setFont("Helvetica", 11)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 215,
        "This certificate is proudly presented to",
    )

    # Participant name
    participant_name = attempt.participant_name.upper()
    name_size = 25

    while (
        stringWidth(
            participant_name,
            "Times-Bold",
            name_size,
        ) > page_width - 180
        and name_size > 15
    ):
        name_size -= 1

    pdf.setFillColor(colors.HexColor("#FF6B00"))
    pdf.setFont("Times-Bold", name_size)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 255,
        participant_name,
    )

    # Participation text
    pdf.setFillColor(colors.HexColor("#475569"))
    pdf.setFont("Helvetica", 11)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 290,
        "for successfully completing the 25-question AI Awareness Quiz",
    )
    pdf.drawCentredString(
        page_width / 2,
        page_height - 308,
        "and participating in the MCTI AI Ready Maharashtra initiative.",
    )

    # Readiness result
    result_band = attempt.result.result_band

    pdf.setFillColor(colors.HexColor("#111827"))
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 350,
        f"AI Readiness Category: {result_band}",
    )

    pdf.setFillColor(colors.HexColor("#475569"))
    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 374,
        f"Assessment Score: {attempt.score}/{attempt.total_marks}  |  AI Readiness: {attempt.percentage:.2f}%",
    )

    # Divider
    pdf.setStrokeColor(colors.HexColor("#E5E7EB"))
    pdf.setLineWidth(1)
    pdf.line(80, 155, page_width - 80, 155)

    # Certificate ID
    pdf.setFillColor(colors.HexColor("#64748B"))
    pdf.setFont("Helvetica", 8)
    pdf.drawString(60, 116, "Certificate ID")

    pdf.setFillColor(colors.HexColor("#111827"))
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(
        60,
        101,
        certificate.certificate_id,
    )

    # Issue date
    pdf.setFillColor(colors.HexColor("#64748B"))
    pdf.setFont("Helvetica", 8)
    pdf.drawString(250, 116, "Issue Date")

    pdf.setFillColor(colors.HexColor("#111827"))
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(
        250,
        101,
        certificate.issued_at.strftime("%d %B %Y"),
    )

    # QR verification
    qr_size = 70
    pdf.drawImage(
        qr_reader,
        page_width - 300,
        72,
        width=qr_size,
        height=qr_size,
        preserveAspectRatio=True,
        mask="auto",
    )

    pdf.setFillColor(colors.HexColor("#64748B"))
    pdf.setFont("Helvetica", 7)
    pdf.drawCentredString(
        page_width - 265,
        62,
        "Scan to verify",
    )

    # Director signature
    if signature_reader:
        pdf.drawImage(
            signature_reader,
            page_width - 198,
            108,
            width=115,
            height=48,
            preserveAspectRatio=True,
            mask="auto",
        )

    pdf.setStrokeColor(colors.HexColor("#111827"))
    pdf.line(
        page_width - 210,
        105,
        page_width - 70,
        105,
    )

    pdf.setFillColor(colors.HexColor("#111827"))
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawCentredString(
        page_width - 140,
        88,
        "DIRECTOR",
    )

    pdf.setFillColor(colors.HexColor("#64748B"))
    pdf.setFont("Helvetica", 7)
    pdf.drawCentredString(
        page_width - 140,
        76,
        "MCTI",
    )

    # Footer
    pdf.setFillColor(colors.HexColor("#64748B"))
    pdf.setFont("Helvetica", 7)
    pdf.drawCentredString(
        page_width / 2,
        48,
        "MCTI Technologies - An Initiative by Maharashtra Computer Training Institute",
    )
    pdf.drawCentredString(
        page_width / 2,
        38,
        "Independent AI awareness initiative | Certificate verification available via QR",
    )

    pdf.showPage()
    pdf.save()

    return response


def verify_assessment_certificate(request, verification_token):
    certificate = get_object_or_404(
        AssessmentCertificate.objects.select_related(
            "attempt",
            "attempt__assessment",
            "attempt__result",
        ),
        verification_token=verification_token,
    )

    return render(
        request,
        "assessments/verify_certificate.html",
        {
            "certificate": certificate,
            "attempt": certificate.attempt,
            "assessment": certificate.attempt.assessment,
            "result": certificate.attempt.result,
        },
    )
