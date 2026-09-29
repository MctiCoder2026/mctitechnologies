from django.shortcuts import render, redirect

from .forms import SSCStudentRegistrationForm
from .models import SSCStudent, SSCResource, SSCDownload


def ssc_exam_preparation(request):

    student = None
    student_id = request.session.get("ssc_student_id")

    if student_id:
        student = SSCStudent.objects.filter(id=student_id).first()

    if student:
        # Medium selected from dashboard has priority.
        selected_medium = (
            request.GET.get("medium")
            or request.session.get("ssc_selected_medium")
            or student.medium
            or "marathi"
        ).strip().lower()

        if selected_medium not in ("marathi", "english"):
            selected_medium = "marathi"

        # Remember selection for refresh/login flow.
        request.session["ssc_selected_medium"] = selected_medium

        # Keep student profile in sync with selected medium.
        if student.medium != selected_medium:
            student.medium = selected_medium
            student.save(update_fields=["medium"])

        resources = SSCResource.objects.filter(
            is_active=True,
            medium=selected_medium,
        )

        subject = request.GET.get("subject", "").strip()
        year = request.GET.get("year", "").strip()

        valid_subjects = dict(SSCResource.SUBJECT_CHOICES)

        if subject in valid_subjects:
            resources = resources.filter(subject=subject)

        if year in {"2022", "2023", "2024", "2025", "2026"}:
            resources = resources.filter(year=int(year))

        resources = resources.order_by("-year", "subject", "title")

        return render(
            request,
            "exam_preparation/ssc_resources.html",
            {
                "student": student,
                "resources": resources,
                "selected_medium": selected_medium,
            },
        )

    if request.method == "POST":
        form = SSCStudentRegistrationForm(request.POST)

        if form.is_valid():
            mobile = form.cleaned_data["mobile"]

            student = (
                SSCStudent.objects
                .filter(mobile=mobile)
                .order_by("-created_at")
                .first()
            )

            if student:
                student.full_name = form.cleaned_data["full_name"]
                student.school_name = form.cleaned_data["school_name"]
                student.medium = form.cleaned_data["medium"]
                student.city = form.cleaned_data.get("city", "")
                student.preferred_branch = form.cleaned_data.get(
                    "preferred_branch"
                )
                student.consent_given = True
                student.save()
            else:
                student = form.save()

            request.session["ssc_student_id"] = student.id
            request.session["ssc_selected_medium"] = student.medium

            return redirect("exam_preparation:ssc_exam_preparation")

    else:
        form = SSCStudentRegistrationForm()

    return render(
        request,
        "exam_preparation/ssc_start.html",
        {"form": form},
    )


def ssc_resource_open(request, resource_id):
    from django.shortcuts import get_object_or_404
    from django.http import FileResponse, Http404
    from .models import SSCDownload

    student_id = request.session.get("ssc_student_id")

    if not student_id:
        return redirect("exam_preparation:ssc_exam_preparation")

    student = get_object_or_404(SSCStudent, id=student_id)

    resource = get_object_or_404(
        SSCResource,
        id=resource_id,
        is_active=True,
        medium=student.medium,
    )

    SSCDownload.objects.create(
        student=student,
        resource=resource,
    )

    if resource.file:
        return FileResponse(
            resource.file.open("rb"),
            as_attachment=False,
            filename=resource.file.name.split("/")[-1],
        )

    if resource.source_url:
        return redirect(resource.source_url)

    raise Http404("Resource is currently unavailable.")


def ssc_management_dashboard(request):
    from django.db.models import Count, Avg, Max
    from assessments.models import AssessmentAttempt
    from core.views import is_admin_user

    if not request.user.is_authenticated:
        return redirect("staff_login")

    if not (request.user.is_superuser or is_admin_user(request.user)):
        return redirect("branch_dashboard")

    students = (
        SSCStudent.objects
        .select_related("preferred_branch")
        .annotate(resource_opens=Count("downloads"))
        .order_by("-created_at")
    )

    total_students = students.count()
    total_resource_opens = SSCDownload.objects.count()

    medium_counts = {
        "english": students.filter(medium="english").count(),
        "marathi": students.filter(medium="marathi").count(),
        "semi_english": students.filter(medium="semi_english").count(),
    }

    ssc_attempts = (
        AssessmentAttempt.objects
        .filter(assessment__assessment_type="exam_preparation")
        .select_related("assessment")
    )

    total_attempts = ssc_attempts.count()
    completed_attempts = ssc_attempts.filter(status="completed")
    total_completed = completed_attempts.count()

    avg_score = completed_attempts.aggregate(
        avg=Avg("percentage")
    )["avg"] or 0

    crm_leads = students.exclude(enquiry_id=None).count()

    subject_performance = (
        completed_attempts
        .values("assessment__title")
        .annotate(
            attempts=Count("id"),
            average=Avg("percentage"),
            best=Max("percentage"),
        )
        .order_by("-attempts", "assessment__title")
    )

    top_performers = (
        completed_attempts
        .order_by("-percentage", "-completed_at")[:15]
    )

    branch_counts = (
        students
        .values("preferred_branch__name")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    recent_downloads = (
        SSCDownload.objects
        .select_related("student", "resource")
        .order_by("-downloaded_at")[:20]
    )

    return render(
        request,
        "exam_preparation/ssc_management_dashboard.html",
        {
            "students": students,
            "total_students": total_students,
            "total_resource_opens": total_resource_opens,
            "medium_counts": medium_counts,
            "recent_downloads": recent_downloads,
            "total_attempts": total_attempts,
            "total_completed": total_completed,
            "avg_score": avg_score,
            "crm_leads": crm_leads,
            "subject_performance": subject_performance,
            "top_performers": top_performers,
            "branch_counts": branch_counts,
        },
    )


def ssc_send_to_enquiry(request, student_id):
    from django.contrib import messages
    from django.db import transaction
    from django.shortcuts import get_object_or_404
    from core.models import Enquiry, EnquiryActivity
    from core.views import is_admin_user

    if not request.user.is_authenticated or not is_admin_user(request.user):
        messages.error(request, "You are not authorized to perform this action.")
        return redirect("staff_login")

    if request.method != "POST":
        return redirect("exam_preparation:ssc_management_dashboard")

    with transaction.atomic():

        student = get_object_or_404(
            SSCStudent.objects.select_related(
                "preferred_branch",
                "enquiry",
            ),
            id=student_id,
        )

        # Already linked: never create another enquiry.
        if student.enquiry_id:
            messages.info(
                request,
                "This SSC student is already linked to CRM."
            )
            return redirect(
                "exam_preparation:ssc_management_dashboard"
            )

        enquiry = (
            Enquiry.objects
            .filter(mobile=student.mobile)
            .order_by("-created_at")
            .first()
        )

        created = False

        if enquiry is None:
            enquiry = Enquiry.objects.create(
                name=student.full_name,
                mobile=student.mobile,
                branch=student.preferred_branch or None,
                status="new",
                message=(
                    "Lead transferred manually from "
                    "MCTI SSC Exam Preparation 2026-27."
                ),
            )
            created = True

        elif not enquiry.branch and student.preferred_branch:
            enquiry.branch = student.preferred_branch
            enquiry.save(update_fields=["branch"])

        EnquiryActivity.objects.create(
            enquiry=enquiry,
            created_by=request.user,
            activity_type="note",
            message=(
                "SSC Exam Preparation lead transferred to CRM | "
                f"School: {student.school_name} | "
                f"Medium: {student.get_medium_display()} | "
                f"City: {student.city or '-'} | "
                f"Preferred Branch: {student.preferred_branch or '-'}"
            ),
        )

        student.enquiry = enquiry
        student.save(update_fields=["enquiry"])

    if created:
        messages.success(
            request,
            f"{student.full_name} sent to CRM as a new enquiry."
        )
    else:
        messages.success(
            request,
            f"{student.full_name} linked to existing CRM enquiry."
        )

    return redirect("exam_preparation:ssc_management_dashboard")


def ssc_mock_start(request, practice_key="math1"):
    import random
    from django.shortcuts import get_object_or_404
    from assessments.models import Assessment, AssessmentAttempt

    student_id = request.session.get("ssc_student_id")

    if not student_id:
        return redirect("exam_preparation:ssc_exam_preparation")

    student = get_object_or_404(SSCStudent, id=student_id)

    practice_slugs = {
        "math1": "ssc-marathi-mathematics-part-1-practice",
        "math2": "ssc-marathi-mathematics-part-2-practice",
        "marathi": "ssc-marathi-first-language-practice",
        "social1": "ssc-marathi-social-science-paper-1-practice",
        "geography": "ssc-marathi-geography-paper-2-practice",
        "science2": "ssc-marathi-science-technology-part-2-practice",
        "science1": "ssc-marathi-science-technology-part-1-practice",
        "english": "ssc-english-first-language-practice",
        "hindi": "ssc-hindi-second-third-language-practice",

        # English Medium
        "em_math1": "ssc-english-medium-mathematics-part-1-practice",
        "em_math2": "ssc-english-medium-mathematics-part-2-practice",
        "em_science1": "ssc-english-medium-science-technology-part-1-practice",
        "em_science2": "ssc-english-medium-science-technology-part-2-practice",
        "em_social1": "ssc-english-medium-social-science-paper-1-practice",
        "em_geography": "ssc-english-medium-geography-paper-2-practice",
        "em_english": "ssc-english-first-language-practice",
    }
    assessment_slug = practice_slugs.get(practice_key)
    if not assessment_slug:
        raise Http404("Invalid SSC practice test.")

    assessment = get_object_or_404(
        Assessment,
        slug=assessment_slug,
        assessment_type="exam_preparation",
        is_active=True,
    )

    question_ids = list(
        assessment.questions
        .filter(is_active=True)
        .values_list("id", flat=True)
    )

    if len(question_ids) < 25:
        from django.contrib import messages

        messages.info(
            request,
            "This subject question bank is being prepared. "
            "Please try another subject for now."
        )

        medium = "english" if practice_key.startswith("em_") else "marathi"

        return redirect(
            f"/ssc-exam-preparation/?medium={medium}"
        )

    selected_ids = random.sample(
        question_ids,
        min(25, len(question_ids)),
    )

    attempt = AssessmentAttempt.objects.create(
        assessment=assessment,
        participant_name=student.full_name,
        participant_mobile=student.mobile,
        status="started",
        selected_question_ids=selected_ids,
    )

    request.session["ssc_mock_attempt_id"] = attempt.id

    return redirect(
        "exam_preparation:ssc_mock_quiz",
        attempt_id=attempt.id,
    )

def ssc_mock_quiz(request, attempt_id):
    from django.shortcuts import get_object_or_404
    from django.db import transaction
    from django.utils import timezone
    from assessments.models import (
        AssessmentAttempt,
        AssessmentAnswer,
        AssessmentOption,
    )

    student_id = request.session.get("ssc_student_id")

    if not student_id:
        return redirect("exam_preparation:ssc_exam_preparation")

    student = get_object_or_404(SSCStudent, id=student_id)

    attempt = get_object_or_404(
        AssessmentAttempt.objects.select_related("assessment"),
        id=attempt_id,
        assessment__assessment_type="exam_preparation",
        assessment__slug__in=[
            "ssc-marathi-mathematics-part-1-practice",
            "ssc-marathi-mathematics-part-2-practice",
            "ssc-marathi-first-language-practice",
            "ssc-marathi-social-science-paper-1-practice",
            "ssc-marathi-geography-paper-2-practice",
            "ssc-marathi-science-technology-part-2-practice",
            "ssc-marathi-science-technology-part-1-practice",
            "ssc-english-first-language-practice",
            "ssc-hindi-second-third-language-practice",

            # English Medium
            "ssc-english-medium-mathematics-part-1-practice",
            "ssc-english-medium-mathematics-part-2-practice",
            "ssc-english-medium-science-technology-part-1-practice",
            "ssc-english-medium-science-technology-part-2-practice",
            "ssc-english-medium-social-science-paper-1-practice",
            "ssc-english-medium-geography-paper-2-practice",
        ],
        participant_mobile=student.mobile,
        status="started",
    )

    selected_ids = attempt.selected_question_ids or []

    question_map = {
        q.id: q
        for q in attempt.assessment.questions
        .filter(
            is_active=True,
            id__in=selected_ids,
        )
        .prefetch_related("options")
    }

    # Preserve the exact random order locked when attempt started.
    questions = [
        question_map[qid]
        for qid in selected_ids
        if qid in question_map
    ]

    if request.method == "POST":

        with transaction.atomic():

            score = 0
            total_marks = sum(q.marks for q in questions)

            for question in questions:

                option_id = request.POST.get(
                    f"question_{question.id}"
                )

                selected_option = None
                is_correct = False
                marks_awarded = 0

                if option_id:
                    selected_option = AssessmentOption.objects.filter(
                        id=option_id,
                        question=question,
                    ).first()

                if selected_option and selected_option.is_correct:
                    is_correct = True
                    marks_awarded = question.marks
                    score += question.marks

                AssessmentAnswer.objects.update_or_create(
                    attempt=attempt,
                    question=question,
                    defaults={
                        "selected_option": selected_option,
                        "is_correct": is_correct,
                        "marks_awarded": marks_awarded,
                    },
                )

            percentage = (
                round((score / total_marks) * 100, 2)
                if total_marks
                else 0
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
            "exam_preparation:ssc_mock_result",
            attempt_id=attempt.id,
        )

    return render(
        request,
        "exam_preparation/ssc_mock_quiz.html",
        {
            "student": student,
            "attempt": attempt,
            "assessment": attempt.assessment,
            "questions": questions,
        },
    )


def ssc_mock_result(request, attempt_id):
    from django.shortcuts import get_object_or_404
    from assessments.models import AssessmentAttempt

    student_id = request.session.get("ssc_student_id")

    if not student_id:
        return redirect("exam_preparation:ssc_exam_preparation")

    student = get_object_or_404(SSCStudent, id=student_id)

    attempt = get_object_or_404(
        AssessmentAttempt.objects.select_related("assessment"),
        id=attempt_id,
        assessment__assessment_type="exam_preparation",
        participant_mobile=student.mobile,
        status="completed",
    )

    answers = list(
        attempt.answers
        .select_related("question", "selected_option")
        .order_by("question__order")
    )

    attempted = sum(1 for a in answers if a.selected_option_id)
    correct = sum(1 for a in answers if a.is_correct)
    wrong = attempted - correct
    unanswered = len(answers) - attempted

    category_data = {}

    for answer in answers:
        category = answer.question.category or "General"

        if category not in category_data:
            category_data[category] = {
                "category": category,
                "total": 0,
                "attempted": 0,
                "correct": 0,
                "score": 0,
                "max_marks": 0,
            }

        item = category_data[category]
        item["total"] += 1
        item["max_marks"] += answer.question.marks

        if answer.selected_option_id:
            item["attempted"] += 1

        if answer.is_correct:
            item["correct"] += 1

        item["score"] += answer.marks_awarded

    category_analysis = []

    for item in category_data.values():
        item["percentage"] = (
            round((item["score"] / item["max_marks"]) * 100, 2)
            if item["max_marks"]
            else 0
        )

        if item["percentage"] >= 80:
            item["level"] = "Strong"
        elif item["percentage"] >= 60:
            item["level"] = "Good"
        elif item["percentage"] >= 40:
            item["level"] = "Needs Practice"
        else:
            item["level"] = "Focus Required"

        category_analysis.append(item)

    return render(
        request,
        "exam_preparation/ssc_mock_result.html",
        {
            "student": student,
            "attempt": attempt,
            "assessment": attempt.assessment,
            "attempted": attempted,
            "correct": correct,
            "wrong": wrong,
            "unanswered": unanswered,
            "category_analysis": category_analysis,
        },
    )


def ssc_student_login(request):
    from django.contrib import messages
    from .forms import SSCStudentLoginForm

    if request.method == "POST":
        form = SSCStudentLoginForm(request.POST)

        if form.is_valid():
            mobile = form.cleaned_data["mobile"]

            student = (
                SSCStudent.objects
                .filter(mobile=mobile)
                .order_by("-created_at")
                .first()
            )

            if student:
                request.session["ssc_student_id"] = student.id

                return redirect(
                    "exam_preparation:ssc_exam_preparation"
                )

            messages.error(
                request,
                "This mobile number is not registered. Please register free first."
            )

    else:
        form = SSCStudentLoginForm()

    return render(
        request,
        "exam_preparation/ssc_student_login.html",
        {"form": form},
    )


def ssc_student_logout(request):
    request.session.pop("ssc_student_id", None)
    request.session.pop("ssc_mock_attempt_id", None)

    return redirect("exam_preparation:ssc_student_login")
