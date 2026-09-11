from io import BytesIO
from xml.sax.saxutils import escape

from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone

from core.models import Student, Enquiry

from .models import (
    CareerProfile,
    Resume,
    AptitudeQuestion,
    AptitudeAttempt,
    AptitudeAnswer,
    CareerRecommendation,
    CareerRecommendationItem,
)

from .forms import (
    CareerProfileForm,
    ResumeForm,
    GuestCareerStartForm,
    EducationFormSet,
    ExperienceFormSet,
    ProjectFormSet,
    CertificationFormSet,
)


def career_home(request):
    return render(
        request,
        "career_tools/home.html"
    )


# =========================================================
# EXISTING MCTI STUDENT RESUME BUILDER
# =========================================================

@login_required
def resume_builder(request):

    student = Student.objects.filter(
        user=request.user
    ).first()

    profile = None

    if student:
        profile, created = CareerProfile.objects.get_or_create(
            student=student,
            defaults={
                "full_name": student.name,
                "mobile": student.mobile,
                "email": student.email or "",
                "city": "",
                "is_guest": False,
                "source": "MCTI Career Kit - Existing Student",
            }
        )

    resume = None

    if profile:
        resume = Resume.objects.filter(
            profile=profile,
            is_default=True
        ).first()

    if resume is None and profile:
        resume = Resume(
            profile=profile,
            is_default=True
        )

    # -----------------------------------------------------
    # POST
    # -----------------------------------------------------

    if request.method == "POST":

        profile_form = CareerProfileForm(
            request.POST,
            instance=profile
        )

        if student:
            profile_form.fields[
                "full_name"
            ].disabled = True

            profile_form.fields[
                "mobile"
            ].disabled = True

        resume_form = ResumeForm(
            request.POST,
            instance=resume
        )

        education_formset = EducationFormSet(
            request.POST,
            instance=resume,
            prefix="education"
        )

        experience_formset = ExperienceFormSet(
            request.POST,
            instance=resume,
            prefix="experience"
        )

        project_formset = ProjectFormSet(
            request.POST,
            instance=resume,
            prefix="project"
        )

        certification_formset = CertificationFormSet(
            request.POST,
            instance=resume,
            prefix="certification"
        )

        if (
            profile_form.is_valid()
            and resume_form.is_valid()
            and education_formset.is_valid()
            and experience_formset.is_valid()
            and project_formset.is_valid()
            and certification_formset.is_valid()
        ):

            profile = profile_form.save(
                commit=False
            )

            if student:
                profile.student = student
                profile.full_name = student.name
                profile.mobile = student.mobile
                profile.email = (
                    student.email
                    or profile.email
                )
                profile.is_guest = False
                profile.source = (
                    "MCTI Career Kit - Existing Student"
                )

            profile.save()

            resume = resume_form.save(
                commit=False
            )

            resume.profile = profile
            resume.is_default = True
            resume.save()

            education_formset.instance = resume
            education_formset.save()

            experience_formset.instance = resume
            experience_formset.save()

            project_formset.instance = resume
            project_formset.save()

            certification_formset.instance = resume
            certification_formset.save()

            return redirect(
                "career_tools:resume_builder"
            )

    # -----------------------------------------------------
    # GET
    # -----------------------------------------------------

    else:

        profile_form = CareerProfileForm(
            instance=profile
        )

        if student:
            profile_form.fields[
                "full_name"
            ].disabled = True

            profile_form.fields[
                "mobile"
            ].disabled = True

        resume_form = ResumeForm(
            instance=resume
        )

        education_formset = EducationFormSet(
            instance=resume,
            prefix="education"
        )

        experience_formset = ExperienceFormSet(
            instance=resume,
            prefix="experience"
        )

        project_formset = ProjectFormSet(
            instance=resume,
            prefix="project"
        )

        certification_formset = CertificationFormSet(
            instance=resume,
            prefix="certification"
        )

    context = {
        "profile_form": profile_form,
        "resume_form": resume_form,

        "education_formset": education_formset,
        "experience_formset": experience_formset,
        "project_formset": project_formset,
        "certification_formset": certification_formset,

        "profile": profile,
        "resume": resume,
        "student": student,
        "is_guest": False,
    }

    return render(
        request,
        "career_tools/resume_builder.html",
        context
    )


# =========================================================
# GUEST START / LEAD CAPTURE
# =========================================================

def guest_start(request):

    if request.method == "POST":

        form = GuestCareerStartForm(
            request.POST
        )

        if form.is_valid():

            full_name = (
                form.cleaned_data[
                    "full_name"
                ].strip()
            )

            mobile = (
                form.cleaned_data[
                    "mobile"
                ]
            )

            # ---------------------------------------------
            # EXISTING CRM ENQUIRY CHECK
            # ---------------------------------------------

            enquiry = (
                Enquiry.objects.filter(
                    mobile=mobile
                )
                .order_by("-created_at")
                .first()
            )

            if not enquiry:

                enquiry = Enquiry.objects.create(
                    name=full_name,
                    mobile=mobile,
                    status="new",
                    message=(
                        "Lead generated from "
                        "MCTI Career Kit - "
                        "Guest Resume Builder"
                    ),
                )

            # ---------------------------------------------
            # EXISTING GUEST PROFILE CHECK
            # ---------------------------------------------

            profile = (
                CareerProfile.objects.filter(
                    mobile=mobile,
                    student__isnull=True
                )
                .order_by("-updated_at")
                .first()
            )

            if profile:

                profile.full_name = full_name
                profile.mobile = mobile
                profile.enquiry = enquiry
                profile.is_guest = True
                profile.consent_given = True
                profile.source = (
                    "MCTI Career Kit - Guest"
                )

                profile.save()

            else:

                profile = CareerProfile.objects.create(
                    full_name=full_name,
                    mobile=mobile,
                    enquiry=enquiry,
                    is_guest=True,
                    consent_given=True,
                    source=(
                        "MCTI Career Kit - Guest"
                    ),
                )

            # ---------------------------------------------
            # SAVE GUEST PROFILE IN SESSION
            # ---------------------------------------------

            request.session[
                "career_guest_profile_id"
            ] = profile.id

            return redirect(
                "career_tools:guest_resume_builder"
            )

    else:
        form = GuestCareerStartForm()

    return render(
        request,
        "career_tools/guest_start.html",
        {
            "form": form
        }
    )


# =========================================================
# GUEST RESUME BUILDER
# =========================================================

def guest_resume_builder(request):

    profile_id = request.session.get(
        "career_guest_profile_id"
    )

    if not profile_id:

        return redirect(
            "career_tools:guest_start"
        )

    profile = CareerProfile.objects.filter(
        id=profile_id,
        is_guest=True
    ).first()

    if not profile:

        request.session.pop(
            "career_guest_profile_id",
            None
        )

        return redirect(
            "career_tools:guest_start"
        )

    resume = Resume.objects.filter(
        profile=profile,
        is_default=True
    ).first()

    if resume is None:
        resume = Resume(
            profile=profile,
            is_default=True
        )

    # -----------------------------------------------------
    # POST
    # -----------------------------------------------------

    if request.method == "POST":

        profile_form = CareerProfileForm(
            request.POST,
            instance=profile
        )

        resume_form = ResumeForm(
            request.POST,
            instance=resume
        )

        education_formset = EducationFormSet(
            request.POST,
            instance=resume,
            prefix="education"
        )

        experience_formset = ExperienceFormSet(
            request.POST,
            instance=resume,
            prefix="experience"
        )

        project_formset = ProjectFormSet(
            request.POST,
            instance=resume,
            prefix="project"
        )

        certification_formset = CertificationFormSet(
            request.POST,
            instance=resume,
            prefix="certification"
        )

        if (
            profile_form.is_valid()
            and resume_form.is_valid()
            and education_formset.is_valid()
            and experience_formset.is_valid()
            and project_formset.is_valid()
            and certification_formset.is_valid()
        ):

            profile = profile_form.save(
                commit=False
            )

            profile.is_guest = True
            profile.source = (
                "MCTI Career Kit - Guest"
            )

            profile.save()

            resume = resume_form.save(
                commit=False
            )

            resume.profile = profile
            resume.is_default = True
            resume.save()

            education_formset.instance = resume
            education_formset.save()

            experience_formset.instance = resume
            experience_formset.save()

            project_formset.instance = resume
            project_formset.save()

            certification_formset.instance = resume
            certification_formset.save()

            # ---------------------------------------------
            # UPDATE CRM WITH CAREER DATA
            # ---------------------------------------------

            if profile.enquiry:

                details = [
                    (
                        "Lead generated from "
                        "MCTI Career Kit"
                    ),
                    "Tool: Resume Builder",
                ]

                if profile.highest_qualification:
                    details.append(
                        "Qualification: "
                        + profile.highest_qualification
                    )

                if profile.career_interest:
                    details.append(
                        "Career Interest: "
                        + profile.career_interest
                    )

                if profile.preferred_job_role:
                    details.append(
                        "Preferred Job Role: "
                        + profile.preferred_job_role
                    )

                if profile.skills:
                    details.append(
                        "Skills: "
                        + profile.skills
                    )

                profile.enquiry.name = (
                    profile.full_name
                )

                profile.enquiry.email = (
                    profile.email or None
                )

                profile.enquiry.message = (
                    "\n".join(details)
                )

                profile.enquiry.save()

            return redirect(
                "career_tools:guest_resume_builder"
            )

    # -----------------------------------------------------
    # GET
    # -----------------------------------------------------

    else:

        profile_form = CareerProfileForm(
            instance=profile
        )

        resume_form = ResumeForm(
            instance=resume
        )

        education_formset = EducationFormSet(
            instance=resume,
            prefix="education"
        )

        experience_formset = ExperienceFormSet(
            instance=resume,
            prefix="experience"
        )

        project_formset = ProjectFormSet(
            instance=resume,
            prefix="project"
        )

        certification_formset = CertificationFormSet(
            instance=resume,
            prefix="certification"
        )

    context = {
        "profile_form": profile_form,
        "resume_form": resume_form,

        "education_formset": education_formset,
        "experience_formset": experience_formset,
        "project_formset": project_formset,
        "certification_formset": certification_formset,

        "profile": profile,
        "resume": resume,
        "student": None,
        "is_guest": True,
    }

    return render(
        request,
        "career_tools/resume_builder.html",
        context
    )
def download_resume_pdf(request):
    """
    Generate a clean, ATS-friendly professional resume PDF
    for either a logged-in MCTI student or a guest profile.
    """

    profile = None

    # -----------------------------------------------------
    # FIND CAREER PROFILE
    # -----------------------------------------------------

    if request.user.is_authenticated:
        student = Student.objects.filter(
            user=request.user
        ).first()

        if student:
            profile = CareerProfile.objects.filter(
                student=student
            ).first()

    if profile is None:
        profile_id = request.session.get(
            "career_guest_profile_id"
        )

        if profile_id:
            profile = CareerProfile.objects.filter(
                id=profile_id,
                is_guest=True,
            ).first()

    if profile is None:
        return HttpResponse(
            "Career profile not found.",
            status=404,
        )

    resume = (
        Resume.objects
        .filter(
            profile=profile,
            is_default=True,
        )
        .first()
    )

    if not resume:
        return HttpResponse(
            "Resume not found.",
            status=404,
        )

    # -----------------------------------------------------
    # SAFE TEXT HELPERS
    # -----------------------------------------------------

    def safe(value):
        if value is None:
            return ""
        return escape(str(value))

    def safe_multiline(value):
        return safe(value).replace("\n", "<br/>")

    def has_text(value):
        return bool(value and str(value).strip())

    # -----------------------------------------------------
    # PDF SETUP
    # -----------------------------------------------------

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=44,
        leftMargin=44,
        topMargin=36,
        bottomMargin=38,
        title=f"{profile.full_name} Resume",
        author="MCTI Career Kit",
    )

    page_width = A4[0] - 88

    styles = getSampleStyleSheet()

    orange = colors.HexColor("#F36A21")
    dark = colors.HexColor("#151515")
    body = colors.HexColor("#3F3F3F")
    grey = colors.HexColor("#6D6D6D")
    pale = colors.HexColor("#F3F3F3")

    name_style = ParagraphStyle(
        "ResumeV2Name",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=23,
        leading=27,
        textColor=dark,
        spaceAfter=3,
    )

    role_style = ParagraphStyle(
        "ResumeV2Role",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=orange,
        spaceAfter=6,
    )

    contact_style = ParagraphStyle(
        "ResumeV2Contact",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.8,
        leading=12,
        textColor=grey,
        spaceAfter=0,
    )

    section_style = ParagraphStyle(
        "ResumeV2Section",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=10.3,
        leading=13,
        textColor=dark,
        spaceBefore=0,
        spaceAfter=0,
    )

    normal_style = ParagraphStyle(
        "ResumeV2Normal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.3,
        leading=13.3,
        textColor=body,
        spaceAfter=4,
    )

    item_title_style = ParagraphStyle(
        "ResumeV2ItemTitle",
        parent=normal_style,
        fontName="Helvetica-Bold",
        fontSize=9.7,
        leading=13,
        textColor=dark,
        spaceAfter=1,
    )

    company_style = ParagraphStyle(
        "ResumeV2Company",
        parent=normal_style,
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=body,
        spaceAfter=1,
    )

    meta_style = ParagraphStyle(
        "ResumeV2Meta",
        parent=normal_style,
        fontSize=8.4,
        leading=11,
        textColor=grey,
        spaceAfter=3,
    )

    chip_style = ParagraphStyle(
        "ResumeV2Chip",
        parent=normal_style,
        fontSize=8.8,
        leading=12,
        textColor=body,
        spaceAfter=0,
    )

    story = []

    # -----------------------------------------------------
    # HEADER
    # -----------------------------------------------------

    story.append(
        Paragraph(
            safe(profile.full_name or "Your Name"),
            name_style,
        )
    )

    if has_text(profile.preferred_job_role):
        story.append(
            Paragraph(
                safe(profile.preferred_job_role),
                role_style,
            )
        )

    contact_parts = []

    if has_text(profile.mobile):
        contact_parts.append(safe(profile.mobile))

    if has_text(profile.email):
        contact_parts.append(safe(profile.email))

    if has_text(profile.city):
        contact_parts.append(safe(profile.city))

    if contact_parts:
        story.append(
            Paragraph(
                "  |  ".join(contact_parts),
                contact_style,
            )
        )

    story.append(Spacer(1, 8))

    story.append(
        Table(
            [[""]],
            colWidths=[page_width],
            rowHeights=[2],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), orange),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]),
        )
    )

    story.append(Spacer(1, 9))

    # -----------------------------------------------------
    # SECTION HELPERS
    # -----------------------------------------------------

    def add_section_header(title):
        heading = Table(
            [[
                Paragraph(
                    safe(title.upper()),
                    section_style,
                )
            ]],
            colWidths=[page_width],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), pale),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LINEBEFORE", (0, 0), (0, 0), 2.2, orange),
            ]),
        )

        story.append(Spacer(1, 6))
        story.append(heading)
        story.append(Spacer(1, 5))

    def add_text_section(title, content):
        if not has_text(content):
            return

        add_section_header(title)

        story.append(
            Paragraph(
                safe_multiline(content),
                normal_style,
            )
        )

    # -----------------------------------------------------
    # SUMMARY / OBJECTIVE
    # -----------------------------------------------------

    add_text_section(
        "Professional Summary",
        resume.professional_summary,
    )

    add_text_section(
        "Career Objective",
        resume.objective,
    )

    # -----------------------------------------------------
    # SKILLS / LANGUAGES
    # -----------------------------------------------------

    if has_text(profile.skills):
        add_section_header("Skills")
        story.append(
            Paragraph(
                safe_multiline(profile.skills),
                chip_style,
            )
        )

    if has_text(profile.languages):
        add_section_header("Languages")
        story.append(
            Paragraph(
                safe_multiline(profile.languages),
                chip_style,
            )
        )

    # -----------------------------------------------------
    # EDUCATION
    # -----------------------------------------------------

    education_items = resume.education.all().order_by(
        "order",
        "id",
    )

    if education_items.exists():
        add_section_header("Education")

        for item in education_items:
            block = []

            if has_text(item.qualification):
                block.append(
                    Paragraph(
                        safe(item.qualification),
                        item_title_style,
                    )
                )

            institute_parts = []

            if has_text(item.institute_name):
                institute_parts.append(
                    safe(item.institute_name)
                )

            if has_text(item.board_university):
                institute_parts.append(
                    safe(item.board_university)
                )

            if institute_parts:
                block.append(
                    Paragraph(
                        " | ".join(institute_parts),
                        company_style,
                    )
                )

            meta = []

            if item.start_year or item.end_year:
                years = " - ".join(
                    str(value)
                    for value in [
                        item.start_year,
                        item.end_year,
                    ]
                    if value
                )

                if years:
                    meta.append(
                        safe(years)
                    )

            if has_text(item.percentage_cgpa):
                meta.append(
                    safe(item.percentage_cgpa)
                )

            if meta:
                block.append(
                    Paragraph(
                        " | ".join(meta),
                        meta_style,
                    )
                )

            block.append(Spacer(1, 4))

            story.append(
                KeepTogether(block)
            )

    elif (
        has_text(profile.highest_qualification)
        or has_text(profile.college_name)
        or profile.passing_year
    ):
        # Fallback to the basic Career Profile education fields
        # when no detailed ResumeEducation entry exists.
        add_section_header("Education")

        if has_text(profile.highest_qualification):
            story.append(
                Paragraph(
                    safe(profile.highest_qualification),
                    item_title_style,
                )
            )

        if has_text(profile.college_name):
            story.append(
                Paragraph(
                    safe(profile.college_name),
                    company_style,
                )
            )

        if profile.passing_year:
            story.append(
                Paragraph(
                    safe(profile.passing_year),
                    meta_style,
                )
            )

    # -----------------------------------------------------
    # WORK EXPERIENCE
    # -----------------------------------------------------

    experience_items = resume.experience.all().order_by(
        "order",
        "id",
    )

    if experience_items.exists():
        add_section_header("Work Experience")

        for item in experience_items:
            block = []

            if has_text(item.job_title):
                block.append(
                    Paragraph(
                        safe(item.job_title),
                        item_title_style,
                    )
                )

            if has_text(item.company_name):
                block.append(
                    Paragraph(
                        safe(item.company_name),
                        company_style,
                    )
                )

            date_parts = []

            if item.start_date:
                date_parts.append(
                    item.start_date.strftime("%b %Y")
                )

            if item.currently_working:
                date_parts.append("Present")

            elif item.end_date:
                date_parts.append(
                    item.end_date.strftime("%b %Y")
                )

            if date_parts:
                block.append(
                    Paragraph(
                        safe(" - ".join(date_parts)),
                        meta_style,
                    )
                )

            if has_text(item.description):
                block.append(
                    Paragraph(
                        safe_multiline(item.description),
                        normal_style,
                    )
                )

            block.append(Spacer(1, 4))

            story.append(
                KeepTogether(block)
            )

    # -----------------------------------------------------
    # PROJECTS
    # -----------------------------------------------------

    project_items = resume.projects.all().order_by(
        "order",
        "id",
    )

    if project_items.exists():
        add_section_header("Projects")

        for item in project_items:
            block = []

            if has_text(item.project_title):
                block.append(
                    Paragraph(
                        safe(item.project_title),
                        item_title_style,
                    )
                )

            if has_text(item.project_url):
                block.append(
                    Paragraph(
                        safe(item.project_url),
                        meta_style,
                    )
                )

            if has_text(item.description):
                block.append(
                    Paragraph(
                        safe_multiline(item.description),
                        normal_style,
                    )
                )

            block.append(Spacer(1, 4))

            story.append(
                KeepTogether(block)
            )

    # -----------------------------------------------------
    # CERTIFICATIONS
    # -----------------------------------------------------

    certification_items = (
        resume.certifications.all()
        .order_by(
            "order",
            "id",
        )
    )

    if certification_items.exists():
        add_section_header("Certifications")

        for item in certification_items:
            block = []

            if has_text(item.certification_name):
                block.append(
                    Paragraph(
                        safe(item.certification_name),
                        item_title_style,
                    )
                )

            meta = []

            if has_text(item.issuing_organization):
                meta.append(
                    safe(item.issuing_organization)
                )

            if item.issue_year:
                meta.append(
                    safe(item.issue_year)
                )

            if meta:
                block.append(
                    Paragraph(
                        " | ".join(meta),
                        meta_style,
                    )
                )

            block.append(Spacer(1, 4))

            story.append(
                KeepTogether(block)
            )

    # -----------------------------------------------------
    # BUILD + DOWNLOAD
    # -----------------------------------------------------

    document.build(story)

    pdf = buffer.getvalue()
    buffer.close()

    safe_name = (
        profile.full_name
        .strip()
        .replace(" ", "_")
        or "resume"
    )

    response = HttpResponse(
        pdf,
        content_type="application/pdf",
    )

    response[
        "Content-Disposition"
    ] = (
        f'attachment; filename="{safe_name}_Resume.pdf"'
    )

    return response

# =========================================================
# APTITUDE TEST
# =========================================================

def _get_career_profile_for_request(request):
    """
    Return the CareerProfile for either:
    1) a logged-in MCTI student, or
    2) the current guest session.
    """
    profile = None

    if request.user.is_authenticated:
        student = Student.objects.filter(
            user=request.user
        ).first()

        if student:
            profile, created = CareerProfile.objects.get_or_create(
                student=student,
                defaults={
                    "full_name": student.name,
                    "mobile": student.mobile,
                    "email": student.email or "",
                    "is_guest": False,
                    "source": "MCTI Career Kit - Existing Student",
                },
            )

    if profile is None:
        profile_id = request.session.get(
            "career_guest_profile_id"
        )

        if profile_id:
            profile = CareerProfile.objects.filter(
                id=profile_id,
                is_guest=True,
            ).first()

    return profile


def aptitude_test(request):
    profile = _get_career_profile_for_request(request)

    if profile is None:
        if request.user.is_authenticated:
            return HttpResponse(
                "Career profile not found.",
                status=404,
            )

        return redirect(
            "career_tools:guest_start"
        )

    questions = list(
        AptitudeQuestion.objects.filter(
            is_active=True
        ).order_by(
            "category",
            "order",
            "id",
        )
    )

    if not questions:
        return HttpResponse(
            "No aptitude questions are available.",
            status=404,
        )

    if request.method == "POST":
        attempt = AptitudeAttempt.objects.create(
            profile=profile,
            total_questions=len(questions),
            status="started",
        )

        attempted_questions = 0
        correct_answers = 0

        category_correct = {
            "numerical": 0,
            "logical": 0,
            "verbal": 0,
            "computer": 0,
            "career": 0,
        }

        category_total = {
            "numerical": 0,
            "logical": 0,
            "verbal": 0,
            "computer": 0,
            "career": 0,
        }

        for question in questions:
            if question.category in category_total:
                category_total[question.category] += 1

            selected_option = request.POST.get(
                f"question_{question.id}"
            )

            if selected_option not in {
                "A", "B", "C", "D"
            }:
                continue

            attempted_questions += 1

            is_correct = (
                selected_option
                == question.correct_option
            )

            if is_correct:
                correct_answers += 1

                if question.category in category_correct:
                    category_correct[
                        question.category
                    ] += 1

            AptitudeAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_option=selected_option,
                is_correct=is_correct,
            )

        score_percentage = round(
            (
                correct_answers
                / len(questions)
            ) * 100,
            2,
        )

        def category_percentage(category):
            total = category_total.get(
                category,
                0,
            )

            if not total:
                return 0

            return round(
                (
                    category_correct.get(
                        category,
                        0,
                    )
                    / total
                ) * 100
            )

        attempt.attempted_questions = (
            attempted_questions
        )
        attempt.correct_answers = (
            correct_answers
        )
        attempt.score_percentage = (
            score_percentage
        )

        attempt.numerical_score = (
            category_percentage(
                "numerical"
            )
        )
        attempt.logical_score = (
            category_percentage(
                "logical"
            )
        )
        attempt.verbal_score = (
            category_percentage(
                "verbal"
            )
        )
        attempt.computer_score = (
            category_percentage(
                "computer"
            )
        )
        attempt.career_score = (
            category_percentage(
                "career"
            )
        )

        attempt.status = "completed"
        attempt.completed_at = timezone.now()
        attempt.save()

        # Keep useful aptitude information on the linked CRM lead.
        if profile.enquiry:
            aptitude_summary = (
                "\n\nAptitude Test Result"
                f"\nOverall Score: {attempt.score_percentage}%"
                f"\nNumerical: {attempt.numerical_score}%"
                f"\nLogical: {attempt.logical_score}%"
                f"\nVerbal: {attempt.verbal_score}%"
                f"\nComputer/Digital: {attempt.computer_score}%"
                f"\nCareer/Work: {attempt.career_score}%"
            )

            current_message = (
                profile.enquiry.message or ""
            ).rstrip()

            profile.enquiry.message = (
                current_message
                + aptitude_summary
            ).strip()

            profile.enquiry.save(
                update_fields=["message"]
            )

        return redirect(
            "career_tools:aptitude_result",
            attempt_id=attempt.id,
        )

    return render(
        request,
        "career_tools/aptitude_test.html",
        {
            "profile": profile,
            "questions": questions,
            "total_questions": len(questions),
        },
    )


def aptitude_result(request, attempt_id):
    profile = _get_career_profile_for_request(request)

    if profile is None:
        if request.user.is_authenticated:
            return HttpResponse(
                "Career profile not found.",
                status=404,
            )

        return redirect(
            "career_tools:guest_start"
        )

    attempt = AptitudeAttempt.objects.filter(
        id=attempt_id,
        profile=profile,
        status="completed",
    ).first()

    if not attempt:
        return HttpResponse(
            "Aptitude result not found.",
            status=404,
        )

    category_results = [
        {
            "name": "Numerical Aptitude",
            "score": attempt.numerical_score,
        },
        {
            "name": "Logical Reasoning",
            "score": attempt.logical_score,
        },
        {
            "name": "Verbal Ability",
            "score": attempt.verbal_score,
        },
        {
            "name": "Computer / Digital",
            "score": attempt.computer_score,
        },
        {
            "name": "Career / Work Aptitude",
            "score": attempt.career_score,
        },
    ]

    return render(
        request,
        "career_tools/aptitude_result.html",
        {
            "profile": profile,
            "attempt": attempt,
            "category_results": category_results,
        },
    )

# =========================================================
# CAREER RECOMMENDATION
# =========================================================

def career_recommendation(request, attempt_id):
    profile = _get_career_profile_for_request(request)

    if profile is None:
        if request.user.is_authenticated:
            return HttpResponse(
                "Career profile not found.",
                status=404,
            )

        return redirect(
            "career_tools:guest_start"
        )

    attempt = AptitudeAttempt.objects.filter(
        id=attempt_id,
        profile=profile,
        status="completed",
    ).first()

    if not attempt:
        return HttpResponse(
            "Completed aptitude attempt not found.",
            status=404,
        )

    # -----------------------------------------------------
    # SCORE INPUTS
    # -----------------------------------------------------

    scores = {
        "numerical": attempt.numerical_score,
        "logical": attempt.logical_score,
        "verbal": attempt.verbal_score,
        "computer": attempt.computer_score,
        "career": attempt.career_score,
    }

    strongest_key = max(
        scores,
        key=scores.get,
    )

    weakest_key = min(
        scores,
        key=scores.get,
    )

    area_names = {
        "numerical": "Numerical Aptitude",
        "logical": "Logical Reasoning",
        "verbal": "Verbal Ability",
        "computer": "Computer / Digital Aptitude",
        "career": "Career / Work Aptitude",
    }

    # -----------------------------------------------------
    # PROFILE KEYWORDS
    # -----------------------------------------------------

    profile_text = " ".join(
        [
            profile.career_interest or "",
            profile.preferred_job_role or "",
            profile.skills or "",
            profile.highest_qualification or "",
        ]
    ).lower()

    # -----------------------------------------------------
    # CAREER RULES
    # -----------------------------------------------------

    career_rules = [
        {
            "title": "MIS / Advanced Excel Executive",
            "weights": {
                "numerical": 0.25,
                "logical": 0.20,
                "verbal": 0.05,
                "computer": 0.35,
                "career": 0.15,
            },
            "keywords": [
                "excel",
                "mis",
                "data",
                "office",
            ],
            "reason": (
                "This role suits learners with good numerical, "
                "logical and computer aptitude and an interest in "
                "working with reports, spreadsheets and business data."
            ),
            "skills": (
                "Advanced Excel, Pivot Tables, Lookup Functions, "
                "Dashboards, Data Cleaning and basic Power BI."
            ),
            "course": "Advanced Excel",
            "next_step": (
                "Build 2-3 practical Excel/MIS projects and practise "
                "business reporting with real datasets."
            ),
        },
        {
            "title": "Accounting / Tally Executive",
            "weights": {
                "numerical": 0.35,
                "logical": 0.15,
                "verbal": 0.05,
                "computer": 0.20,
                "career": 0.25,
            },
            "keywords": [
                "account",
                "tally",
                "gst",
                "finance",
                "commerce",
            ],
            "reason": (
                "This path is suitable for candidates who are comfortable "
                "with numbers, structured work and computer-based business "
                "processes."
            ),
            "skills": (
                "Tally Prime, GST, accounting fundamentals, invoicing, "
                "Excel and business documentation."
            ),
            "course": "MIA / Tally Prime with GST",
            "next_step": (
                "Practise company creation, voucher entry, GST transactions "
                "and monthly accounting reports."
            ),
        },
        {
            "title": "Digital Marketing Executive",
            "weights": {
                "numerical": 0.05,
                "logical": 0.10,
                "verbal": 0.30,
                "computer": 0.30,
                "career": 0.25,
            },
            "keywords": [
                "marketing",
                "digital",
                "social media",
                "seo",
                "content",
            ],
            "reason": (
                "This career benefits from strong communication, digital "
                "comfort and practical workplace aptitude."
            ),
            "skills": (
                "Social Media Marketing, SEO, Google Ads, Meta Ads, "
                "Canva, content writing and analytics."
            ),
            "course": "Digital Marketing",
            "next_step": (
                "Create a small campaign portfolio with social posts, "
                "ad creatives and basic performance reports."
            ),
        },
        {
            "title": "Software / Programming Trainee",
            "weights": {
                "numerical": 0.20,
                "logical": 0.35,
                "verbal": 0.05,
                "computer": 0.30,
                "career": 0.10,
            },
            "keywords": [
                "python",
                "programming",
                "coding",
                "software",
                "developer",
                "c++",
                "java",
            ],
            "reason": (
                "Programming is a stronger match when logical reasoning, "
                "computer aptitude and problem-solving ability are high."
            ),
            "skills": (
                "Programming fundamentals, Python or C/C++, DSA basics, "
                "Git, SQL and project development."
            ),
            "course": "Programming / DSA & CS",
            "next_step": (
                "Complete programming fundamentals and build at least "
                "two small projects before moving to advanced development."
            ),
        },
        {
            "title": "Office Administration Executive",
            "weights": {
                "numerical": 0.05,
                "logical": 0.10,
                "verbal": 0.20,
                "computer": 0.30,
                "career": 0.35,
            },
            "keywords": [
                "admin",
                "office",
                "ms office",
                "back office",
                "operations",
            ],
            "reason": (
                "This path suits candidates with practical computer skills, "
                "workplace judgement and clear communication."
            ),
            "skills": (
                "MS Office, email communication, Excel, documentation, "
                "file management and office coordination."
            ),
            "course": "Advanced MS Office",
            "next_step": (
                "Practise professional Word documents, Excel reports, "
                "PowerPoint presentations and office email communication."
            ),
        },
        {
            "title": "Customer Support / Sales Executive",
            "weights": {
                "numerical": 0.05,
                "logical": 0.15,
                "verbal": 0.35,
                "computer": 0.10,
                "career": 0.35,
            },
            "keywords": [
                "sales",
                "customer",
                "support",
                "communication",
                "counselling",
            ],
            "reason": (
                "This role is a stronger fit for candidates with good verbal "
                "ability, practical judgement and confidence in working "
                "with people."
            ),
            "skills": (
                "Communication, CRM usage, customer handling, sales process, "
                "follow-up, presentation and basic Excel."
            ),
            "course": "Advanced MS Office + Communication Practice",
            "next_step": (
                "Practise customer conversations, CRM follow-ups and "
                "professional communication scenarios."
            ),
        },
    ]

    ranked = []

    for rule in career_rules:
        weighted_score = sum(
            scores[key] * weight
            for key, weight in rule["weights"].items()
        )

        keyword_bonus = 0

        if profile_text:
            for keyword in rule["keywords"]:
                if keyword in profile_text:
                    keyword_bonus = 7
                    break

        match_percentage = int(
            round(
                min(
                    98,
                    weighted_score + keyword_bonus,
                )
            )
        )

        ranked.append(
            {
                **rule,
                "match_percentage": match_percentage,
            }
        )

    ranked.sort(
        key=lambda item: item["match_percentage"],
        reverse=True,
    )

    top_three = ranked[:3]

    # -----------------------------------------------------
    # SAVE / REFRESH RECOMMENDATION
    # -----------------------------------------------------

    recommendation = CareerRecommendation.objects.filter(
        profile=profile,
        aptitude_attempt=attempt,
    ).first()

    if recommendation is None:
        recommendation = CareerRecommendation.objects.create(
            profile=profile,
            aptitude_attempt=attempt,
        )

    recommendation.strongest_area = area_names[
        strongest_key
    ]
    recommendation.improvement_area = area_names[
        weakest_key
    ]
    recommendation.overall_summary = (
        f"Your strongest aptitude area is "
        f"{recommendation.strongest_area}. "
        f"The main area to improve is "
        f"{recommendation.improvement_area}. "
        f"Based on your aptitude scores and career profile, "
        f"the following career paths are your strongest current matches."
    )
    recommendation.status = "generated"
    recommendation.save()

    recommendation.items.all().delete()

    for rank, item in enumerate(
        top_three,
        start=1,
    ):
        CareerRecommendationItem.objects.create(
            recommendation=recommendation,
            rank=rank,
            career_title=item["title"],
            match_percentage=item["match_percentage"],
            reason=item["reason"],
            skills_to_improve=item["skills"],
            recommended_course=item["course"],
            next_step=item["next_step"],
        )

    # -----------------------------------------------------
    # CRM UPDATE FOR GUEST / LINKED LEAD
    # -----------------------------------------------------

    if profile.enquiry:
        top_titles = ", ".join(
            item["title"]
            for item in top_three
        )

        crm_note = (
            "\n\nCareer Recommendation"
            f"\nStrongest Area: {recommendation.strongest_area}"
            f"\nImprovement Area: {recommendation.improvement_area}"
            f"\nTop Matches: {top_titles}"
        )

        current_message = (
            profile.enquiry.message or ""
        ).rstrip()

        # Avoid repeatedly appending the same recommendation block
        # every time the result page is refreshed.
        if "Career Recommendation" not in current_message:
            profile.enquiry.message = (
                current_message + crm_note
            ).strip()

            profile.enquiry.save(
                update_fields=["message"]
            )

    return render(
        request,
        "career_tools/career_recommendation.html",
        {
            "profile": profile,
            "attempt": attempt,
            "recommendation": recommendation,
            "items": recommendation.items.all(),
        },
    )

# =========================================================
# COUNSELLOR DASHBOARD - INTERNAL STAFF ONLY
# =========================================================

@staff_member_required(login_url="/admin/login/")
def counsellor_dashboard(request):
    """
    Internal MCTI counsellor dashboard.

    Shows Career Profiles together with the latest aptitude attempt,
    latest career recommendation and linked CRM enquiry.
    Accessible only to Django staff/admin users.
    """

    search_query = request.GET.get("q", "").strip()
    profile_type = request.GET.get("type", "").strip()

    profiles = (
        CareerProfile.objects
        .select_related(
            "student",
            "enquiry",
        )
        .prefetch_related(
            "aptitude_attempts",
            "career_recommendations__items",
        )
        .order_by("-updated_at")
    )

    if search_query:
        from django.db.models import Q

        profiles = profiles.filter(
            Q(full_name__icontains=search_query)
            | Q(mobile__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(career_interest__icontains=search_query)
            | Q(preferred_job_role__icontains=search_query)
        )

    if profile_type == "guest":
        profiles = profiles.filter(
            is_guest=True
        )

    elif profile_type == "student":
        profiles = profiles.filter(
            is_guest=False
        )

    rows = []

    for profile in profiles:
        latest_attempt = (
            profile.aptitude_attempts
            .filter(status="completed")
            .order_by("-completed_at", "-id")
            .first()
        )

        latest_recommendation = (
            profile.career_recommendations
            .order_by("-created_at", "-id")
            .first()
        )

        top_recommendations = []

        if latest_recommendation:
            top_recommendations = list(
                latest_recommendation.items
                .all()
                .order_by("rank", "id")[:3]
            )

        rows.append(
            {
                "profile": profile,
                "latest_attempt": latest_attempt,
                "latest_recommendation": latest_recommendation,
                "top_recommendations": top_recommendations,
            }
        )

    context = {
        "rows": rows,
        "search_query": search_query,
        "profile_type": profile_type,
        "total_profiles": len(rows),
    }

    return render(
        request,
        "career_tools/counsellor_dashboard.html",
        context,
    )


@staff_member_required(login_url="/admin/login/")
def counsellor_profile_detail(request, profile_id):
    """
    Internal detailed counselling view for one CareerProfile.
    """

    profile = (
        CareerProfile.objects
        .select_related(
            "student",
            "enquiry",
        )
        .filter(id=profile_id)
        .first()
    )

    if profile is None:
        return HttpResponse(
            "Career profile not found.",
            status=404,
        )

    attempts = (
        profile.aptitude_attempts
        .filter(status="completed")
        .order_by("-completed_at", "-id")
    )

    recommendations = (
        profile.career_recommendations
        .prefetch_related("items")
        .order_by("-created_at", "-id")
    )

    latest_attempt = attempts.first()
    latest_recommendation = recommendations.first()

    top_recommendations = []

    if latest_recommendation:
        top_recommendations = list(
            latest_recommendation.items
            .all()
            .order_by("rank", "id")[:3]
        )

    context = {
        "profile": profile,
        "enquiry": profile.enquiry,
        "latest_attempt": latest_attempt,
        "latest_recommendation": latest_recommendation,
        "top_recommendations": top_recommendations,
        "attempts": attempts[:10],
        "recommendations": recommendations[:10],
    }

    return render(
        request,
        "career_tools/counsellor_profile_detail.html",
        context,
    )

