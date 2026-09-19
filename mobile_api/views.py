import random

from django.utils import timezone
from django.contrib.auth import authenticate
from django.db.models import Sum

from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    Student,
    Enrollment,
    FeePayment,
    Attendance,
    BranchLocation,
)

from core.views import calculate_distance_meters

from lms.models import (
    LMSModule,
    LMSTopic,
    LMSTopicContent,
    StudentTopicProgress,
    QuizQuestion,
    QuizAttempt,
)

from lms.views import get_module_fee_access


# =========================================================
# MOBILE LOGIN
# =========================================================

@api_view(["POST"])
def mobile_login(request):

    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:

        return Response(
            {
                "success": False,
                "message": (
                    "Student ID and password are required."
                ),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(
        request,
        username=username,
        password=password,
    )

    if user is None:

        return Response(
            {
                "success": False,
                "message": (
                    "Invalid Student ID or password."
                ),
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    try:

        student = (
            Student.objects
            .select_related(
                "course",
                "admission",
            )
            .get(user=user)
        )

    except Student.DoesNotExist:

        return Response(
            {
                "success": False,
                "message": "Student profile not found.",
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    token, created = Token.objects.get_or_create(
        user=user
    )

    return Response(
        {
            "success": True,
            "message": "Login successful.",

            "token": token.key,

            "student": {
                "id": student.id,
                "student_id": student.student_id,
                "name": student.name,
                "mobile": student.mobile,
                "email": student.email,
                "branch": student.branch,
                "status": student.status,

                "course": {
                    "id": (
                        student.course.id
                        if student.course
                        else None
                    ),
                    "name": (
                        str(student.course)
                        if student.course
                        else None
                    ),
                },
            },
        },
        status=status.HTTP_200_OK,
    )


# =========================================================
# STUDENT DASHBOARD
# =========================================================

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def student_dashboard(request):

    try:

        student = Student.objects.get(
            user=request.user
        )

    except Student.DoesNotExist:

        return Response(
            {
                "success": False,
                "message": "Student profile not found.",
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    enrollments = (
        Enrollment.objects
        .filter(student=student)
        .select_related("course")
        .order_by("-enrollment_date")
    )

    enrollment_data = []

    total_fee = 0
    total_paid = 0

    for enrollment in enrollments:

        paid = (
            FeePayment.objects
            .filter(enrollment=enrollment)
            .aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        balance = (
            enrollment.final_fee - paid
        )

        total_fee += enrollment.final_fee
        total_paid += paid

        enrollment_data.append(
            {
                "id": enrollment.id,

                "enrollment_number": (
                    enrollment.enrollment_number
                ),

                "course_id": (
                    enrollment.course.id
                ),

                "course_name": str(
                    enrollment.course
                ),

                "enrollment_date": (
                    enrollment.enrollment_date
                ),

                "branch": enrollment.branch,
                "status": enrollment.status,

                "standard_fee": (
                    enrollment.standard_fee
                ),

                "discount_amount": (
                    enrollment.discount_amount
                ),

                "final_fee": (
                    enrollment.final_fee
                ),

                "paid": paid,
                "balance": balance,
            }
        )

    total_balance = (
        total_fee - total_paid
    )

    return Response(
        {
            "success": True,

            "student": {
                "id": student.id,
                "student_id": student.student_id,
                "name": student.name,
                "mobile": student.mobile,
                "email": student.email,
                "branch": student.branch,
                "status": student.status,
            },

            "summary": {
                "total_enrollments": (
                    enrollments.count()
                ),
                "total_fee": total_fee,
                "total_paid": total_paid,
                "total_balance": total_balance,
            },

            "enrollments": enrollment_data,
        },
        status=status.HTTP_200_OK,
    )


# =========================================================
# MY COURSES
# =========================================================

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def my_courses(request):

    try:

        student = Student.objects.get(
            user=request.user
        )

    except Student.DoesNotExist:

        return Response(
            {
                "success": False,
                "message": "Student profile not found.",
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    enrollments = (
        Enrollment.objects
        .filter(
            student=student,
            status="active",
        )
        .select_related("course")
        .order_by("-enrollment_date")
    )

    courses_data = []

    added_course_ids = set()

    for enrollment in enrollments:

        parent_course = enrollment.course

        learning_courses = []

        # ---------------------------------------------
        # NORMAL COURSE
        # ---------------------------------------------

        if not getattr(
            parent_course,
            "is_package",
            False,
        ):

            learning_courses.append(
                parent_course
            )

        # ---------------------------------------------
        # PACKAGE COURSE
        # ---------------------------------------------

        else:

            learning_courses.extend(
                parent_course
                .included_courses
                .all()
            )

        for course in learning_courses:

            # Avoid duplicate cards
            if course.id in added_course_ids:
                continue

            added_course_ids.add(
                course.id
            )

            modules = (
                LMSModule.objects
                .filter(
                    course=course,
                    is_active=True,
                )
                .order_by("order")
            )

            total_modules = (
                modules.count()
            )

            total_topics = (
                LMSTopic.objects
                .filter(
                    module__course=course,
                    module__is_active=True,
                    is_active=True,
                )
                .count()
            )

            completed_topics = (
                StudentTopicProgress.objects
                .filter(
                    student=student,
                    topic__module__course=course,
                    is_completed=True,
                )
                .count()
            )

            if total_topics > 0:

                progress_percentage = round(
                    (
                        completed_topics
                        / total_topics
                    )
                    * 100
                )

            else:

                progress_percentage = 0

            courses_data.append(
                {
                    "course_id": course.id,

                    "course_name": str(
                        course
                    ),

                    "enrollment_id": (
                        enrollment.id
                    ),

                    "enrollment_number": (
                        enrollment
                        .enrollment_number
                    ),

                    "is_package_course": (
                        getattr(
                            parent_course,
                            "is_package",
                            False,
                        )
                    ),

                    "parent_package": (
                        str(parent_course)
                        if getattr(
                            parent_course,
                            "is_package",
                            False,
                        )
                        else None
                    ),

                    "total_modules": (
                        total_modules
                    ),

                    "total_topics": (
                        total_topics
                    ),

                    "completed_topics": (
                        completed_topics
                    ),

                    "progress_percentage": (
                        progress_percentage
                    ),
                }
            )

    return Response(
        {
            "success": True,

            "student_id": (
                student.student_id
            ),

            "student_name": (
                student.name
            ),

            "total_courses": len(
                courses_data
            ),

            "courses": courses_data,
        },
        status=status.HTTP_200_OK,
    )


# =========================================================
# COURSE MODULES + TOPICS
# =========================================================

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def course_content(request, course_id):

    try:

        student = Student.objects.get(
            user=request.user
        )

    except Student.DoesNotExist:

        return Response(
            {
                "success": False,
                "message": "Student profile not found.",
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    # =====================================================
    # VERIFY COURSE ACCESS
    # =====================================================

    student_enrollments = (
        Enrollment.objects
        .filter(
            student=student,
            status="active",
        )
        .select_related("course")
    )

    allowed_course_ids = set()

    for enrollment in student_enrollments:

        enrolled_course = (
            enrollment.course
        )

        if getattr(
            enrolled_course,
            "is_package",
            False,
        ):

            allowed_course_ids.update(
                enrolled_course
                .included_courses
                .values_list(
                    "id",
                    flat=True,
                )
            )

        else:

            allowed_course_ids.add(
                enrolled_course.id
            )

    if course_id not in allowed_course_ids:

        return Response(
            {
                "success": False,
                "message": (
                    "You are not enrolled in this course."
                ),
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    # =====================================================
    # GET MODULES
    # =====================================================

    modules = (
        LMSModule.objects
        .filter(
            course_id=course_id,
            is_active=True,
        )
        .order_by(
            "order",
            "id",
        )
    )

    modules_data = []

    for module in modules:

        # =================================================
        # EXISTING WEB LMS FEE RULE
        # =================================================

        fee_access = get_module_fee_access(
            student,
            module,
        )

        module_fee_allowed = (
            fee_access["allowed"]
        )

        topics = list(
            LMSTopic.objects
            .filter(
                module=module,
                is_active=True,
            )
            .order_by(
                "order",
                "id",
            )
        )

        # =================================================
        # FIRST COURSE TOPIC AUTO UNLOCK
        #
        # Only first module + first topic.
        # Other topics/modules follow quiz progression.
        # =================================================

        if (
            module.order == 1
            and topics
            and module_fee_allowed
        ):

            first_topic = topics[0]

            first_progress, created = (
                StudentTopicProgress.objects
                .get_or_create(
                    student=student,
                    topic=first_topic,
                    defaults={
                        "is_unlocked": True,
                    },
                )
            )

            if not first_progress.is_unlocked:

                first_progress.is_unlocked = True

                first_progress.save(
                    update_fields=[
                        "is_unlocked",
                    ]
                )

        # =================================================
        # MODULE PROGRESS
        # =================================================

        module_completed_topics = (
            StudentTopicProgress.objects
            .filter(
                student=student,
                topic__module=module,
                is_completed=True,
            )
            .count()
        )

        module_total_topics = len(
            topics
        )

        if module_total_topics > 0:

            module_progress_percentage = round(
                (
                    module_completed_topics
                    / module_total_topics
                )
                * 100
            )

        else:

            module_progress_percentage = 0

        # =================================================
        # TOPICS
        # =================================================

        topics_data = []

        for topic in topics:

            progress = (
                StudentTopicProgress.objects
                .filter(
                    student=student,
                    topic=topic,
                )
                .first()
            )

            database_unlocked = (
                progress.is_unlocked
                if progress
                else False
            )

            # Even if previously unlocked by quiz,
            # fee gate must still block the module.
            effective_unlocked = (
                database_unlocked
                and module_fee_allowed
            )

            topics_data.append(
                {
                    "topic_id": topic.id,

                    "title": topic.title,

                    "description": (
                        topic.description
                    ),

                    "order": topic.order,

                    "video_url": (
                        topic.video_url
                        or None
                    ),

                    "notes_file": (
                        request.build_absolute_uri(
                            topic.notes_file.url
                        )
                        if topic.notes_file
                        else None
                    ),

                    "practice_file": (
                        request.build_absolute_uri(
                            topic.practice_file.url
                        )
                        if topic.practice_file
                        else None
                    ),

                    "is_unlocked": (
                        effective_unlocked
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

                    "attempts": (
                        progress.attempts
                        if progress
                        else 0
                    ),

                    "locked_by_fee": (
                        not module_fee_allowed
                    ),
                }
            )

        # =================================================
        # MODULE DATA
        # =================================================

        modules_data.append(
            {
                "module_id": module.id,

                "title": module.title,

                "description": (
                    module.description
                ),

                "order": module.order,

                "total_topics": (
                    module_total_topics
                ),

                "completed_topics": (
                    module_completed_topics
                ),

                "progress_percentage": (
                    module_progress_percentage
                ),

                "fee_access": {
                    "allowed": (
                        fee_access["allowed"]
                    ),

                    "required_percent": (
                        fee_access[
                            "required_percent"
                        ]
                    ),

                    "paid_percent": (
                        fee_access[
                            "paid_percent"
                        ]
                    ),

                    "message": (
                        fee_access["message"]
                    ),
                },

                "topics": topics_data,
            }
        )

    # =====================================================
    # RESPONSE
    # =====================================================

    return Response(
        {
            "success": True,

            "course_id": course_id,

            "total_modules": len(
                modules_data
            ),

            "modules": modules_data,
        },
        status=status.HTTP_200_OK,
    )

# =========================================================
# MOBILE TOPIC QUIZ - GET QUESTIONS
# =========================================================

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def topic_quiz(request, topic_id):

    try:
        student = Student.objects.get(
            user=request.user
        )

    except Student.DoesNotExist:
        return Response(
            {
                "success": False,
                "message": "Student profile not found.",
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        topic = (
            LMSTopic.objects
            .select_related(
                "module",
                "module__course",
            )
            .get(
                id=topic_id,
                is_active=True,
            )
        )

    except LMSTopic.DoesNotExist:
        return Response(
            {
                "success": False,
                "message": "Topic not found.",
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    # -----------------------------------------------------
    # VERIFY COURSE ACCESS
    # -----------------------------------------------------

    student_enrollments = (
        Enrollment.objects
        .filter(
            student=student,
            status="active",
        )
        .select_related("course")
    )

    allowed_course_ids = set()

    for enrollment in student_enrollments:

        enrolled_course = enrollment.course

        if getattr(
            enrolled_course,
            "is_package",
            False,
        ):
            allowed_course_ids.update(
                enrolled_course
                .included_courses
                .values_list(
                    "id",
                    flat=True,
                )
            )

        else:
            allowed_course_ids.add(
                enrolled_course.id
            )

    if topic.module.course_id not in allowed_course_ids:

        return Response(
            {
                "success": False,
                "message": (
                    "You do not have access to this course."
                ),
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    # -----------------------------------------------------
    # FEE ACCESS
    # -----------------------------------------------------

    fee_access = get_module_fee_access(
        student,
        topic.module,
    )

    if not fee_access["allowed"]:

        return Response(
            {
                "success": False,
                "message": fee_access["message"],
                "locked_by_fee": True,
                "fee_access": {
                    "required_percent": (
                        fee_access["required_percent"]
                    ),
                    "paid_percent": (
                        fee_access["paid_percent"]
                    ),
                },
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    # -----------------------------------------------------
    # TOPIC UNLOCK CHECK
    # -----------------------------------------------------

    progress = (
        StudentTopicProgress.objects
        .filter(
            student=student,
            topic=topic,
        )
        .first()
    )

    if not progress or not progress.is_unlocked:

        return Response(
            {
                "success": False,
                "message": (
                    "This topic is locked. "
                    "Complete the previous topic first."
                ),
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    # -----------------------------------------------------
    # ENGLISH QUESTIONS - MAX 5
    # -----------------------------------------------------

    questions = list(
        QuizQuestion.objects
        .filter(
            topic=topic,
            language="en",
            is_active=True,
        )
        .order_by(
            "order",
            "id",
        )[:5]
    )

    questions_data = []

    for question in questions:

        options = [
            {
                "key": "A",
                "text": question.option_a,
            },
            {
                "key": "B",
                "text": question.option_b,
            },
            {
                "key": "C",
                "text": question.option_c,
            },
            {
                "key": "D",
                "text": question.option_d,
            },
        ]

        random.shuffle(options)

        questions_data.append(
            {
                "question_id": question.id,
                "question": question.question,
                "order": question.order,
                "options": options,
            }
        )

    return Response(
        {
            "success": True,

            "topic": {
                "topic_id": topic.id,
                "title": topic.title,
                "module_id": topic.module.id,
                "module_title": topic.module.title,
                "course_id": topic.module.course.id,
                "course_name": str(
                    topic.module.course
                ),
            },

            "language": "en",
            "language_name": "English",

            "total_questions": len(
                questions_data
            ),

            "pass_score": 3,

            "questions": questions_data,
        },
        status=status.HTTP_200_OK,
    )


# =========================================================
# MOBILE TOPIC QUIZ - SUBMIT
# =========================================================

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def submit_topic_quiz(request, topic_id):

    try:
        student = Student.objects.get(
            user=request.user
        )

    except Student.DoesNotExist:
        return Response(
            {
                "success": False,
                "message": "Student profile not found.",
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        topic = (
            LMSTopic.objects
            .select_related(
                "module",
                "module__course",
            )
            .get(
                id=topic_id,
                is_active=True,
            )
        )

    except LMSTopic.DoesNotExist:
        return Response(
            {
                "success": False,
                "message": "Topic not found.",
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    # -----------------------------------------------------
    # VERIFY COURSE ACCESS
    # -----------------------------------------------------

    student_enrollments = (
        Enrollment.objects
        .filter(
            student=student,
            status="active",
        )
        .select_related("course")
    )

    allowed_course_ids = set()

    for enrollment in student_enrollments:

        enrolled_course = enrollment.course

        if getattr(
            enrolled_course,
            "is_package",
            False,
        ):
            allowed_course_ids.update(
                enrolled_course
                .included_courses
                .values_list(
                    "id",
                    flat=True,
                )
            )

        else:
            allowed_course_ids.add(
                enrolled_course.id
            )

    if topic.module.course_id not in allowed_course_ids:

        return Response(
            {
                "success": False,
                "message": (
                    "You do not have access to this course."
                ),
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    # -----------------------------------------------------
    # FEE ACCESS
    # -----------------------------------------------------

    fee_access = get_module_fee_access(
        student,
        topic.module,
    )

    if not fee_access["allowed"]:

        return Response(
            {
                "success": False,
                "message": fee_access["message"],
                "locked_by_fee": True,
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    # -----------------------------------------------------
    # TOPIC UNLOCK CHECK
    # -----------------------------------------------------

    progress = (
        StudentTopicProgress.objects
        .filter(
            student=student,
            topic=topic,
        )
        .first()
    )

    if not progress or not progress.is_unlocked:

        return Response(
            {
                "success": False,
                "message": (
                    "This topic is locked. "
                    "Complete the previous topic first."
                ),
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    # -----------------------------------------------------
    # GET QUIZ QUESTIONS
    # -----------------------------------------------------

    questions = list(
        QuizQuestion.objects
        .filter(
            topic=topic,
            language="en",
            is_active=True,
        )
        .order_by(
            "order",
            "id",
        )[:5]
    )

    total_questions = len(questions)

    if total_questions == 0:

        return Response(
            {
                "success": False,
                "message": (
                    "No quiz questions found "
                    "for this topic."
                ),
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    # -----------------------------------------------------
    # ANSWERS FORMAT:
    #
    # {
    #   "answers": {
    #       "1": "A",
    #       "2": "C"
    #   }
    # }
    # -----------------------------------------------------

    answers = request.data.get(
        "answers",
        {}
    )

    if not isinstance(answers, dict):

        return Response(
            {
                "success": False,
                "message": (
                    "Answers must be sent "
                    "as an object."
                ),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    score = 0

    answer_results = []

    for question in questions:

        selected_answer = answers.get(
            str(question.id)
        )

        if selected_answer:
            selected_answer = (
                str(selected_answer)
                .strip()
                .upper()
            )

        is_correct = (
            selected_answer
            == question.correct_answer
        )

        if is_correct:
            score += 1

        answer_results.append(
            {
                "question_id": question.id,
                "selected_answer": (
                    selected_answer
                ),
                "is_correct": is_correct,
            }
        )

    # -----------------------------------------------------
    # PASS RULE - SAME AS WEB LMS
    # -----------------------------------------------------

    passed = score >= 3

    # -----------------------------------------------------
    # SAVE QUIZ ATTEMPT
    # -----------------------------------------------------

    QuizAttempt.objects.create(
        student=student,
        topic=topic,
        score=score,
        total_questions=total_questions,
        passed=passed,
    )

    # -----------------------------------------------------
    # UPDATE TOPIC PROGRESS
    # -----------------------------------------------------

    progress, created = (
        StudentTopicProgress.objects
        .get_or_create(
            student=student,
            topic=topic,
            defaults={
                "is_unlocked": True,
                "is_completed": False,
                "best_score": 0,
                "total_questions": (
                    total_questions
                ),
                "attempts": 0,
            },
        )
    )

    progress.is_unlocked = True

    progress.attempts += 1

    progress.total_questions = (
        total_questions
    )

    progress.last_attempt_at = (
        timezone.now()
    )

    if score > progress.best_score:
        progress.best_score = score

    if passed:

        progress.is_completed = True

        if not progress.completed_at:
            progress.completed_at = (
                timezone.now()
            )

    progress.save()

    # -----------------------------------------------------
    # NEXT UNLOCK INFORMATION
    # -----------------------------------------------------

    next_unlocked = None

    next_locked_by_fee = False

    next_fee_message = ""

    # -----------------------------------------------------
    # UNLOCK NEXT TOPIC
    # -----------------------------------------------------

    if passed:

        next_topic = (
            LMSTopic.objects
            .filter(
                module=topic.module,
                is_active=True,
                order__gt=topic.order,
            )
            .order_by(
                "order",
                "id",
            )
            .first()
        )

        if next_topic:

            next_progress, created = (
                StudentTopicProgress.objects
                .get_or_create(
                    student=student,
                    topic=next_topic,
                    defaults={
                        "is_unlocked": True,
                    },
                )
            )

            if not next_progress.is_unlocked:

                next_progress.is_unlocked = True

                next_progress.save(
                    update_fields=[
                        "is_unlocked",
                    ]
                )

            next_unlocked = {
                "type": "topic",
                "topic_id": next_topic.id,
                "title": next_topic.title,
                "module_id": (
                    next_topic.module_id
                ),
            }

        else:

            # ---------------------------------------------
            # LAST TOPIC OF MODULE
            # TRY NEXT MODULE
            # ---------------------------------------------

            next_module = (
                LMSModule.objects
                .filter(
                    course=topic.module.course,
                    is_active=True,
                    order__gt=topic.module.order,
                )
                .order_by(
                    "order",
                    "id",
                )
                .first()
            )

            if next_module:

                next_module_fee_access = (
                    get_module_fee_access(
                        student,
                        next_module,
                    )
                )

                first_topic_next_module = (
                    LMSTopic.objects
                    .filter(
                        module=next_module,
                        is_active=True,
                    )
                    .order_by(
                        "order",
                        "id",
                    )
                    .first()
                )

                if (
                    first_topic_next_module
                    and
                    next_module_fee_access[
                        "allowed"
                    ]
                ):

                    next_progress, created = (
                        StudentTopicProgress.objects
                        .get_or_create(
                            student=student,
                            topic=(
                                first_topic_next_module
                            ),
                            defaults={
                                "is_unlocked": True,
                            },
                        )
                    )

                    if not next_progress.is_unlocked:

                        next_progress.is_unlocked = True

                        next_progress.save(
                            update_fields=[
                                "is_unlocked",
                            ]
                        )

                    next_unlocked = {
                        "type": "module",
                        "module_id": (
                            next_module.id
                        ),
                        "module_title": (
                            next_module.title
                        ),
                        "topic_id": (
                            first_topic_next_module.id
                        ),
                        "topic_title": (
                            first_topic_next_module.title
                        ),
                    }

                elif not next_module_fee_access[
                    "allowed"
                ]:

                    next_locked_by_fee = True

                    next_fee_message = (
                        next_module_fee_access[
                            "message"
                        ]
                    )

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return Response(
        {
            "success": True,

            "topic_id": topic.id,

            "topic_title": topic.title,

            "score": score,

            "total_questions": (
                total_questions
            ),

            "passed": passed,

            "pass_score": 3,

            "attempts": progress.attempts,

            "best_score": (
                progress.best_score
            ),

            "is_completed": (
                progress.is_completed
            ),

            "message": (
                "Quiz passed successfully."
                if passed
                else (
                    "Quiz not passed. "
                    "Minimum 3 out of 5 "
                    "is required."
                )
            ),

            "next_unlocked": (
                next_unlocked
            ),

            "next_locked_by_fee": (
                next_locked_by_fee
            ),

            "next_fee_message": (
                next_fee_message
            ),

            "answers": answer_results,
        },
        status=status.HTTP_200_OK,
    )
# =========================================================
# MOBILE TOPIC DETAIL
# =========================================================

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def topic_detail(request, topic_id):

    try:
        student = Student.objects.get(
            user=request.user
        )

    except Student.DoesNotExist:
        return Response(
            {
                "success": False,
                "message": "Student profile not found.",
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        topic = (
            LMSTopic.objects
            .select_related(
                "module",
                "module__course",
            )
            .get(
                id=topic_id,
                is_active=True,
            )
        )

    except LMSTopic.DoesNotExist:
        return Response(
            {
                "success": False,
                "message": "Topic not found.",
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    # -----------------------------------------------------
    # VERIFY COURSE ACCESS
    # -----------------------------------------------------

    student_enrollments = (
        Enrollment.objects
        .filter(
            student=student,
            status="active",
        )
        .select_related("course")
    )

    allowed_course_ids = set()

    for enrollment in student_enrollments:

        enrolled_course = enrollment.course

        if getattr(
            enrolled_course,
            "is_package",
            False,
        ):

            allowed_course_ids.update(
                enrolled_course
                .included_courses
                .values_list(
                    "id",
                    flat=True,
                )
            )

        else:
            allowed_course_ids.add(
                enrolled_course.id
            )

    if topic.module.course_id not in allowed_course_ids:

        return Response(
            {
                "success": False,
                "message": (
                    "You do not have access to this course."
                ),
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    # -----------------------------------------------------
    # FEE ACCESS
    # -----------------------------------------------------

    fee_access = get_module_fee_access(
        student,
        topic.module,
    )

    if not fee_access["allowed"]:

        return Response(
            {
                "success": False,

                "message": (
                    fee_access["message"]
                ),

                "locked_by_fee": True,

                "fee_access": {
                    "allowed": False,

                    "required_percent": (
                        fee_access[
                            "required_percent"
                        ]
                    ),

                    "paid_percent": (
                        fee_access[
                            "paid_percent"
                        ]
                    ),
                },
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    # -----------------------------------------------------
    # TOPIC PROGRESS / UNLOCK
    # -----------------------------------------------------

    progress = (
        StudentTopicProgress.objects
        .filter(
            student=student,
            topic=topic,
        )
        .first()
    )

    if not progress or not progress.is_unlocked:

        return Response(
            {
                "success": False,

                "message": (
                    "This topic is locked. "
                    "Complete the previous topic first."
                ),

                "locked": True,
                "locked_by_fee": False,
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    # -----------------------------------------------------
    # LANGUAGE
    # ?lang=en
    # ?lang=hi
    # ?lang=mr
    # -----------------------------------------------------

    requested_language = (
        request.GET.get(
            "lang",
            "en",
        )
        .strip()
        .lower()
    )

    allowed_languages = {
        "en": "English",
        "hi": "Hindi",
        "mr": "Marathi",
    }

    if requested_language not in allowed_languages:

        requested_language = "en"

    # -----------------------------------------------------
    # MULTILINGUAL CONTENT
    # -----------------------------------------------------

    localized_content = (
        LMSTopicContent.objects
        .filter(
            topic=topic,
            language=requested_language,
            is_active=True,
        )
        .first()
    )

    content_language = requested_language

    # If requested language is unavailable,
    # try English multilingual content.

    if not localized_content:

        localized_content = (
            LMSTopicContent.objects
            .filter(
                topic=topic,
                language="en",
                is_active=True,
            )
            .first()
        )

        if localized_content:
            content_language = "en"

    # -----------------------------------------------------
    # DESCRIPTION
    # -----------------------------------------------------

    if (
        localized_content
        and localized_content.description
    ):
        description = (
            localized_content.description
        )

    else:
        description = (
            topic.description or ""
        )

    # -----------------------------------------------------
    # VIDEO
    # -----------------------------------------------------

    if (
        localized_content
        and localized_content.video_url
    ):
        video_url = (
            localized_content.video_url
        )

    else:
        video_url = (
            topic.video_url or None
        )

    # -----------------------------------------------------
    # NOTES FILE
    # -----------------------------------------------------

    if (
        localized_content
        and localized_content.notes_file
    ):
        notes_file = (
            request.build_absolute_uri(
                localized_content
                .notes_file
                .url
            )
        )

    elif topic.notes_file:

        notes_file = (
            request.build_absolute_uri(
                topic.notes_file.url
            )
        )

    else:
        notes_file = None

    # -----------------------------------------------------
    # PRACTICE FILE
    # -----------------------------------------------------

    if (
        localized_content
        and localized_content.practice_file
    ):
        practice_file = (
            request.build_absolute_uri(
                localized_content
                .practice_file
                .url
            )
        )

    elif topic.practice_file:

        practice_file = (
            request.build_absolute_uri(
                topic.practice_file.url
            )
        )

    else:
        practice_file = None

    # -----------------------------------------------------
    # AVAILABLE LANGUAGES
    # -----------------------------------------------------

    available_language_codes = set(
        LMSTopicContent.objects
        .filter(
            topic=topic,
            is_active=True,
        )
        .values_list(
            "language",
            flat=True,
        )
    )

    # Base topic itself works as English fallback.

    available_language_codes.add(
        "en"
    )

    available_languages = []

    for language_code in [
        "en",
        "hi",
        "mr",
    ]:

        if language_code in available_language_codes:

            available_languages.append(
                {
                    "code": language_code,

                    "name": (
                        allowed_languages[
                            language_code
                        ]
                    ),
                }
            )

    # -----------------------------------------------------
    # QUIZ
    # -----------------------------------------------------

    quiz_questions_count = (
        QuizQuestion.objects
        .filter(
            topic=topic,
            language="en",
            is_active=True,
        )
        .count()
    )

    quiz_available = (
        quiz_questions_count > 0
    )

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return Response(
        {
            "success": True,

            "course": {
                "course_id": (
                    topic.module.course.id
                ),

                "course_name": str(
                    topic.module.course
                ),
            },

            "module": {
                "module_id": (
                    topic.module.id
                ),

                "title": (
                    topic.module.title
                ),

                "order": (
                    topic.module.order
                ),
            },

            "topic": {
                "topic_id": (
                    topic.id
                ),

                "title": (
                    topic.title
                ),

                "order": (
                    topic.order
                ),

                "description": (
                    description
                ),

                "video_url": (
                    video_url
                ),

                "notes_file": (
                    notes_file
                ),

                "practice_file": (
                    practice_file
                ),
            },

            "language": {
                "requested": (
                    requested_language
                ),

                "served": (
                    content_language
                ),

                "served_name": (
                    allowed_languages[
                        content_language
                    ]
                ),

                "available": (
                    available_languages
                ),
            },

            "progress": {
                "is_unlocked": True,

                "is_completed": (
                    progress.is_completed
                ),

                "best_score": (
                    progress.best_score
                ),

                "total_questions": (
                    progress.total_questions
                ),

                "attempts": (
                    progress.attempts
                ),

                "completed_at": (
                    progress.completed_at
                ),
            },

            "quiz": {
                "available": (
                    quiz_available
                ),

                "questions_count": (
                    quiz_questions_count
                ),

                "pass_score": 3,

                "quiz_url": (
                    request.build_absolute_uri(
                        (
                            f"/api/mobile/topics/"
                            f"{topic.id}/quiz/"
                        )
                    )
                    if quiz_available
                    else None
                ),
            },

            "fee_access": {
                "allowed": (
                    fee_access["allowed"]
                ),

                "required_percent": (
                    fee_access[
                        "required_percent"
                    ]
                ),

                "paid_percent": (
                    fee_access[
                        "paid_percent"
                    ]
                ),
            },
        },
        status=status.HTTP_200_OK,
    )

# =========================================================
# MOBILE GPS ATTENDANCE
# =========================================================

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def mark_mobile_attendance(request):

    try:
        student = Student.objects.get(
            user=request.user
        )
    except Student.DoesNotExist:
        return Response(
            {
                "success": False,
                "message": "Student profile not found.",
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    latitude = request.data.get("latitude")
    longitude = request.data.get("longitude")

    if latitude in [None, ""] or longitude in [None, ""]:
        return Response(
            {
                "success": False,
                "message": "Location not received.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except (TypeError, ValueError):
        return Response(
            {
                "success": False,
                "message": "Invalid GPS coordinates.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not (-90 <= latitude <= 90):
        return Response(
            {
                "success": False,
                "message": "Invalid latitude.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not (-180 <= longitude <= 180):
        return Response(
            {
                "success": False,
                "message": "Invalid longitude.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    today = timezone.localdate()

    existing_attendance = (
        Attendance.objects
        .filter(
            student=student,
            attendance_date=today,
        )
        .first()
    )

    if existing_attendance:
        return Response(
            {
                "success": True,
                "already_marked": True,
                "attendance": {
                    "attendance_date": existing_attendance.attendance_date,
                    "status": existing_attendance.status,
                    "branch": existing_attendance.branch,
                    "source": existing_attendance.source,
                    "first_login_time": existing_attendance.first_login_time,
                },
                "message": "Attendance already marked for today.",
            },
            status=status.HTTP_200_OK,
        )

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
            branch.longitude,
        )

        if distance <= branch.radius_meters:
            if (
                matched_distance is None
                or distance < matched_distance
            ):
                matched_branch = branch
                matched_distance = distance

    if not matched_branch:
        return Response(
            {
                "success": False,
                "already_marked": False,
                "inside_branch_radius": False,
                "message": "You are outside the allowed branch radius.",
            },
            status=status.HTTP_403_FORBIDDEN,
        )

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
        },
    )

    if not created:
        return Response(
            {
                "success": True,
                "already_marked": True,
                "attendance": {
                    "attendance_date": attendance.attendance_date,
                    "status": attendance.status,
                    "branch": attendance.branch,
                    "source": attendance.source,
                    "first_login_time": attendance.first_login_time,
                },
                "message": "Attendance already marked for today.",
            },
            status=status.HTTP_200_OK,
        )

    return Response(
        {
            "success": True,
            "already_marked": False,
            "inside_branch_radius": True,
            "attendance": {
                "attendance_date": attendance.attendance_date,
                "status": attendance.status,
                "branch": attendance.branch,
                "distance_meters": round(matched_distance, 2),
                "allowed_radius_meters": matched_branch.radius_meters,
                "source": attendance.source,
                "first_login_time": attendance.first_login_time,
            },
            "message": "Attendance marked successfully.",
        },
        status=status.HTTP_201_CREATED,
    )
