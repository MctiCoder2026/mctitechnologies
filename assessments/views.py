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

from core.models import Course, Enquiry, EnquiryActivity

from .forms import (
    AIReadyRegistrationForm,
    HiringApplicationForm,
    HiringEvaluationForm,
    HiringInterviewProfileForm,
    ScholarshipRegistrationForm,
)
from .models import (
    Assessment,
    AssessmentAttempt,
    AssessmentParticipantProfile,
    AssessmentAnswer,
    AssessmentResult,
    AssessmentCertificate,
    HiringCandidate,
    HiringApplication,
    HiringEvaluation,
    HiringSalaryMatrix,
    ScholarshipResult,
)


AI_READY_SLUG = "ai-ready-maharashtra-2026"
AI_READY_MARATHI_SLUG = "ai-ready-maharashtra-2026-marathi"
SCHOLARSHIP_SLUG = "mcti-scholarship-test-2026"


@transaction.atomic
def ai_ready_start(request):
    language = request.GET.get("lang", "en").lower()
    selected_slug = (
        AI_READY_MARATHI_SLUG if language == "mr"
        else AI_READY_SLUG
    )

    assessment = get_object_or_404(
        Assessment,
        slug=selected_slug,
        is_active=True,
    )

    if request.method == "POST":
        form = AIReadyRegistrationForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            full_name = data["full_name"].strip()
            mobile = data["mobile"]
            email = data.get("email") or ""

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
                enquiry=None,
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

            request.session["ai_ready_attempt_id"] = attempt.id
            request.session["ai_ready_language"] = language

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
            "language": language,
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
        assessment__slug__in=[
            AI_READY_SLUG,
            AI_READY_MARATHI_SLUG,
        ],
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
        assessment__slug__in=[
            AI_READY_SLUG,
            AI_READY_MARATHI_SLUG,
        ],
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
    # Student/public users must own the attempt through their session.
    # Authenticated admin/management users may download certificates
    # directly from the AI Ready management report.
    is_management_user = (
        request.user.is_authenticated
        and (
            request.user.is_superuser
            or request.user.is_staff
        )
    )

    if (
        not is_management_user
        and request.session.get("ai_ready_attempt_id") != attempt_id
    ):
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
        assessment__slug__in=[
            AI_READY_SLUG,
            AI_READY_MARATHI_SLUG,
        ],
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


# ============================================================
# MCTI HR HIRING ASSESSMENT
# Common engine for all hiring roles
# ============================================================

@transaction.atomic
def hiring_start(request):
    if request.method == "POST":
        form = HiringApplicationForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            role = data["job_role"]
            assessment = role.assessment

            if not assessment or not assessment.is_active:
                messages.error(
                    request,
                    "Assessment is not available for this job role."
                )
                return redirect("assessments:hiring_start")

            if not assessment.questions.filter(is_active=True).exists():
                messages.error(
                    request,
                    "Assessment questions are being prepared for this role."
                )
                return redirect("assessments:hiring_start")

            candidate = (
                HiringCandidate.objects
                .filter(mobile=data["mobile"])
                .order_by("-created_at")
                .first()
            )

            if candidate is None:
                candidate = HiringCandidate.objects.create(
                    full_name=data["full_name"].strip(),
                    mobile=data["mobile"],
                    email=data.get("email") or "",
                    qualification=data["qualification"].strip(),
                    experience=data.get("experience", "").strip(),
                    city=data["city"].strip(),
                    consent_given=data["consent_given"],
                )
            else:
                candidate.full_name = data["full_name"].strip()
                candidate.email = data.get("email") or candidate.email
                candidate.qualification = data["qualification"].strip()
                candidate.experience = data.get("experience", "").strip()
                candidate.city = data["city"].strip()
                candidate.consent_given = data["consent_given"]
                candidate.save()

            attempt = AssessmentAttempt.objects.create(
                assessment=assessment,
                participant_name=candidate.full_name,
                participant_mobile=candidate.mobile,
                participant_email=candidate.email,
                status="started",
            )

            application = HiringApplication.objects.create(
                candidate=candidate,
                job_role=role,
                employment_type=data["employment_type"],
                assessment_attempt=attempt,
                status="test_pending",
                source="MCTI Hiring Assessment",
            )

            request.session["hiring_application_id"] = application.id
            request.session["hiring_attempt_id"] = attempt.id

            return redirect(
                "assessments:hiring_interview",
                application_id=application.id,
            )
    else:
        form = HiringApplicationForm()

    return render(
        request,
        "assessments/hiring_start.html",
        {"form": form},
    )


@transaction.atomic
def _hiring_get_application(request, attempt_id):
    if request.session.get("hiring_attempt_id") != attempt_id:
        return None

    return get_object_or_404(
        HiringApplication.objects.select_related(
            "candidate",
            "job_role",
            "assessment_attempt",
            "assessment_attempt__assessment",
        ),
        assessment_attempt_id=attempt_id,
    )


def _hiring_section_questions(attempt, stage):
    qs = (
        attempt.assessment.questions
        .filter(is_active=True)
        .prefetch_related("options")
        .order_by("order")
    )

    if stage == "technical":
        return list(qs.filter(order__lte=25))

    if stage == "practical":
        return list(
            qs.filter(
                category="AUTO_PRACTICAL",
                order__gte=26,
                order__lte=35,
            )
        )

    if stage == "communication":
        return list(
            qs.filter(
                category="AUTO_COMMUNICATION",
                order__gte=36,
                order__lte=45,
            )
        )

    raise ValueError("Unknown hiring assessment stage.")


def _hiring_answered_count(attempt, stage):
    answers = attempt.answers.all()

    if stage == "technical":
        return answers.filter(
            question__order__lte=25
        ).count()

    if stage == "practical":
        return answers.filter(
            question__category="AUTO_PRACTICAL",
            question__order__gte=26,
            question__order__lte=35,
        ).count()

    if stage == "communication":
        return answers.filter(
            question__category="AUTO_COMMUNICATION",
            question__order__gte=36,
            question__order__lte=45,
        ).count()

    return 0


def _hiring_save_section_answers(request, attempt, questions):
    submitted_answers = []

    for question in questions:
        option_id = request.POST.get(
            f"question_{question.id}"
        )

        if not option_id:
            return None, "Please answer all questions before submitting."

        option = next(
            (
                item
                for item in question.options.all()
                if str(item.id) == str(option_id)
            ),
            None,
        )

        if option is None:
            return None, "Invalid answer detected. Please try again."

        submitted_answers.append((question, option))

    score = 0
    total_marks = 0

    for question, option in submitted_answers:
        is_correct = option.is_correct
        marks_awarded = question.marks if is_correct else 0

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
        if total_marks else 0
    )

    return percentage, None


@transaction.atomic
def hiring_quiz(request, attempt_id):
    application = _hiring_get_application(
        request,
        attempt_id,
    )

    if application is None:
        messages.error(
            request,
            "Please submit your hiring application first."
        )
        return redirect("assessments:hiring_start")

    attempt = application.assessment_attempt

    if attempt.status == "completed":
        return redirect(
            "assessments:hiring_result",
            attempt_id=attempt.id,
        )

    questions = _hiring_section_questions(
        attempt,
        "technical",
    )

    if len(questions) != 25:
        messages.error(
            request,
            "Technical assessment is not configured correctly."
        )
        return redirect("assessments:hiring_start")

    if request.method == "POST":
        percentage, error = _hiring_save_section_answers(
            request,
            attempt,
            questions,
        )

        if error:
            messages.error(request, error)
            return render(
                request,
                "assessments/hiring_quiz.html",
                {
                    "application": application,
                    "attempt": attempt,
                    "assessment": attempt.assessment,
                    "questions": questions,
                    "stage_title": "Technical Assessment",
                    "stage_number": 1,
                    "stage_total": 3,
                    "submit_label": "Continue to Practical Assessment",
                },
            )

        evaluation, _ = HiringEvaluation.objects.get_or_create(
            application=application
        )
        evaluation.technical_score = percentage
        evaluation.save(
            update_fields=[
                "technical_score",
                "updated_at",
            ]
        )

        application.status = "practical_pending"
        application.save(
            update_fields=["status", "updated_at"]
        )

        return redirect(
            "assessments:hiring_practical",
            attempt_id=attempt.id,
        )

    return render(
        request,
        "assessments/hiring_quiz.html",
        {
            "application": application,
            "attempt": attempt,
            "assessment": attempt.assessment,
            "questions": questions,
            "stage_title": "Technical Assessment",
            "stage_number": 1,
            "stage_total": 3,
            "submit_label": "Continue to Practical Assessment",
        },
    )


@transaction.atomic
def hiring_practical(request, attempt_id):
    application = _hiring_get_application(
        request,
        attempt_id,
    )

    if application is None:
        messages.error(
            request,
            "Please submit your hiring application first."
        )
        return redirect("assessments:hiring_start")

    attempt = application.assessment_attempt

    if attempt.status == "completed":
        return redirect(
            "assessments:hiring_result",
            attempt_id=attempt.id,
        )

    if _hiring_answered_count(attempt, "technical") < 25:
        messages.error(
            request,
            "Please complete the Technical Assessment first."
        )
        return redirect(
            "assessments:hiring_quiz",
            attempt_id=attempt.id,
        )

    questions = _hiring_section_questions(
        attempt,
        "practical",
    )

    if len(questions) != 10:
        messages.error(
            request,
            "Practical assessment is not configured correctly."
        )
        return redirect(
            "assessments:hiring_quiz",
            attempt_id=attempt.id,
        )

    if request.method == "POST":
        percentage, error = _hiring_save_section_answers(
            request,
            attempt,
            questions,
        )

        if error:
            messages.error(request, error)
        else:
            evaluation, _ = HiringEvaluation.objects.get_or_create(
                application=application
            )
            evaluation.practical_score = percentage
            evaluation.save(
                update_fields=[
                    "practical_score",
                    "updated_at",
                ]
            )

            return redirect(
                "assessments:hiring_communication",
                attempt_id=attempt.id,
            )

    return render(
        request,
        "assessments/hiring_quiz.html",
        {
            "application": application,
            "attempt": attempt,
            "assessment": attempt.assessment,
            "questions": questions,
            "stage_title": "Practical / Scenario Assessment",
            "stage_number": 2,
            "stage_total": 3,
            "submit_label": "Continue to Communication Assessment",
        },
    )


@transaction.atomic
def hiring_communication(request, attempt_id):
    application = _hiring_get_application(
        request,
        attempt_id,
    )

    if application is None:
        messages.error(
            request,
            "Please submit your hiring application first."
        )
        return redirect("assessments:hiring_start")

    attempt = application.assessment_attempt

    if attempt.status == "completed":
        return redirect(
            "assessments:hiring_result",
            attempt_id=attempt.id,
        )

    if _hiring_answered_count(attempt, "technical") < 25:
        return redirect(
            "assessments:hiring_quiz",
            attempt_id=attempt.id,
        )

    if _hiring_answered_count(attempt, "practical") < 10:
        messages.error(
            request,
            "Please complete the Practical Assessment first."
        )
        return redirect(
            "assessments:hiring_practical",
            attempt_id=attempt.id,
        )

    questions = _hiring_section_questions(
        attempt,
        "communication",
    )

    if len(questions) != 10:
        messages.error(
            request,
            "Communication assessment is not configured correctly."
        )
        return redirect(
            "assessments:hiring_practical",
            attempt_id=attempt.id,
        )

    if request.method == "POST":
        communication_score, error = _hiring_save_section_answers(
            request,
            attempt,
            questions,
        )

        if error:
            messages.error(request, error)
        else:
            evaluation, _ = HiringEvaluation.objects.get_or_create(
                application=application
            )

            practical_score = evaluation.practical_score or 0

            evaluation = calculate_hiring_evaluation(
                application=application,
                practical_score=practical_score,
                communication_score=communication_score,
            )

            all_answers = attempt.answers.filter(
                question__is_active=True,
                question__order__lte=45,
            )

            raw_score = sum(
                answer.marks_awarded
                for answer in all_answers
            )

            total_marks = sum(
                answer.question.marks
                for answer in all_answers
            )

            attempt.score = raw_score
            attempt.total_marks = total_marks
            attempt.percentage = (
                (raw_score / total_marks) * 100
                if total_marks else 0
            )
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

            application.status = "test_completed"
            application.save(
                update_fields=["status", "updated_at"]
            )

            return redirect(
                "assessments:hiring_result",
                attempt_id=attempt.id,
            )

    return render(
        request,
        "assessments/hiring_quiz.html",
        {
            "application": application,
            "attempt": attempt,
            "assessment": attempt.assessment,
            "questions": questions,
            "stage_title": "Teaching / Communication Assessment",
            "stage_number": 3,
            "stage_total": 3,
            "submit_label": "Complete Assessment",
        },
    )


def hiring_result(request, attempt_id):
    if request.session.get("hiring_attempt_id") != attempt_id:
        messages.error(
            request,
            "Please complete your hiring assessment first."
        )
        return redirect("assessments:hiring_start")

    application = get_object_or_404(
        HiringApplication.objects.select_related(
            "candidate",
            "job_role",
            "assessment_attempt",
            "evaluation",
        ),
        assessment_attempt_id=attempt_id,
        assessment_attempt__status="completed",
    )

    return render(
        request,
        "assessments/hiring_result.html",
        {
            "application": application,
            "attempt": application.assessment_attempt,
            "evaluation": application.evaluation,
        },
    )


# ============================================================
# HIRING FINAL EVALUATION ENGINE
# ============================================================

def calculate_hiring_evaluation(application, practical_score, communication_score):
    """
    Final score uses the weights configured on HiringJobRole.

    Trainer roles currently:
        Technical / Subject Knowledge = 50%
        Practical / Development       = 30%
        Teaching / Communication      = 20%

    Tele Sales / Receptionist currently:
        Technical / Role Knowledge    = 40%
        Practical                     = 20%
        Communication                 = 40%
    """

    evaluation, _ = HiringEvaluation.objects.get_or_create(
        application=application
    )

    role = application.job_role

    # Keep all score arithmetic Decimal-safe.
    # Form/quiz percentages may arrive as float, while model DecimalFields
    # are returned as Decimal. Mixing Decimal and float raises TypeError.
    from decimal import Decimal

    technical_score = Decimal(str(evaluation.technical_score or 0))
    practical_score = Decimal(str(practical_score or 0))
    communication_score = Decimal(str(communication_score or 0))

    total_weight = (
        role.technical_weight
        + role.practical_weight
        + role.communication_weight
    )

    if total_weight != 100:
        raise ValueError(
            f"Job role weights must total 100. "
            f"{role.name} currently totals {total_weight}."
        )

    hundred = Decimal("100")

    final_score = (
        (technical_score * Decimal(str(role.technical_weight)) / hundred)
        + (practical_score * Decimal(str(role.practical_weight)) / hundred)
        + (communication_score * Decimal(str(role.communication_weight)) / hundred)
    )

    if final_score < 40:
        band = "not_shortlisted"
    elif final_score < 55:
        band = "trainee"
    elif final_score < 70:
        band = "junior"
    elif final_score < 85:
        band = "skilled"
    else:
        band = "advanced"

    salary = HiringSalaryMatrix.objects.filter(
        job_role=role,
        employment_type=application.employment_type,
        performance_band=band,
        is_active=True,
    ).first()

    evaluation.practical_score = practical_score
    evaluation.communication_score = communication_score
    evaluation.final_score = final_score
    evaluation.performance_band = band
    evaluation.suggested_salary_min = (
        salary.min_salary if salary else None
    )
    evaluation.suggested_salary_max = (
        salary.max_salary if salary else None
    )
    evaluation.evaluated_at = timezone.now()

    evaluation.save(
        update_fields=[
            "practical_score",
            "communication_score",
            "final_score",
            "performance_band",
            "suggested_salary_min",
            "suggested_salary_max",
            "evaluated_at",
            "updated_at",
        ]
    )

    return evaluation


@transaction.atomic
def hiring_hr_evaluate(request, application_id):
    # Main User / Head Office security.
    from core.views import is_admin_user

    if not is_admin_user(request.user):
        messages.error(
            request,
            "You do not have permission to access HR hiring evaluation."
        )
        return redirect("staff_login")

    application = get_object_or_404(
        HiringApplication.objects.select_related(
            "candidate",
            "job_role",
            "assessment_attempt",
        ),
        id=application_id,
        assessment_attempt__status="completed",
    )

    evaluation, _ = HiringEvaluation.objects.get_or_create(
        application=application
    )

    if request.method == "POST":
        form = HiringEvaluationForm(request.POST)

        if form.is_valid():
            decision = form.cleaned_data["decision"]

            if decision not in {"selected", "hold", "rejected"}:
                messages.error(request, "Invalid hiring decision.")
            else:
                application.status = decision
                application.save(
                    update_fields=["status", "updated_at"]
                )

                evaluation.notes = form.cleaned_data.get("notes", "")
                evaluation.evaluated_by = request.user
                evaluation.evaluated_at = timezone.now()
                evaluation.save(
                    update_fields=[
                        "notes",
                        "evaluated_by",
                        "evaluated_at",
                        "updated_at",
                    ]
                )

                messages.success(
                    request,
                    f"Candidate marked as {application.get_status_display()}."
                )

                return redirect(
                    "assessments:hiring_hr_evaluate",
                    application_id=application.id,
                )

    else:
        initial_decision = (
            application.status
            if application.status in {"selected", "hold", "rejected"}
            else ""
        )

        form = HiringEvaluationForm(
            initial={
                "decision": initial_decision,
                "notes": evaluation.notes,
            }
        )

    return render(
        request,
        "assessments/hiring_hr_evaluate.html",
        {
            "application": application,
            "attempt": application.assessment_attempt,
            "evaluation": evaluation,
            "form": form,
        },
    )


def hiring_hr_dashboard(request):
    # Same Main User / Head Office security used by MCTI.
    from core.views import is_admin_user

    if not is_admin_user(request.user):
        messages.error(
            request,
            "You do not have permission to access the HR Hiring Dashboard."
        )
        return redirect("staff_login")

    applications = (
        HiringApplication.objects
        .select_related(
            "candidate",
            "job_role",
            "assessment_attempt",
            "evaluation",
        )
        .order_by("-created_at")
    )

    # -----------------------------
    # FILTERS
    # -----------------------------
    role_id = request.GET.get("role", "").strip()
    status = request.GET.get("status", "").strip()
    employment_type = request.GET.get("employment_type", "").strip()
    search = request.GET.get("q", "").strip()

    if role_id:
        applications = applications.filter(job_role_id=role_id)

    if status:
        applications = applications.filter(status=status)

    if employment_type:
        applications = applications.filter(
            employment_type=employment_type
        )

    if search:
        from django.db.models import Q

        applications = applications.filter(
            Q(candidate__full_name__icontains=search)
            | Q(candidate__mobile__icontains=search)
            | Q(candidate__email__icontains=search)
        )

    from .models import HiringJobRole

    roles = HiringJobRole.objects.filter(
        is_active=True
    ).order_by("name")

    all_applications = HiringApplication.objects.all()

    summary = {
        "total": all_applications.count(),
        "test_pending": all_applications.filter(
            status="test_pending"
        ).count(),
        "test_completed": all_applications.filter(
            status="test_completed"
        ).count(),
        "shortlisted": all_applications.filter(
            status="shortlisted"
        ).count(),
        "selected": all_applications.filter(
            status="selected"
        ).count(),
        "joined": all_applications.filter(
            status="joined"
        ).count(),
    }

    return render(
        request,
        "assessments/hiring_hr_dashboard.html",
        {
            "applications": applications,
            "roles": roles,
            "summary": summary,
            "status_choices": HiringApplication.STATUS_CHOICES,
            "employment_choices": HiringSalaryMatrix.EMPLOYMENT_TYPES,
            "selected_role": role_id,
            "selected_status": status,
            "selected_employment": employment_type,
            "search": search,
        },
    )


@transaction.atomic
def hiring_interview(request, application_id):
    """
    Standard interview profile completed before the technical test.
    Answers are stored for HR review and are not automatically scored.
    """
    from .models import HiringInterviewProfile

    if request.session.get("hiring_application_id") != application_id:
        messages.error(
            request,
            "Please submit your hiring application first."
        )
        return redirect("assessments:hiring_start")

    application = get_object_or_404(
        HiringApplication.objects.select_related(
            "candidate",
            "job_role",
            "assessment_attempt",
        ),
        id=application_id,
    )

    attempt = application.assessment_attempt

    if not attempt:
        messages.error(
            request,
            "Assessment is not available for this application."
        )
        return redirect("assessments:hiring_start")

    # Existing profile can be reviewed/updated until test begins.
    profile = HiringInterviewProfile.objects.filter(
        application=application
    ).first()

    if request.method == "POST":
        form = HiringInterviewProfileForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            HiringInterviewProfile.objects.update_or_create(
                application=application,
                defaults={
                    "about_yourself": data["about_yourself"],
                    "why_mcti": data["why_mcti"],
                    "why_select_you": data["why_select_you"],
                    "strengths": data["strengths"],
                    "weakness_improving": data["weakness_improving"],
                    "career_goals": data["career_goals"],
                    "current_learning": data.get(
                        "current_learning", ""
                    ),
                    "role_interest": data["role_interest"],
                    "why_train_students": data.get(
                        "why_train_students", ""
                    ),
                    "job_source": data.get("job_source", ""),
                    "expected_salary": data.get(
                        "expected_salary"
                    ),
                    "joining_availability": data.get(
                        "joining_availability", ""
                    ),
                },
            )

            return redirect(
                "assessments:hiring_quiz",
                attempt_id=attempt.id,
            )

    else:
        initial = {}

        if profile:
            initial = {
                "about_yourself": profile.about_yourself,
                "why_mcti": profile.why_mcti,
                "why_select_you": profile.why_select_you,
                "strengths": profile.strengths,
                "weakness_improving": profile.weakness_improving,
                "career_goals": profile.career_goals,
                "current_learning": profile.current_learning,
                "role_interest": profile.role_interest,
                "why_train_students": profile.why_train_students,
                "job_source": profile.job_source,
                "expected_salary": profile.expected_salary,
                "joining_availability": profile.joining_availability,
            }

        form = HiringInterviewProfileForm(initial=initial)

    return render(
        request,
        "assessments/hiring_interview.html",
        {
            "application": application,
            "form": form,
        },
    )


# ============================================================
# MCTI SCHOLARSHIP TEST
# ============================================================

@transaction.atomic
def scholarship_start(request):
    assessment = get_object_or_404(
        Assessment,
        slug=SCHOLARSHIP_SLUG,
        is_active=True,
    )

    if request.method == "POST":
        form = ScholarshipRegistrationForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            full_name = data["full_name"].strip()
            mobile = data["mobile"]
            email = data.get("email") or ""

            # IMPORTANT:
            # Scholarship registrations stay separate from normal CRM.
            # No Enquiry is created here.
            profile = AssessmentParticipantProfile.objects.create(
                assessment=assessment,
                full_name=full_name,
                mobile=mobile,
                email=email,
                qualification=data["qualification"],
                institution_name=data.get("institution_name", "").strip(),
                district="",
                city=data["city"].strip(),
                current_status=data["current_status"],
                career_interest=data["course"],
                enquiry=None,
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

            ScholarshipResult.objects.create(
                attempt=attempt,
                scholarship_percentage=0,
                scholarship_band="Test Pending",
                selected_course=data["course"],
                preferred_branch=data["preferred_branch"],
                claim_status="new",
            )

            request.session["scholarship_attempt_id"] = attempt.id

            return redirect(
                "assessments:scholarship_quiz",
                attempt_id=attempt.id,
            )

    else:
        form = ScholarshipRegistrationForm()

    return render(
        request,
        "assessments/scholarship_start.html",
        {
            "form": form,
            "assessment": assessment,
        },
    )


@transaction.atomic
def scholarship_quiz(request, attempt_id):

    if request.session.get("scholarship_attempt_id") != attempt_id:
        messages.error(
            request,
            "Please register first to access the Scholarship Test."
        )
        return redirect("assessments:scholarship_start")

    attempt = get_object_or_404(
        AssessmentAttempt.objects.select_related(
            "assessment",
            "participant_profile",
        ),
        id=attempt_id,
        assessment__slug=SCHOLARSHIP_SLUG,
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
                    f"Please answer all {len(questions)} questions before submitting."
                )
                return render(
                    request,
                    "assessments/scholarship_quiz.html",
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
                return redirect(
                    "assessments:scholarship_quiz",
                    attempt_id=attempt.id,
                )

            submitted_answers.append((question, option))

        score = 0
        total_marks = 0

        for question, option in submitted_answers:
            is_correct = option.is_correct
            marks_awarded = question.marks if is_correct else 0

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

        # Scholarship policy
        if percentage >= 90:
            scholarship_percentage = 50
            band = "Outstanding"
        elif percentage >= 80:
            scholarship_percentage = 40
            band = "Excellent"
        elif percentage >= 70:
            scholarship_percentage = 30
            band = "Very Good"
        elif percentage >= 60:
            scholarship_percentage = 20
            band = "Good"
        elif percentage >= 50:
            scholarship_percentage = 10
            band = "Qualified"
        else:
            scholarship_percentage = 0
            band = "Career Guidance Eligible"

        scholarship = attempt.scholarship_result
        scholarship.scholarship_percentage = scholarship_percentage
        scholarship.scholarship_band = band
        scholarship.claim_status = "test_completed"
        scholarship.valid_until = (
            timezone.localdate() + timedelta(days=7)
        )
        scholarship.save(
            update_fields=[
                "scholarship_percentage",
                "scholarship_band",
                "claim_status",
                "valid_until",
                "updated_at",
            ]
        )

        AssessmentResult.objects.update_or_create(
            attempt=attempt,
            defaults={
                "result_band": band,
                "result_title": (
                    f"{scholarship_percentage}% Scholarship Qualified"
                    if scholarship_percentage
                    else "Career Guidance Eligible"
                ),
                "result_message": (
                    f"You scored {percentage:.0f}% in the "
                    "MCTI Scholarship Test 2026."
                ),
                "recommendation": (
                    "Connect with an MCTI counsellor for course guidance "
                    "and scholarship eligibility confirmation."
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
            "assessments:scholarship_result",
            attempt_id=attempt.id,
        )

    return render(
        request,
        "assessments/scholarship_quiz.html",
        {
            "attempt": attempt,
            "assessment": attempt.assessment,
            "questions": questions,
        },
    )


def scholarship_result(request, attempt_id):

    if request.session.get("scholarship_attempt_id") != attempt_id:
        messages.error(
            request,
            "Please register first to access your Scholarship result."
        )
        return redirect("assessments:scholarship_start")

    attempt = get_object_or_404(
        AssessmentAttempt.objects.select_related(
            "assessment",
            "participant_profile",
            "result",
            "scholarship_result",
        ),
        id=attempt_id,
        assessment__slug=SCHOLARSHIP_SLUG,
        status="completed",
    )

    return render(
        request,
        "assessments/scholarship_result.html",
        {
            "attempt": attempt,
            "assessment": attempt.assessment,
            "result": attempt.result,
            "scholarship": attempt.scholarship_result,
        },
    )


# ============================================================
# SCHOLARSHIP MANAGEMENT DASHBOARD
# ============================================================

def scholarship_dashboard(request):

    from core.views import is_admin_user

    if not is_admin_user(request.user):
        messages.error(request, "You are not authorized to access this page.")
        return redirect("staff_login")

    scholarship_results = (
        ScholarshipResult.objects
        .select_related(
            "attempt",
            "attempt__participant_profile",
            "attempt__participant_profile__enquiry",
        )
        .filter(
            attempt__assessment__slug=SCHOLARSHIP_SLUG
        )
        .order_by("-created_at")
    )

    status_filter = request.GET.get("status", "").strip()

    if status_filter:
        scholarship_results = scholarship_results.filter(
            claim_status=status_filter
        )

    stats = {
        "total": ScholarshipResult.objects.filter(
            attempt__assessment__slug=SCHOLARSHIP_SLUG
        ).count(),

        "completed": ScholarshipResult.objects.filter(
            attempt__assessment__slug=SCHOLARSHIP_SLUG,
            claim_status="test_completed",
        ).count(),

        "interested": ScholarshipResult.objects.filter(
            attempt__assessment__slug=SCHOLARSHIP_SLUG,
            claim_status="interested",
        ).count(),

        "sent_to_enquiry": ScholarshipResult.objects.filter(
            attempt__assessment__slug=SCHOLARSHIP_SLUG,
            claim_status="sent_to_enquiry",
        ).count(),
    }

    return render(
        request,
        "assessments/scholarship_dashboard.html",
        {
            "scholarship_results": scholarship_results,
            "stats": stats,
            "status_filter": status_filter,
            "status_choices": ScholarshipResult.CLAIM_STATUS_CHOICES,
        },
    )


@transaction.atomic
def scholarship_update_status(request, scholarship_id):

    from core.views import is_admin_user

    if not is_admin_user(request.user):
        messages.error(request, "You are not authorized to perform this action.")
        return redirect("staff_login")

    if request.method != "POST":
        return redirect("assessments:scholarship_dashboard")

    scholarship = get_object_or_404(
        ScholarshipResult,
        id=scholarship_id,
        attempt__assessment__slug=SCHOLARSHIP_SLUG,
    )

    new_status = request.POST.get("status", "").strip()

    allowed_statuses = {
        value
        for value, label in ScholarshipResult.CLAIM_STATUS_CHOICES
    }

    # Sent to Enquiry must happen only through the dedicated action.
    allowed_statuses.discard("sent_to_enquiry")

    if new_status not in allowed_statuses:
        messages.error(request, "Invalid scholarship status.")
        return redirect("assessments:scholarship_dashboard")

    scholarship.claim_status = new_status
    scholarship.save(
        update_fields=[
            "claim_status",
            "updated_at",
        ]
    )

    messages.success(
        request,
        f"Scholarship status updated to {scholarship.get_claim_status_display()}."
    )

    return redirect("assessments:scholarship_dashboard")


@transaction.atomic
def scholarship_send_to_enquiry(request, scholarship_id):

    from core.views import is_admin_user

    if not is_admin_user(request.user):
        messages.error(request, "You are not authorized to perform this action.")
        return redirect("staff_login")

    if request.method != "POST":
        return redirect("assessments:scholarship_dashboard")

    scholarship = get_object_or_404(
        ScholarshipResult.objects.select_related(
            "attempt",
            "attempt__participant_profile",
        ),
        id=scholarship_id,
        attempt__assessment__slug=SCHOLARSHIP_SLUG,
    )

    attempt = scholarship.attempt
    profile = attempt.participant_profile

    # Idempotent: if already linked, never create another CRM enquiry.
    if profile.enquiry_id:
        scholarship.claim_status = "sent_to_enquiry"
        scholarship.save(
            update_fields=[
                "claim_status",
                "updated_at",
            ]
        )

        messages.info(
            request,
            "This scholarship candidate is already linked to CRM."
        )
        return redirect("assessments:scholarship_dashboard")

    course = (
        Course.objects
        .filter(
            title=scholarship.selected_course,
            is_active=True,
        )
        .first()
    )

    # Reuse latest enquiry for the same mobile if one already exists.
    enquiry = (
        Enquiry.objects
        .filter(mobile=profile.mobile)
        .order_by("-created_at")
        .first()
    )

    created = False

    if enquiry is None:
        enquiry = Enquiry.objects.create(
            name=profile.full_name,
            mobile=profile.mobile,
            email=profile.email or None,
            course=course,
            branch=scholarship.preferred_branch or None,
            status="new",
            message=(
                "Lead transferred manually from "
                "MCTI Scholarship Test 2026."
            ),
        )
        created = True

    else:
        changed_fields = []

        if not enquiry.course_id and course:
            enquiry.course = course
            changed_fields.append("course")

        if not enquiry.branch and scholarship.preferred_branch:
            enquiry.branch = scholarship.preferred_branch
            changed_fields.append("branch")

        if not enquiry.email and profile.email:
            enquiry.email = profile.email
            changed_fields.append("email")

        if changed_fields:
            enquiry.save(update_fields=changed_fields)

    EnquiryActivity.objects.create(
        enquiry=enquiry,
        created_by=request.user,
        activity_type="note",
        message=(
            "Scholarship Lead transferred to CRM | "
            f"Test Score: {attempt.percentage:.2f}% | "
            f"Scholarship: {scholarship.scholarship_percentage}% | "
            f"Band: {scholarship.scholarship_band} | "
            f"Course: {scholarship.selected_course} | "
            f"Preferred Branch: {scholarship.preferred_branch}"
        ),
    )

    profile.enquiry = enquiry
    profile.save(update_fields=["enquiry"])

    scholarship.claim_status = "sent_to_enquiry"
    scholarship.save(
        update_fields=[
            "claim_status",
            "updated_at",
        ]
    )

    if created:
        messages.success(
            request,
            f"{profile.full_name} sent to CRM as a new enquiry."
        )
    else:
        messages.success(
            request,
            f"{profile.full_name} linked with the existing CRM enquiry."
        )

    return redirect("assessments:scholarship_dashboard")

# ============================================================
# MCTI CYBER FRAUD AWARENESS TEST 2026
# ============================================================

CYBER_FRAUD_SLUG = "mcti-cyber-fraud-awareness-2026"


@transaction.atomic
def cyber_fraud_start(request):

    assessment = get_object_or_404(
        Assessment,
        slug=CYBER_FRAUD_SLUG,
        is_active=True,
    )

    if request.method == "POST":

        language = request.POST.get("language", "en").strip().lower()
        if language not in {"en", "mr", "hi"}:
            language = "en"

        request.session["cyber_fraud_language"] = language

        full_name = request.POST.get("full_name", "").strip()
        mobile = request.POST.get("mobile", "").strip()
        email = request.POST.get("email", "").strip()
        city = request.POST.get("city", "").strip()
        current_status = request.POST.get("current_status", "").strip()
        institution_name = request.POST.get("institution_name", "").strip()
        consent = request.POST.get("consent_given") == "on"

        digits = "".join(ch for ch in mobile if ch.isdigit())

        if len(digits) == 12 and digits.startswith("91"):
            digits = digits[2:]

        if (
            not full_name
            or len(digits) != 10
            or not city
            or not current_status
            or not consent
        ):
            messages.error(
                request,
                "Please complete all required fields and enter a valid 10-digit mobile number."
            )
        else:

            mobile = digits

            enquiry = (
                Enquiry.objects
                .filter(mobile=mobile)
                .order_by("-created_at")
                .first()
            )

            if not enquiry:
                enquiry_kwargs = {
                    "name": full_name,
                    "mobile": mobile,
                }

                # Optional fields are intentionally not assumed here.
                try:
                    enquiry = Enquiry.objects.create(**enquiry_kwargs)
                except Exception:
                    enquiry = None

            profile = AssessmentParticipantProfile.objects.create(
                assessment=assessment,
                full_name=full_name,
                mobile=mobile,
                email=email,
                qualification=current_status,
                institution_name=institution_name,
                district="",
                city=city,
                current_status=current_status,
                career_interest="Cyber Safety Awareness",
                enquiry=enquiry,
                consent_given=True,
            )

            attempt = AssessmentAttempt.objects.create(
                assessment=assessment,
                participant_profile=profile,
                participant_name=full_name,
                participant_mobile=mobile,
                participant_email=email,
                status="started",
            )

            request.session["cyber_fraud_attempt_id"] = attempt.id

            return redirect(
                "assessments:cyber_fraud_quiz",
                attempt_id=attempt.id,
            )

    return render(
        request,
        "assessments/cyber_fraud_start.html",
        {
            "assessment": assessment,
        },
    )


@transaction.atomic
def cyber_fraud_quiz(request, attempt_id):

    language = request.session.get("cyber_fraud_language", "en")
    if language not in {"en", "mr", "hi"}:
        language = "en"

    if request.session.get("cyber_fraud_attempt_id") != attempt_id:
        messages.error(
            request,
            "Please register first to access the Cyber Fraud Awareness Test."
        )
        return redirect("assessments:cyber_fraud_start")

    attempt = get_object_or_404(
        AssessmentAttempt.objects.select_related(
            "assessment",
            "participant_profile",
        ),
        id=attempt_id,
        assessment__slug=CYBER_FRAUD_SLUG,
        status="started",
    )

    questions = list(
        attempt.assessment.questions
        .filter(is_active=True)
        .prefetch_related("options")
        .order_by("order", "id")
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
                    "assessments/cyber_fraud_quiz.html",
                    {
                        "attempt": attempt,
                        "assessment": attempt.assessment,
                        "questions": questions,
                        "language": language,
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
                    "assessments/cyber_fraud_quiz.html",
                    {
                        "attempt": attempt,
                        "assessment": attempt.assessment,
                        "questions": questions,
                        "language": language,
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
            band = "Cyber Safety Beginner"
            title = "Your Cyber Awareness Needs Attention"
            message = (
                "You may be vulnerable to common digital scams. "
                "Build the habit of pausing, verifying and protecting "
                "your banking and account credentials."
            )

        elif score <= 15:
            band = "Cyber Aware Learner"
            title = "You Are Building Cyber Awareness"
            message = (
                "You recognize several common fraud techniques, "
                "but a few situations could still put you at risk."
            )

        elif score <= 20:
            band = "Cyber Aware"
            title = "You Have Good Cyber Fraud Awareness"
            message = (
                "You understand many common digital fraud warning signs "
                "and safer online practices."
            )

        else:
            band = "Cyber Safety Champion"
            title = "Excellent Cyber Fraud Awareness"
            message = (
                "You demonstrate strong awareness of common cyber fraud "
                "techniques and safer digital behaviour."
            )

        recommendation = (
            "Pause before acting on urgent messages. Verify requests "
            "through official channels. Never share OTP, PIN, password "
            "or CVV. Avoid unknown links, QR codes and remote-access apps. "
            "If financial cyber fraud occurs, act quickly and report it "
            "through your bank/payment provider and official cybercrime channels."
        )

        AssessmentResult.objects.update_or_create(
            attempt=attempt,
            defaults={
                "result_band": band,
                "result_title": title,
                "result_message": message,
                "recommendation": recommendation,
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
            "assessments:cyber_fraud_result",
            attempt_id=attempt.id,
        )

    return render(
        request,
        "assessments/cyber_fraud_quiz.html",
        {
            "attempt": attempt,
            "assessment": attempt.assessment,
            "questions": questions,
            "language": language,
        },
    )


def cyber_fraud_result(request, attempt_id):

    language = request.session.get("cyber_fraud_language", "en")
    if language not in {"en", "mr", "hi"}:
        language = "en"


    if request.session.get("cyber_fraud_attempt_id") != attempt_id:
        messages.error(
            request,
            "Please register first to access your Cyber Awareness result."
        )
        return redirect("assessments:cyber_fraud_start")

    attempt = get_object_or_404(
        AssessmentAttempt.objects.select_related(
            "assessment",
            "participant_profile",
            "result",
        ),
        id=attempt_id,
        assessment__slug=CYBER_FRAUD_SLUG,
        status="completed",
    )

    return render(
        request,
        "assessments/cyber_fraud_result.html",
        {
            "attempt": attempt,
            "assessment": attempt.assessment,
            "result": attempt.result,
            "language": language,
        },
    )


# ============================================================
# MCTI CYBER FRAUD AWARENESS - MANAGEMENT DASHBOARD
# ============================================================

def cyber_fraud_dashboard(request):
    if not request.user.is_authenticated:
        return redirect("staff_login")

    if not (request.user.is_staff or request.user.is_superuser):
        return redirect("staff_login")

    from django.db.models import Avg
    from assessments.models import (
        Assessment,
        AssessmentAttempt,
        AssessmentParticipantProfile,
    )

    assessment = get_object_or_404(
        Assessment,
        slug="mcti-cyber-fraud-awareness-2026"
    )

    profiles = (
        AssessmentParticipantProfile.objects
        .filter(assessment=assessment)
        .order_by("-created_at")
    )

    attempts = (
        AssessmentAttempt.objects
        .filter(assessment=assessment)
        .select_related("participant_profile")
        .order_by("-started_at")
    )

    q = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()

    if q:
        from django.db.models import Q
        attempts = attempts.filter(
            Q(participant_name__icontains=q) |
            Q(participant_mobile__icontains=q) |
            Q(participant_email__icontains=q) |
            Q(participant_profile__full_name__icontains=q) |
            Q(participant_profile__mobile__icontains=q) |
            Q(participant_profile__city__icontains=q)
        )

    if status_filter:
        attempts = attempts.filter(status=status_filter)

    all_attempts = AssessmentAttempt.objects.filter(
        assessment=assessment
    )

    completed = all_attempts.filter(status="completed")

    avg_score = completed.aggregate(
        avg=Avg("percentage")
    )["avg"] or 0

    high_awareness = completed.filter(
        percentage__gte=80
    ).count()

    needs_awareness = completed.filter(
        percentage__lt=60
    ).count()

    context = {
        "assessment": assessment,
        "total_registrations": profiles.count(),
        "total_started": all_attempts.count(),
        "total_completed": completed.count(),
        "avg_score": round(float(avg_score), 1),
        "high_awareness": high_awareness,
        "needs_awareness": needs_awareness,
        "attempts": attempts[:500],
        "q": q,
        "status_filter": status_filter,
    }

    return render(
        request,
        "assessments/cyber_fraud_dashboard.html",
        context
    )
