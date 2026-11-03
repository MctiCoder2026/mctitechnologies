from collections import defaultdict
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Max, Q
from django.shortcuts import render
from django.utils import timezone

from core.models import Enrollment, Course
from core.views import get_user_branch, is_admin_user
from .models import (
    LMSModule, LMSTopic, StudentTopicProgress,
    QuizAttempt, TrainerTeachingReport,
)


@login_required
def student_progress_dashboard(request):
    user = request.user
    admin = is_admin_user(user)

    if not admin:
        if not user.is_staff or not user.is_active:
            raise PermissionDenied
        branch = (get_user_branch(user) or "").strip()
        if not branch or branch.lower() == "head_office":
            raise PermissionDenied
    else:
        branch = ""

    today = timezone.localdate()
    search = request.GET.get("q", "").strip()[:100]
    selected_branch = request.GET.get("branch", "").strip()[:100]
    selected_course = request.GET.get("course", "").strip()

    qs = Enrollment.objects.filter(
        status="active",
        student__status="active",
        enrollment_date__lte=today,
    ).select_related("student", "course")

    if not admin:
        qs = qs.filter(
            Q(branch__iexact=branch) |
            (Q(branch__isnull=True) & Q(student__branch__iexact=branch)) |
            (Q(branch="") & Q(student__branch__iexact=branch))
        )
        selected_branch = branch
    elif selected_branch:
        qs = qs.filter(
            Q(branch__iexact=selected_branch) |
            (Q(branch__isnull=True) & Q(student__branch__iexact=selected_branch)) |
            (Q(branch="") & Q(student__branch__iexact=selected_branch))
        )

    if search:
        qs = qs.filter(
            Q(student__name__icontains=search) |
            Q(student__mobile__icontains=search) |
            Q(enrollment_number__icontains=search)
        )

    if selected_course.isdigit():
        qs = qs.filter(course_id=int(selected_course))

    enrollments = list(qs.order_by("student__name", "id")[:500])
    student_ids = {e.student_id for e in enrollments}
    course_ids = {e.course_id for e in enrollments}

    modules = list(
        LMSModule.objects.filter(
            course_id__in=course_ids, is_active=True
        ).values("id", "course_id", "title", "order")
    )
    module_ids = [m["id"] for m in modules]

    topics = list(
        LMSTopic.objects.filter(
            module_id__in=module_ids, is_active=True
        ).values("id", "module_id")
    )

    modules_by_course = defaultdict(list)
    for module in modules:
        modules_by_course[module["course_id"]].append(module)

    topic_ids_by_module = defaultdict(set)
    for topic in topics:
        topic_ids_by_module[topic["module_id"]].add(topic["id"])

    completed_by_student = defaultdict(set)
    progress_qs = StudentTopicProgress.objects.filter(
        student_id__in=student_ids,
        topic_id__in=[t["id"] for t in topics],
        is_completed=True,
    ).values_list("student_id", "topic_id")

    for student_id, topic_id in progress_qs:
        completed_by_student[student_id].add(topic_id)

    activity_by_student_course = {}
    activities = (
        QuizAttempt.objects.filter(
            student_id__in=student_ids,
            topic__module__course_id__in=course_ids,
        )
        .values("student_id", "topic__module__course_id")
        .annotate(last_activity=Max("attempted_at"))
    )
    for item in activities:
        activity_by_student_course[
            (item["student_id"], item["topic__module__course_id"])
        ] = item["last_activity"]

    teaching_by_enrollment = defaultdict(
        lambda: {"submitted": 0, "approved": 0, "verified": 0}
    )
    teaching = TrainerTeachingReport.objects.filter(
        assignment__enrollment_id__in=[e.id for e in enrollments]
    ).values("assignment__enrollment_id").annotate(
        submitted=Count("id"),
        approved=Count("id", filter=Q(review_status="approved")),
        verified=Count("id", filter=Q(trainer_approved_at__isnull=False)),
    )
    for item in teaching:
        teaching_by_enrollment[item["assignment__enrollment_id"]] = item

    rows = []
    unique_students = set()
    total_completed_topics = 0
    total_topics = 0
    completed_modules_total = 0
    pending_attention = 0
    completion_ready = 0

    for enrollment in enrollments:
        unique_students.add(enrollment.student_id)
        course_modules = modules_by_course[enrollment.course_id]
        completed_set = completed_by_student[enrollment.student_id]

        course_total_topics = 0
        course_completed_topics = 0
        completed_modules = 0
        module_details = []

        for module in course_modules:
            module_topic_ids = topic_ids_by_module[module["id"]]
            count = len(module_topic_ids)
            done = len(module_topic_ids & completed_set)

            course_total_topics += count
            course_completed_topics += done

            if count > 0 and done == count:
                completed_modules += 1

            module_details.append({
                "title": module["title"],
                "completed": done,
                "total": count,
                "done": count > 0 and done == count,
            })

        percentage = round(
            100 * course_completed_topics / course_total_topics
        ) if course_total_topics else 0

        last_activity = activity_by_student_course.get(
            (enrollment.student_id, enrollment.course_id)
        )

        inactivity_days = (
            (today - timezone.localtime(last_activity).date()).days
            if last_activity else
            (today - enrollment.enrollment_date).days
        )

        needs_attention = (
            course_total_topics > course_completed_topics
            and inactivity_days >= 7
        )

        if needs_attention:
            pending_attention += 1

        if course_total_topics and course_completed_topics == course_total_topics:
            completion_ready += 1

        total_completed_topics += course_completed_topics
        total_topics += course_total_topics
        completed_modules_total += completed_modules

        rows.append({
            "enrollment": enrollment,
            "module_count": len(course_modules),
            "completed_modules": completed_modules,
            "completed_topics": course_completed_topics,
            "total_topics": course_total_topics,
            "percentage": percentage,
            "last_activity": last_activity,
            "inactive_days": inactivity_days,
            "needs_attention": needs_attention,
            "completion_ready": (
                course_total_topics > 0
                and course_completed_topics == course_total_topics
            ),
            "teaching": teaching_by_enrollment[enrollment.id],
            "module_details": module_details,
        })

    branches = []
    if admin:
        branches = list(
            Enrollment.objects.filter(status="active")
            .exclude(branch__isnull=True).exclude(branch="")
            .values_list("branch", flat=True).distinct().order_by("branch")
        )

    courses = Course.objects.filter(
        id__in=course_ids
    ).order_by("title")

    return render(request, "lms/management_student_progress.html", {
        "rows": rows,
        "admin": admin,
        "branches": branches,
        "courses": courses,
        "selected_branch": selected_branch,
        "selected_course": selected_course,
        "search": search,
        "unique_student_count": len(unique_students),
        "enrollment_count": len(rows),
        "completed_modules_total": completed_modules_total,
        "progress_percentage": round(
            100 * total_completed_topics / total_topics
        ) if total_topics else 0,
        "pending_attention": pending_attention,
        "completion_ready": completion_ready,
        "limited": qs.count() > 500,
    })
