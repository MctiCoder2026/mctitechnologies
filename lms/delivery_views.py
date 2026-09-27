from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.models import Course, Enrollment, StaffProfile, Student
from .models import (
    LMSTopicDoubt,
    TrainingChecklistItem,
    TrainingDeliveryEnrollment,
    TrainingDeliveryPlan,
    TrainingDeliverySession,
    WeeklyTeachingAssignment,
    TrainerTeachingReport,
)


def _staff(request):
    return StaffProfile.objects.filter(user=request.user, is_active=True).first()


def _can_manage(request, staff):
    return request.user.is_superuser or bool(
        staff and staff.department == "management"
        and staff.branch == "head_office"
    )


def _allowed_enrollments(staff, request):
    qs = Enrollment.objects.filter(
        status="active", student__status="active"
    ).select_related("student", "course")
    if not _can_manage(request, staff):
        qs = qs.filter(
            Q(branch__iexact=staff.branch)
            | Q(branch__isnull=True, student__branch__iexact=staff.branch)
            | Q(branch="", student__branch__iexact=staff.branch)
        )
    return qs


def _course_for(enrollment, course_id):
    if enrollment.course_id == course_id and not enrollment.course.is_package:
        return enrollment.course
    if enrollment.course.is_package:
        return enrollment.course.included_courses.filter(
            pk=course_id, is_active=True
        ).first()
    return None


@login_required
def trainer_delivery(request):
    return redirect("lms:staff_classroom")
    staff = _staff(request)
    if not staff or staff.department not in (
        "training", "management", "operations"
    ) and not request.user.is_superuser:
        return HttpResponseForbidden("Trainer access required.")
    enrollments = _allowed_enrollments(staff, request).order_by(
        "student__name", "id"
    )
    courses = Course.objects.filter(
        training_checklist_items__is_published=True
    ).distinct().order_by("title")
    selected_course_id = request.GET.get("course")
    selected_course = courses.filter(pk=selected_course_id).first() if (
        selected_course_id and selected_course_id.isdigit()
    ) else None
    selected_enrollments = []
    items = []
    if selected_course:
        selected_enrollments = [
            enrollment for enrollment in enrollments
            if _course_for(enrollment, selected_course.id)
        ]
        items = list(TrainingChecklistItem.objects.filter(
            course=selected_course, is_published=True
        ).order_by("module_order", "order", "id"))
    doubts = LMSTopicDoubt.objects.filter(
        status="open",
        enrollment_id__in=[e.id for e in selected_enrollments],
    ).select_related(
        "enrollment__student", "topic"
    ).order_by("opened_at") if selected_course else []
    pending_practice = []
    if selected_course:
        doubts = doubts.filter(topic__course=selected_course)
        latest = {}
        verified = set()
        for record in TrainingDeliveryEnrollment.objects.filter(
            enrollment_id__in=[e.id for e in selected_enrollments],
            session__topic__course=selected_course,
        ).select_related(
            "enrollment__student", "session__topic"
        ).order_by("-session__session_date", "-session_id"):
            key = (record.enrollment_id, record.session.topic_id)
            latest.setdefault(key, record)
            if record.practice_verified_at:
                verified.add(key)
        pending_practice = [
            record for key, record in latest.items() if key not in verified
        ]
    return render(request, "lms/delivery_trainer.html", {
        "courses": courses,
        "course": selected_course,
        "enrollments": selected_enrollments,
        "items": items,
        "doubts": doubts,
        "pending_practice": pending_practice,
        "today": timezone.localdate(),
    })


@login_required
@require_POST
def record_delivery(request):
    return HttpResponseForbidden(
        "Use weekly trainer assignment and staff approval."
    )
    staff = _staff(request)
    if not staff or (
        staff.department not in ("training", "management", "operations")
        and not request.user.is_superuser
    ):
        return HttpResponseForbidden("Trainer access required.")
    item = get_object_or_404(
        TrainingChecklistItem,
        pk=request.POST.get("item_id"),
        is_published=True,
    )
    enrollments = list(_allowed_enrollments(staff, request).filter(
        pk__in=request.POST.getlist("enrollment_ids")
    ))
    submitted = set(request.POST.getlist("enrollment_ids"))
    if not submitted or len(enrollments) != len(submitted):
        return HttpResponseForbidden("Invalid student selection.")
    if any(not _course_for(e, item.course_id) for e in enrollments):
        return HttpResponseForbidden("Course does not match enrollment.")
    branches = {
        (e.branch or e.student.branch or "").strip().lower()
        for e in enrollments
    }
    if len(branches) != 1:
        return HttpResponseForbidden("Select students from one branch.")
    try:
        session_date = timezone.datetime.strptime(
            request.POST["session_date"], "%Y-%m-%d"
        ).date()
    except (KeyError, ValueError):
        return HttpResponseForbidden("Invalid class date.")
    if session_date > timezone.localdate():
        return HttpResponseForbidden("A future class cannot be marked taught.")
    if any(session_date < enrollment.enrollment_date for enrollment in enrollments):
        return HttpResponseForbidden("Class date cannot precede student enrollment.")
    session_type = request.POST.get("session_type", "regular")
    if session_type not in ("regular", "revision", "doubt_reteach"):
        return HttpResponseForbidden("Invalid class type.")
    practice_ids = set(request.POST.getlist("practice_verified_ids"))
    if not practice_ids.issubset(submitted):
        return HttpResponseForbidden("Invalid practice selection.")
    evidence = request.POST.get("practice_evidence", "").strip()[:1000]
    if practice_ids and len(evidence) < 5:
        return HttpResponseForbidden("Describe the completed lab task.")
    with transaction.atomic():
        assigned = TrainingDeliveryPlan.objects.filter(
            enrollment__in=enrollments, course=item.course
        ).values_list("assigned_trainer_id", flat=True).distinct()
        assigned_ids = list(assigned)
        assigned_id = assigned_ids[0] if len(assigned_ids) == 1 else None
        session = TrainingDeliverySession.objects.create(
            topic=item,
            branch=branches.pop(),
            taught_by=staff,
            assigned_trainer_id=assigned_id,
            session_type=session_type,
            session_date=session_date,
            notes=request.POST.get("notes", "").strip()[:2000],
            standard_snapshot={
                "version": item.version,
                "module": item.module_title,
                "title": item.title,
                "learning_outcome": item.learning_outcome,
                "trainer_steps": item.trainer_steps,
                "student_practice": item.student_practice,
                "completion_check": item.completion_check,
            },
        )
        verified_time = timezone.now()
        TrainingDeliveryEnrollment.objects.bulk_create([
            TrainingDeliveryEnrollment(
                session=session,
                enrollment=e,
                practice_verified_at=verified_time if str(e.id) in practice_ids else None,
                practice_verified_by=staff if str(e.id) in practice_ids else None,
                practice_evidence=evidence if str(e.id) in practice_ids else "",
            )
            for e in enrollments
        ])
        if session_type == "doubt_reteach":
            LMSTopicDoubt.objects.filter(
                enrollment__in=enrollments, topic=item, status="open"
            ).update(
                status="cleared",
                resolved_at=timezone.now(),
                resolved_by=staff,
                resolution_session=session,
                trainer_note=request.POST.get("notes", "").strip()[:2000],
            )
    return redirect(
        f"{reverse('lms:trainer_delivery')}?course={item.course_id}"
    )


@login_required
def student_delivery(request):
    student = get_object_or_404(Student, user=request.user)
    rows = []
    for enrollment in Enrollment.objects.filter(
        student=student, status="active"
    ).select_related("course").prefetch_related("course__included_courses"):
        if enrollment.course.is_package:
            courses = list(enrollment.course.included_courses.filter(
                is_active=True
            ))
        else:
            courses = [enrollment.course]
        for course in courses:
            items = list(TrainingChecklistItem.objects.filter(
                course=course, is_published=True
            ).order_by("module_order", "order", "id"))
            if not items:
                continue
            delivered = {}
            history = {}
            for record in TrainingDeliveryEnrollment.objects.filter(
                enrollment=enrollment, session__topic__course=course
            ).select_related(
                "session__taught_by__user", "session__topic",
                "practice_verified_by__user",
            ):
                key = record.session.topic_id
                history.setdefault(key, []).append(record)
                if key not in delivered or (
                    record.session.session_date, record.session_id
                ) > (
                    delivered[key].session.session_date,
                    delivered[key].session_id,
                ):
                    delivered[key] = record
            for records in history.values():
                records.sort(key=lambda r: (
                    r.session.session_date, r.session_id
                ))
            doubts = list(LMSTopicDoubt.objects.filter(
                enrollment=enrollment, topic__course=course,
                status="open"
            ))
            doubt_ids = {d.topic_id for d in doubts}
            for item in items:
                item.class_record = delivered.get(item.id)
                item.class_history = history.get(item.id, [])
                item.has_open_doubt = item.id in doubt_ids
            rows.append({
                "enrollment": enrollment,
                "course": course,
                "items": items,
                "taught": len(delivered),
                "total": len(items),
                "open_doubts": len(doubts),
                "plan": TrainingDeliveryPlan.objects.filter(
                    enrollment=enrollment, course=course
                ).first(),
            })
    return render(request, "lms/delivery_student.html", {
        "rows": rows
    })


@login_required
@require_POST
def raise_delivery_doubt(request):
    return HttpResponseForbidden(
        "Use approved class feedback from Classroom Progress."
    )
    student = get_object_or_404(Student, user=request.user)
    enrollment = get_object_or_404(
        Enrollment, pk=request.POST.get("enrollment_id"),
        student=student, status="active"
    )
    item = get_object_or_404(
        TrainingChecklistItem, pk=request.POST.get("item_id"),
        is_published=True
    )
    if not _course_for(enrollment, item.course_id):
        return HttpResponseForbidden("Course does not match enrollment.")
    taught = TrainingDeliveryEnrollment.objects.filter(
        enrollment=enrollment, session__topic=item
    ).exists()
    if not taught:
        return HttpResponseForbidden("Doubt can be raised after a class.")
    question = request.POST.get("question", "").strip()[:1000]
    if not question:
        return HttpResponseForbidden("Enter your doubt.")
    if not LMSTopicDoubt.objects.filter(
        enrollment=enrollment, topic=item, status="open"
    ).exists():
        LMSTopicDoubt.objects.create(
            enrollment=enrollment, topic=item, question=question
        )
    return redirect("lms:student_delivery")


@login_required
def delivery_report(request):
    staff = _staff(request)
    if not _can_manage(request, staff):
        return HttpResponseForbidden("Management access required.")
    all_items = {}
    full_course_counts = {}
    for item in TrainingChecklistItem.objects.values(
        "course_id", "id", "is_published"
    ):
        course_id = item["course_id"]
        full_course_counts[course_id] = full_course_counts.get(course_id, 0) + 1
        if item["is_published"]:
            all_items.setdefault(course_id, set()).add(item["id"])
    delivered = {}
    latest_teacher = {}
    substitutes = {}
    for record in TrainingDeliveryEnrollment.objects.filter(
        enrollment__status="active",
        session__topic__is_published=True,
    ).values(
        "enrollment_id", "session__topic__course_id", "session__topic_id",
        "session_id", "session__session_date",
        "session__taught_by__user__first_name",
        "session__taught_by__user__last_name",
        "session__taught_by__user__username",
        "session__taught_by_id", "session__assigned_trainer_id",
    ):
        key = (
            record["enrollment_id"],
            record["session__topic__course_id"],
        )
        delivered.setdefault(key, set()).add(record["session__topic_id"])
        teacher = " ".join(filter(None, (
            record["session__taught_by__user__first_name"],
            record["session__taught_by__user__last_name"],
        ))) or record["session__taught_by__user__username"]
        date_and_id = (record["session__session_date"], record["session_id"])
        if key not in latest_teacher or date_and_id > latest_teacher[key][0]:
            latest_teacher[key] = (date_and_id, teacher)
        assigned_id = record["session__assigned_trainer_id"]
        if assigned_id and assigned_id != record["session__taught_by_id"]:
            substitutes[key] = substitutes.get(key, 0) + 1
    verified_practice = {}
    for record in TrainingDeliveryEnrollment.objects.filter(
        enrollment__status="active",
        session__topic__is_published=True,
        practice_verified_at__isnull=False,
    ).values(
        "enrollment_id", "session__topic__course_id", "session__topic_id"
    ):
        key = (record["enrollment_id"], record["session__topic__course_id"])
        verified_practice.setdefault(key, set()).add(record["session__topic_id"])

    doubt_counts = {}
    for doubt in LMSTopicDoubt.objects.filter(
        status="open", enrollment__status="active"
    ).values("enrollment_id", "topic__course_id"):
        key = (doubt["enrollment_id"], doubt["topic__course_id"])
        doubt_counts[key] = doubt_counts.get(key, 0) + 1
    weekly_trainer = {}
    for assignment in WeeklyTeachingAssignment.objects.select_related(
        "trainer", "topic"
    ).order_by("week_start", "id"):
        key = (assignment.enrollment_id, assignment.topic.course_id)
        weekly_trainer[key] = assignment.trainer.name

    closed_topics = {}
    latest_approved = {}
    for report in TrainerTeachingReport.objects.filter(
        review_status="approved"
    ).select_related("assignment__topic", "submitted_by").order_by(
        "submitted_at", "id"
    ):
        topic_key = (report.assignment.enrollment_id, report.assignment.topic_id)
        latest_approved[topic_key] = report

    for report in latest_approved.values():
        key = (report.assignment.enrollment_id, report.assignment.topic.course_id)
        topic_id = report.assignment.topic_id
        delivered.setdefault(key, set()).add(topic_id)
        teacher_key = (report.taught_on, report.id)
        if key not in latest_teacher or teacher_key > latest_teacher[key][0]:
            latest_teacher[key] = (teacher_key, report.submitted_by.name)
        if report.lab_completed:
            verified_practice.setdefault(key, set()).add(topic_id)
        if report.student_response == "doubt":
            doubt_counts[key] = doubt_counts.get(key, 0) + 1
        if report.closed_at:
            closed_topics.setdefault(key, set()).add(topic_id)

    pending_by_course = {}
    for report in TrainerTeachingReport.objects.filter(
        review_status="submitted"
    ).select_related("assignment__topic"):
        key = (report.assignment.enrollment_id, report.assignment.topic.course_id)
        pending_by_course[key] = pending_by_course.get(key, 0) + 1
    pending_reviews = sum(pending_by_course.values())

    plans = {
        (plan.enrollment_id, plan.course_id): plan
        for plan in TrainingDeliveryPlan.objects.select_related(
            "assigned_trainer__user"
        )
    }
    rows = []
    enrollments = Enrollment.objects.filter(
        status="active", student__status="active"
    ).select_related(
        "student", "course"
    ).prefetch_related("course__included_courses").order_by(
        "branch", "student__name", "id"
    )
    for enrollment in enrollments:
        courses = list(enrollment.course.included_courses.all()) if (
            enrollment.course.is_package
        ) else [enrollment.course]
        for course in courses:
            item_ids = all_items.get(course.id, set())
            if not item_ids:
                continue
            key = (enrollment.id, course.id)
            plan = plans.get(key)
            due_date = (
                (plan.revised_completion_date or plan.target_completion_date)
                if plan else None
            )
            rows.append({
                "enrollment_id": enrollment.id,
                "branch": enrollment.branch or enrollment.student.branch,
                "student": enrollment.student,
                "course": course,
                "taught": len(delivered.get(key, set()) & item_ids),
                "lab_verified": len(verified_practice.get(key, set()) & item_ids),
                "closed": len(closed_topics.get(key, set()) & item_ids),
                "weekly_trainer": weekly_trainer.get(key),
                "total": len(item_ids),
                "course_total": full_course_counts.get(course.id, len(item_ids)),
                "doubts": doubt_counts.get(key, 0),
                "pending_reviews": pending_by_course.get(key, 0),
                "last_teacher": latest_teacher[key][1] if key in latest_teacher else None,
                "substitute_sessions": substitutes.get(key, 0),
                "plan": plan,
                "due_date": due_date,
                "overdue": bool(
                    due_date and due_date < timezone.localdate()
                    and (
                        len(item_ids) < full_course_counts.get(course.id, len(item_ids))
                        or len(delivered.get(key, set()) & item_ids) < len(item_ids)
                        or len(verified_practice.get(key, set()) & item_ids) < len(item_ids)
                        or len(closed_topics.get(key, set()) & item_ids) < len(item_ids)
                    )
                ),
            })
    return render(request, "lms/delivery_report.html", {
        "rows": rows,
        "today": timezone.localdate(),
        "missing_targets": sum(1 for row in rows if not row["due_date"]),
        "overdue_count": sum(1 for row in rows if row["overdue"]),
        "open_doubt_count": sum(row["doubts"] for row in rows),
        "pending_reviews": pending_reviews,
    })


@login_required
def delivery_student_history(request, enrollment_id, course_id):
    staff = _staff(request)
    if not _can_manage(request, staff):
        return HttpResponseForbidden("Management access required.")

    enrollment = get_object_or_404(
        Enrollment.objects.select_related("student", "course"),
        pk=enrollment_id,
    )
    course = get_object_or_404(Course, pk=course_id)
    if not _course_for(enrollment, course.id):
        return HttpResponseForbidden("Course does not belong to this enrollment.")

    records = TrainingDeliveryEnrollment.objects.filter(
        enrollment=enrollment,
        session__topic__course=course,
    ).select_related(
        "session__topic",
        "session__taught_by__user",
        "session__assigned_trainer__user",
        "practice_verified_by__user",
    ).order_by("-session__session_date", "-session_id")

    new_reports = TrainerTeachingReport.objects.filter(
        assignment__enrollment=enrollment,
        assignment__topic__course=course,
    ).select_related(
        "assignment__topic", "assignment__trainer",
        "submitted_by", "reviewed_by__user", "closed_by__user",
    ).order_by("-submitted_at", "-id")
    return render(request, "lms/delivery_student_history.html", {
        "enrollment": enrollment,
        "course": course,
        "records": records,
        "new_reports": new_reports,
    })


@login_required
@require_POST
def verify_lab_practice(request, record_id):
    return HttpResponseForbidden(
        "Use the new weekly trainer submission workflow."
    )
    staff = _staff(request)
    if not staff or (
        staff.department not in ("training", "management", "operations")
        and not request.user.is_superuser
    ):
        return HttpResponseForbidden("Trainer access required.")
    evidence = request.POST.get("practice_evidence", "").strip()[:1000]
    if len(evidence) < 5:
        return HttpResponseForbidden("Describe the completed lab task.")

    with transaction.atomic():
        record = get_object_or_404(
            TrainingDeliveryEnrollment.objects.select_for_update().select_related(
                "session__topic", "enrollment__course"
            ),
            pk=record_id,
        )
        if not _allowed_enrollments(staff, request).filter(
            pk=record.enrollment_id
        ).exists():
            return HttpResponseForbidden("Student is outside your branch.")
        if not _course_for(record.enrollment, record.session.topic.course_id):
            return HttpResponseForbidden("Course does not match enrollment.")
        if record.practice_verified_at:
            return HttpResponseForbidden("Practice has already been verified.")
        record.practice_verified_at = timezone.now()
        record.practice_verified_by = staff
        record.practice_evidence = evidence
        record.save(update_fields=[
            "practice_verified_at", "practice_verified_by", "practice_evidence"
        ])
    return redirect(
        f"{reverse('lms:trainer_delivery')}?course={record.session.topic.course_id}"
    )
