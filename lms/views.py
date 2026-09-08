import io
import qrcode

from reportlab.lib.utils import ImageReader
from django.http import HttpResponse, HttpResponseForbidden
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.utils import timezone
from django.db.models import Max

from core.models import Student

from .models import (
    LMSModule,
    LMSTopic,
    LMSTopicContent,
    QuizQuestion,
    QuizAttempt,
    StudentTopicProgress,
    Certificate,
)


# =========================================================
# STUDENT LMS COURSE ACCESS
# =========================================================

def get_student_lms_courses(student):
    course = student.course

    if not course:
        return []

    if course.is_package:
        included_courses = list(
            course.included_courses.filter(
                is_active=True
            ).order_by("title")
        )

        if included_courses:
            return included_courses

    return [course]


def student_can_access_course(student, course):
    return any(
        allowed_course.id == course.id
        for allowed_course in get_student_lms_courses(student)
    )


# =========================================================
# MY COURSES
# =========================================================

@login_required
def my_courses(request):

    student = get_object_or_404(
        Student,
        user=request.user
    )

    enrolled_course = student.course
    courses = get_student_lms_courses(student)
    course_data = []

    for course in courses:

        modules = LMSModule.objects.filter(
            course=course,
            is_active=True
        ).order_by("order")

        all_topics = LMSTopic.objects.filter(
            module__course=course,
            module__is_active=True,
            is_active=True
        ).order_by(
            "module__order",
            "order"
        )

        total_topics = all_topics.count()

        completed_topics = StudentTopicProgress.objects.filter(
            student=student,
            topic__in=all_topics,
            is_completed=True
        ).count()

        progress_percent = (
            round((completed_topics / total_topics) * 100)
            if total_topics > 0
            else 0
        )

        continue_topic = None

        for topic in all_topics:
            progress = StudentTopicProgress.objects.filter(
                student=student,
                topic=topic
            ).first()

            if (
                progress
                and progress.is_unlocked
                and not progress.is_completed
            ):
                continue_topic = topic
                break

        module_data = []

        for module in modules:
            module_topics = LMSTopic.objects.filter(
                module=module,
                is_active=True
            )

            module_total = module_topics.count()

            module_completed = StudentTopicProgress.objects.filter(
                student=student,
                topic__in=module_topics,
                is_completed=True
            ).count()

            module_percent = (
                round((module_completed / module_total) * 100)
                if module_total > 0
                else 0
            )

            module_data.append({
                "module": module,
                "total": module_total,
                "completed": module_completed,
                "percent": module_percent,
                "is_completed": (
                    module_total > 0
                    and module_completed == module_total
                ),
            })

        course_data.append({
            "course": course,
            "module_data": module_data,
            "total_topics": total_topics,
            "completed_topics": completed_topics,
            "progress_percent": progress_percent,
            "continue_topic": continue_topic,
        })

    # Keep old template working until we update my_courses.html.
    first_course_data = course_data[0] if course_data else None

    context = {
        "student": student,
        "enrolled_course": enrolled_course,
        "is_package": bool(
            enrolled_course
            and enrolled_course.is_package
        ),
        "courses": courses,
        "course_data": course_data,

        "course": (
            first_course_data["course"]
            if first_course_data
            else enrolled_course
        ),
        "module_data": (
            first_course_data["module_data"]
            if first_course_data
            else []
        ),
        "total_topics": (
            first_course_data["total_topics"]
            if first_course_data
            else 0
        ),
        "completed_topics": (
            first_course_data["completed_topics"]
            if first_course_data
            else 0
        ),
        "progress_percent": (
            first_course_data["progress_percent"]
            if first_course_data
            else 0
        ),
        "continue_topic": (
            first_course_data["continue_topic"]
            if first_course_data
            else None
        ),
    }

    return render(
        request,
        "lms/my_courses.html",
        context
    )


# =========================================================
# MODULE TOPICS
# =========================================================

@login_required
def module_topics(request, module_id):

    student = get_object_or_404(
        Student,
        user=request.user
    )

    module = get_object_or_404(
        LMSModule,
        id=module_id,
        is_active=True
    )

    if not student_can_access_course(
        student,
        module.course
    ):
        return HttpResponseForbidden(
            "You do not have access to this course."
        )

    topics = list(
        module.topics.filter(
            is_active=True
        ).order_by("order")
    )

    first_module = LMSModule.objects.filter(
        course=module.course,
        is_active=True
    ).order_by("order").first()

    if (
        first_module
        and module.id == first_module.id
        and topics
    ):

        first_progress, created = (
            StudentTopicProgress.objects.get_or_create(
                student=student,
                topic=topics[0],
                defaults={
                    "is_unlocked": True
                }
            )
        )

        if not first_progress.is_unlocked:
            first_progress.is_unlocked = True
            first_progress.save()

    topic_data = []

    for topic in topics:

        progress = StudentTopicProgress.objects.filter(
            student=student,
            topic=topic
        ).first()

        topic_data.append({
            "topic": topic,
            "is_unlocked": (
                progress.is_unlocked
                if progress
                else False
            ),
            "is_completed": (
                progress.is_completed
                if progress
                else False
            ),
            "best_score": (
                progress.best_score
                if progress
                else 0
            ),
        })

    context = {
        "student": student,
        "module": module,
        "topic_data": topic_data,
    }

    return render(
        request,
        "lms/module_topics.html",
        context
    )


# =========================================================
# TOPIC DETAIL
# =========================================================

# =========================================================
# TOPIC DETAIL - MULTILINGUAL
# =========================================================

@login_required
def topic_detail(request, topic_id):

    student = get_object_or_404(
        Student,
        user=request.user
    )

    topic = get_object_or_404(
        LMSTopic,
        id=topic_id,
        is_active=True
    )

    if not student_can_access_course(
        student,
        topic.module.course
    ):
        return HttpResponseForbidden(
            "You do not have access to this course."
        )

    progress = StudentTopicProgress.objects.filter(
        student=student,
        topic=topic
    ).first()

    if not progress or not progress.is_unlocked:
        return HttpResponseForbidden(
            "This topic is locked. Complete the previous topic first."
        )

    # -------------------------------------------------
    # LANGUAGE
    # -------------------------------------------------

    languages = {
        "en": "English",
        "hi": "हिंदी",
        "mr": "मराठी",
    }

    selected_language = request.GET.get("lang", "en")

    if selected_language not in languages:
        selected_language = "en"

    # -------------------------------------------------
    # MULTILINGUAL CONTENT
    # -------------------------------------------------

    topic_content = LMSTopicContent.objects.filter(
        topic=topic,
        language=selected_language,
        is_active=True
    ).first()

    # Existing old content remains fallback for English
    if topic_content:

        description = topic_content.description
        video_url = topic_content.video_url
        notes_file = topic_content.notes_file
        practice_file = topic_content.practice_file

    elif selected_language == "en":

        description = topic.description
        video_url = topic.video_url
        notes_file = topic.notes_file
        practice_file = topic.practice_file

    else:

        description = ""
        video_url = ""
        notes_file = None
        practice_file = None

    context = {
        "student": student,
        "topic": topic,
        "progress": progress,

        "languages": languages,
        "selected_language": selected_language,
        "selected_language_name": languages[selected_language],

        "topic_content": topic_content,
        "description": description,
        "video_url": video_url,
        "notes_file": notes_file,
        "practice_file": practice_file,
    }

    return render(
        request,
        "lms/topic_detail.html",
        context
    )


# =========================================================
# TOPIC QUIZ
# =========================================================

@login_required
def topic_quiz(request, topic_id):

    student = get_object_or_404(
        Student,
        user=request.user
    )

    topic = get_object_or_404(
        LMSTopic,
        id=topic_id,
        is_active=True
    )

    if not student_can_access_course(
        student,
        topic.module.course
    ):
        return HttpResponseForbidden(
            "You do not have access to this course."
        )

    progress = StudentTopicProgress.objects.filter(
        student=student,
        topic=topic
    ).first()

    if not progress or not progress.is_unlocked:
        return HttpResponseForbidden(
            "This topic is locked. Complete the previous topic first."
        )

    # -------------------------------------------------
    # LANGUAGE SELECTION
    # -------------------------------------------------

    allowed_languages = {
        "en": "English",
        "hi": "हिंदी",
        "mr": "मराठी",
    }

    if request.method == "POST":
        selected_language = request.POST.get(
            "language",
            "en"
        )
    else:
        selected_language = request.GET.get(
            "lang",
            "en"
        )

    if selected_language not in allowed_languages:
        selected_language = "en"

    # -------------------------------------------------
    # QUESTIONS OF SELECTED LANGUAGE ONLY
    # -------------------------------------------------

    questions = QuizQuestion.objects.filter(
        topic=topic,
        language=selected_language,
        is_active=True
    ).order_by("order")[:5]

    total_questions = questions.count()

    # -------------------------------------------------
    # SUBMIT QUIZ
    # -------------------------------------------------

    if request.method == "POST":

        score = 0

        for question in questions:

            selected_answer = request.POST.get(
                f"question_{question.id}"
            )

            if selected_answer == question.correct_answer:
                score += 1

        # -------------------------------------------------
        # PASS RULE - 3 OUT OF 5
        # -------------------------------------------------

        passed = score >= 3

        QuizAttempt.objects.create(
            student=student,
            topic=topic,
            score=score,
            total_questions=total_questions,
            passed=passed
        )

        progress, created = (
            StudentTopicProgress.objects.get_or_create(
                student=student,
                topic=topic,
                defaults={
                    "is_unlocked": True,
                    "is_completed": False,
                    "best_score": 0,
                    "total_questions": total_questions,
                    "attempts": 0,
                }
            )
        )

        progress.is_unlocked = True
        progress.attempts += 1
        progress.total_questions = total_questions
        progress.last_attempt_at = timezone.now()

        if score > progress.best_score:
            progress.best_score = score

        if passed:

            progress.is_completed = True

            if not progress.completed_at:
                progress.completed_at = timezone.now()

        progress.save()

        # -------------------------------------------------
        # UNLOCK NEXT TOPIC
        # -------------------------------------------------

        if passed:

            next_topic = LMSTopic.objects.filter(
                module=topic.module,
                is_active=True,
                order__gt=topic.order
            ).order_by("order").first()

            if next_topic:

                next_progress, created = (
                    StudentTopicProgress.objects.get_or_create(
                        student=student,
                        topic=next_topic,
                        defaults={
                            "is_unlocked": True
                        }
                    )
                )

                if not next_progress.is_unlocked:
                    next_progress.is_unlocked = True
                    next_progress.save()

            else:

                # -----------------------------------------
                # NEXT MODULE FIRST TOPIC
                # -----------------------------------------

                next_module = LMSModule.objects.filter(
                    course=topic.module.course,
                    is_active=True,
                    order__gt=topic.module.order
                ).order_by("order").first()

                if next_module:

                    first_topic_next_module = (
                        LMSTopic.objects.filter(
                            module=next_module,
                            is_active=True
                        ).order_by("order").first()
                    )

                    if first_topic_next_module:

                        next_progress, created = (
                            StudentTopicProgress.objects.get_or_create(
                                student=student,
                                topic=first_topic_next_module,
                                defaults={
                                    "is_unlocked": True
                                }
                            )
                        )

                        if not next_progress.is_unlocked:
                            next_progress.is_unlocked = True
                            next_progress.save()

        context = {
            "student": student,
            "topic": topic,
            "score": score,
            "total_questions": total_questions,
            "passed": passed,
            "selected_language": selected_language,
            "selected_language_name": allowed_languages[selected_language],
        }

        return render(
            request,
            "lms/quiz_result.html",
            context
        )

    context = {
        "student": student,
        "topic": topic,
        "questions": questions,
        "total_questions": total_questions,
        "selected_language": selected_language,
        "selected_language_name": allowed_languages[selected_language],
        "languages": allowed_languages,
    }

    return render(
        request,
        "lms/topic_quiz.html",
        context
    )


# =========================================================
# QUIZ HISTORY
# =========================================================

@login_required
def quiz_history(request):

    student = get_object_or_404(
        Student,
        user=request.user
    )

    attempts = QuizAttempt.objects.filter(
        student=student
    ).select_related(
        "topic",
        "topic__module"
    ).order_by(
        "-attempted_at"
    )

    progress_records = StudentTopicProgress.objects.filter(
        student=student
    ).select_related(
        "topic",
        "topic__module"
    ).order_by(
        "topic__module__order",
        "topic__order"
    )

    context = {
        "student": student,
        "attempts": attempts,
        "progress_records": progress_records,
    }

    return render(
        request,
        "lms/quiz_history.html",
        context
    )


# =========================================================
# MY PROGRESS
# =========================================================

@login_required
def my_progress(request):

    student = get_object_or_404(
        Student,
        user=request.user
    )

    course = student.course

    modules = LMSModule.objects.filter(
        course=course,
        is_active=True
    ).order_by("order")

    all_topics = LMSTopic.objects.filter(
        module__course=course,
        module__is_active=True,
        is_active=True
    )

    total_topics = all_topics.count()

    completed_topics = StudentTopicProgress.objects.filter(
        student=student,
        topic__in=all_topics,
        is_completed=True
    ).count()

    if total_topics > 0:

        progress_percent = round(
            (completed_topics / total_topics) * 100
        )

    else:

        progress_percent = 0

    # -------------------------------------------------
    # CERTIFICATE ELIGIBILITY - 80%
    # -------------------------------------------------

    certificate_eligible = (
        total_topics > 0
        and progress_percent >= 1
    )

    # -------------------------------------------------
    # QUIZ PERFORMANCE
    # -------------------------------------------------

    course_attempts = QuizAttempt.objects.filter(
        student=student,
        topic__module__course=course
    )

    total_attempts = course_attempts.count()

    passed_attempts = course_attempts.filter(
        passed=True
    ).count()

    best_attempt = course_attempts.order_by(
        "-score"
    ).first()

    best_score = (
        best_attempt.score
        if best_attempt
        else 0
    )

    # -------------------------------------------------
    # MODULE-WISE PROGRESS
    # -------------------------------------------------

    module_data = []

    for module in modules:

        topics = LMSTopic.objects.filter(
            module=module,
            is_active=True
        )

        total = topics.count()

        completed = StudentTopicProgress.objects.filter(
            student=student,
            topic__in=topics,
            is_completed=True
        ).count()

        if total > 0:

            percent = round(
                (completed / total) * 100
            )

        else:

            percent = 0

        module_data.append({
            "module": module,
            "total": total,
            "completed": completed,
            "percent": percent,
        })

    context = {
        "student": student,
        "course": course,
        "total_topics": total_topics,
        "completed_topics": completed_topics,
        "progress_percent": progress_percent,
        "certificate_eligible": certificate_eligible,
        "total_attempts": total_attempts,
        "passed_attempts": passed_attempts,
        "best_score": best_score,
        "module_data": module_data,
    }

    return render(
        request,
        "lms/my_progress.html",
        context
    )


# =========================================================
# CERTIFICATES
# =========================================================

@login_required
def certificates(request):

    student = get_object_or_404(
        Student,
        user=request.user
    )

    course = student.course

    all_topics = LMSTopic.objects.filter(
        module__course=course,
        module__is_active=True,
        is_active=True
    )

    total_topics = all_topics.count()

    completed_topics = StudentTopicProgress.objects.filter(
        student=student,
        topic__in=all_topics,
        is_completed=True
    ).count()

    if total_topics > 0:

        progress_percent = round(
            (completed_topics / total_topics) * 100
        )

    else:

        progress_percent = 0

    certificate_eligible = (
        total_topics > 0
        and progress_percent >= 1
    )

    remaining_percent = max(
        0,
        1 - progress_percent
    )

    context = {
        "student": student,
        "course": course,
        "total_topics": total_topics,
        "completed_topics": completed_topics,
        "progress_percent": progress_percent,
        "certificate_eligible": certificate_eligible,
        "remaining_percent": remaining_percent,
    }

    return render(
        request,
        "lms/certificates.html",
        context
    )


# =========================================================
# ADMIN - STUDENT PERFORMANCE REPORT
# =========================================================

@staff_member_required
def student_performance_report(request):

    search_query = request.GET.get(
        "q",
        ""
    ).strip()

    branch_filter = request.GET.get(
        "branch",
        ""
    ).strip()

    course_filter = request.GET.get(
        "course",
        ""
    ).strip()

    students = Student.objects.select_related(
        "course"
    ).all().order_by(
        "name"
    )

    # -------------------------------------------------
    # STUDENT SEARCH
    # -------------------------------------------------

    if search_query:

        students = students.filter(
            name__icontains=search_query
        )

    # -------------------------------------------------
    # BRANCH FILTER
    # -------------------------------------------------

    if branch_filter:

        students = students.filter(
            branch=branch_filter
        )

    # -------------------------------------------------
    # COURSE FILTER
    # -------------------------------------------------

    if course_filter:

        students = students.filter(
            course_id=course_filter
        )

    # -------------------------------------------------
    # BRANCH OPTIONS
    # -------------------------------------------------

    branches = Student.objects.exclude(
        branch=""
    ).exclude(
        branch__isnull=True
    ).values_list(
        "branch",
        flat=True
    ).distinct().order_by(
        "branch"
    )

    # -------------------------------------------------
    # COURSE OPTIONS
    # -------------------------------------------------

    courses = LMSModule.objects.filter(
        is_active=True
    ).values(
        "course_id",
        "course__title"
    ).distinct().order_by(
        "course__title"
    )

    report_data = []

    # -------------------------------------------------
    # BUILD STUDENT PERFORMANCE DATA
    # -------------------------------------------------

    for student in students:

        if not student.course:
            continue

        course_topics = LMSTopic.objects.filter(
            module__course=student.course,
            module__is_active=True,
            is_active=True
        )

        total_topics = course_topics.count()

        completed_topics = StudentTopicProgress.objects.filter(
            student=student,
            topic__in=course_topics,
            is_completed=True
        ).count()

        if total_topics > 0:

            progress_percent = round(
                (completed_topics / total_topics) * 100
            )

        else:

            progress_percent = 0

        # ---------------------------------------------
        # CERTIFICATE ELIGIBILITY
        # ---------------------------------------------

        certificate_eligible = (
            total_topics > 0
            and progress_percent >= 1
        )

        attempts = QuizAttempt.objects.filter(
            student=student,
            topic__in=course_topics
        )

        total_attempts = attempts.count()

        passed_attempts = attempts.filter(
            passed=True
        ).count()

        best_score_data = attempts.aggregate(
            best_score=Max("score")
        )

        best_score = (
            best_score_data["best_score"]
            or 0
        )

        last_attempt = attempts.order_by(
            "-attempted_at"
        ).first()

        last_activity = (
            last_attempt.attempted_at
            if last_attempt
            else None
        )

        report_data.append({
            "student": student,
            "course": student.course,
            "total_topics": total_topics,
            "completed_topics": completed_topics,
            "progress_percent": progress_percent,
            "total_attempts": total_attempts,
            "passed_attempts": passed_attempts,
            "best_score": best_score,
            "last_activity": last_activity,
            "certificate_eligible": certificate_eligible,
        })

    context = {
        "report_data": report_data,
        "branches": branches,
        "courses": courses,
        "search_query": search_query,
        "branch_filter": branch_filter,
        "course_filter": course_filter,
    }

    return render(
        request,
        "lms/admin/student_performance_report.html",
        context
    )
# =========================================================
# DOWNLOAD CERTIFICATE PDF
# =========================================================

@login_required
def download_certificate(request):

    student = get_object_or_404(
        Student,
        user=request.user
    )

    course = student.course

    if not course:

        return HttpResponseForbidden(
            "No course is assigned to this student."
        )

    # -------------------------------------------------
    # COURSE TOPICS
    # -------------------------------------------------

    all_topics = LMSTopic.objects.filter(
        module__course=course,
        module__is_active=True,
        is_active=True
    )

    total_topics = all_topics.count()

    completed_topics = StudentTopicProgress.objects.filter(
        student=student,
        topic__in=all_topics,
        is_completed=True
    ).count()

    # -------------------------------------------------
    # PROGRESS
    # -------------------------------------------------

    if total_topics > 0:

        progress_percent = round(
            (completed_topics / total_topics) * 100
        )

    else:

        progress_percent = 0

    # -------------------------------------------------
    # CERTIFICATE ELIGIBILITY
    # -------------------------------------------------

    certificate_eligible = (
        total_topics > 0
        and progress_percent >= 1
    )

    if not certificate_eligible:

        return HttpResponseForbidden(
            "Certificate is available only after completing at least 80% of the course."
        )

    # -------------------------------------------------
    # CERTIFICATE INFORMATION
    # -------------------------------------------------

    certificate_number = (
    f"MCTI-CERT-"
    f"{student.id:05d}-"
    f"{course.id:03d}"
    )

    certificate, created = Certificate.objects.get_or_create(
        student=student,
        course=course,
        defaults={
            "certificate_number": certificate_number,
        }
    )

    certificate_number = certificate.certificate_number
    issue_date = certificate.issue_date
    verification_url = (
    "https://mctitechnologies.com"
    f"/lms/certificate/verify/{certificate.verification_token}/"
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
        back_color="white"
    )

    qr_buffer = io.BytesIO()
    qr_image.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)

    qr_reader = ImageReader(qr_buffer)

    # -------------------------------------------------
    # PDF RESPONSE
    # -------------------------------------------------

    response = HttpResponse(
        content_type="application/pdf"
    )

    safe_student_name = (
        student.name
        .replace(" ", "_")
        .replace("/", "-")
    )

    response[
        "Content-Disposition"
    ] = (
        f'attachment; '
        f'filename="MCTI_Certificate_{safe_student_name}.pdf"'
    )

    # -------------------------------------------------
    # PAGE SETUP
    # -------------------------------------------------

    page_width, page_height = landscape(A4)

    pdf = canvas.Canvas(
        response,
        pagesize=landscape(A4)
    )

    # -------------------------------------------------
    # BACKGROUND
    # -------------------------------------------------

    pdf.setFillColor(
        colors.HexColor("#FFFDF8")
    )

    pdf.rect(
        0,
        0,
        page_width,
        page_height,
        fill=1,
        stroke=0
    )
    # -------------------------------------------------
    # SUBTLE MCTI BACKGROUND WATERMARK PATTERN
    # -------------------------------------------------

    pdf.saveState()

    pdf.setFillColor(
        colors.HexColor("#F7E8D8")
    )

    pdf.setFont(
        "Helvetica-Bold",
        7
    )

    start_x = 45
    start_y = 45
    end_x = page_width - 45
    end_y = page_height - 45

    y = start_y

    while y < end_y:

        x = start_x

        while x < end_x:

            pdf.drawString(
                x,
                y,
                "MCTI"
            )

            x += 55

        y += 28

    pdf.restoreState()
    # -------------------------------------------------
    # OUTER NAVY BORDER
    # -------------------------------------------------

    pdf.setStrokeColor(
        colors.HexColor("#111827")
    )

    pdf.setLineWidth(4)

    pdf.rect(
        20,
        20,
        page_width - 40,
        page_height - 40,
        fill=0,
        stroke=1
    )

    # -------------------------------------------------
    # INNER ORANGE BORDER
    # -------------------------------------------------

    pdf.setStrokeColor(
        colors.HexColor("#FF6B00")
    )

    pdf.setLineWidth(1.5)

    pdf.rect(
        30,
        30,
        page_width - 60,
        page_height - 60,
        fill=0,
        stroke=1
    )
    # -------------------------------------------------
    # ISO CERTIFICATION TEXT
    # -------------------------------------------------

    pdf.setFillColor(
        colors.HexColor("#64748B")
    )

    pdf.setFont(
        "Helvetica-Bold",
        8
    )

    pdf.drawRightString(
        page_width - 45,
        page_height - 48,
        "ISO 9001:2015"
    )
    # -------------------------------------------------
    # TOP BRAND
    # -------------------------------------------------

    pdf.setFillColor(
        colors.HexColor("#FF6B00")
    )

    pdf.setFont(
        "Helvetica-Bold",
        24
    )

    pdf.drawCentredString(
        page_width / 2,
        page_height - 72,
        "MCTI"
    )

    pdf.setFillColor(
        colors.HexColor("#111827")
    )

    pdf.setFont(
        "Helvetica-Bold",
        13
    )

    pdf.drawCentredString(
        page_width / 2,
        page_height - 92,
        "MAHARASHTRA COMPUTER TRAINING INSTITUTE"
    )

    pdf.setFont(
        "Helvetica",
        9
    )

    pdf.setFillColor(
        colors.HexColor("#64748B")
    )

    pdf.drawCentredString(
        page_width / 2,
        page_height - 108,
        "Education | Skills | Career Development"
    )

    # -------------------------------------------------
    # CERTIFICATE TITLE
    # -------------------------------------------------

    pdf.setFillColor(
        colors.HexColor("#111827")
    )

    pdf.setFont(
        "Times-Bold",
        32
    )

    pdf.drawCentredString(
        page_width / 2,
        page_height - 155,
        "CERTIFICATE"
    )

    pdf.setFillColor(
        colors.HexColor("#FF6B00")
    )

    pdf.setFont(
        "Helvetica-Bold",
        13
    )

    pdf.drawCentredString(
        page_width / 2,
        page_height - 178,
        "OF COURSE COMPLETION"
    )

    # -------------------------------------------------
    # CERTIFY TEXT
    # -------------------------------------------------

    pdf.setFillColor(
        colors.HexColor("#475569")
    )

    pdf.setFont(
        "Helvetica",
        11
    )

    pdf.drawCentredString(
        page_width / 2,
        page_height - 220,
        "This is to certify that"
    )

    # -------------------------------------------------
    # STUDENT NAME
    # -------------------------------------------------

    student_name = student.name.upper()

    student_font_size = 25

    while (
        stringWidth(
            student_name,
            "Times-Bold",
            student_font_size
        )
        > page_width - 180
        and student_font_size > 15
    ):

        student_font_size -= 1

    pdf.setFillColor(
        colors.HexColor("#FF6B00")
    )

    pdf.setFont(
        "Times-Bold",
        student_font_size
    )

    pdf.drawCentredString(
        page_width / 2,
        page_height - 260,
        student_name
    )

    # -------------------------------------------------
    # COMPLETION TEXT
    # -------------------------------------------------

    pdf.setFillColor(
        colors.HexColor("#475569")
    )

    pdf.setFont(
        "Helvetica",
        11
    )

    pdf.drawCentredString(
        page_width / 2,
        page_height - 292,
        "has successfully achieved the required learning progress"
    )

    pdf.drawCentredString(
        page_width / 2,
        page_height - 310,
        "and completed the prescribed learning requirements for"
    )

    # -------------------------------------------------
    # COURSE NAME
    # -------------------------------------------------

    course_name = course.title.upper()

    course_font_size = 22

    while (
        stringWidth(
            course_name,
            "Helvetica-Bold",
            course_font_size
        )
        > page_width - 180
        and course_font_size > 14
    ):

        course_font_size -= 1

    pdf.setFillColor(
        colors.HexColor("#111827")
    )

    pdf.setFont(
        "Helvetica-Bold",
        course_font_size
    )

    pdf.drawCentredString(
        page_width / 2,
        page_height - 350,
        course_name
    )

    # -------------------------------------------------
    # PROGRESS
    # -------------------------------------------------

    pdf.setFillColor(
        colors.HexColor("#475569")
    )

    pdf.setFont(
        "Helvetica",
        10
    )

    pdf.drawCentredString(
        page_width / 2,
        page_height - 380,
        f"Course Progress Achieved: {progress_percent}%"
    )

    # -------------------------------------------------
    # DIVIDER
    # -------------------------------------------------

    pdf.setStrokeColor(
        colors.HexColor("#E5E7EB")
    )

    pdf.setLineWidth(1)

    pdf.line(
        110,
        155,
        page_width - 110,
        155
    )

    # -------------------------------------------------
    # CERTIFICATE NUMBER
    # -------------------------------------------------

    pdf.setFillColor(
        colors.HexColor("#64748B")
    )

    pdf.setFont(
        "Helvetica",
        8
    )

    pdf.drawString(
        60,
        116,
        "Certificate No."
    )

    pdf.setFillColor(
        colors.HexColor("#111827")
    )

    pdf.setFont(
        "Helvetica-Bold",
        9
    )

    pdf.drawString(
        60,
        101,
        certificate_number
    )

    # -------------------------------------------------
    # STUDENT ID
    # -------------------------------------------------

    pdf.setFillColor(
        colors.HexColor("#64748B")
    )

    pdf.setFont(
        "Helvetica",
        8
    )

    pdf.drawString(
        250,
        116,
        "Student ID"
    )

    pdf.setFillColor(
        colors.HexColor("#111827")
    )

    pdf.setFont(
        "Helvetica-Bold",
        9
    )

    pdf.drawString(
        250,
        101,
        student.student_id
    )

    # -------------------------------------------------
    # ISSUE DATE
    # -------------------------------------------------

    pdf.setFillColor(
        colors.HexColor("#64748B")
    )

    pdf.setFont(
        "Helvetica",
        8
    )

    pdf.drawString(
        430,
        116,
        "Issue Date"
    )

    pdf.setFillColor(
        colors.HexColor("#111827")
    )

    pdf.setFont(
        "Helvetica-Bold",
        9
    )

    pdf.drawString(
        430,
        101,
        issue_date.strftime("%d %B %Y")
    )

        # -------------------------------------------------
    # CERTIFICATE VERIFICATION QR
    # -------------------------------------------------

    qr_size = 70

    pdf.drawImage(
        qr_reader,
        page_width - 300,
        72,
        width=qr_size,
        height=qr_size,
        preserveAspectRatio=True,
        mask="auto"
    )

    pdf.setFillColor(
        colors.HexColor("#64748B")
    )

    pdf.setFont(
        "Helvetica",
        7
    )

    pdf.drawCentredString(
        page_width - 265,
        62,
        "Scan to verify"
    )

    # -------------------------------------------------
    # DIRECTOR SIGNATURE AREA
    # -------------------------------------------------

    pdf.setStrokeColor(
        colors.HexColor("#111827")
    )

    pdf.line(
        page_width - 210,
        105,
        page_width - 70,
        105
    )

    pdf.setFillColor(
        colors.HexColor("#111827")
    )

    pdf.setFont(
        "Helvetica-Bold",
        9
    )

    pdf.drawCentredString(
        page_width - 140,
        88,
        "DIRECTOR"
    )

    pdf.setFont(
        "Helvetica",
        7
    )

    pdf.setFillColor(
        colors.HexColor("#64748B")
    )

    pdf.drawCentredString(
        page_width - 140,
        76,
        "MCTI"
    )

    # -------------------------------------------------
    # FOOTER
    # -------------------------------------------------

    pdf.setFillColor(
        colors.HexColor("#64748B")
    )

    pdf.setFont(
        "Helvetica",
        7
    )

    pdf.drawCentredString(
        page_width / 2,
        48,
        "Maharashtra Computer Training Institute | Since 2013"
    )

    pdf.drawCentredString(
        page_width / 2,
        38,
        "This certificate has been generated through the MCTI One Learning Management System."
    )

    # -------------------------------------------------
    # FINISH PDF
    # -------------------------------------------------

    pdf.showPage()

    pdf.save()

    return response
def verify_certificate(request, verification_token):

    certificate = get_object_or_404(
        Certificate.objects.select_related(
            "student",
            "course"
        ),
        verification_token=verification_token
    )

    context = {
        "certificate": certificate,
    }

    return render(
        request,
        "lms/verify_certificate.html",
        context
    )
