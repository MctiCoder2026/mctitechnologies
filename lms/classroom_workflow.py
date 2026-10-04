from datetime import datetime, timedelta

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.models import Course, StaffProfile, Student
from .delivery_views import _allowed_enrollments, _can_manage, _course_for, _staff
from .models import (
    ClassroomTrainer, TrainingChecklistItem,
    WeeklyTeachingAssignment, TrainerTeachingReport,
)


def _staff_can_assign(request):
    staff = _staff(request)
    if not staff or staff.department not in ("operations", "management", "training"):
        return None
    return staff


def trainer_login(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username", "").strip(),
            password=request.POST.get("password", ""),
        )
        trainer = ClassroomTrainer.objects.filter(
            user=user, is_active=True, user__is_active=True,
        ).first() if user and not user.is_staff and not user.is_superuser else None
        if trainer:
            login(request, user)
            return redirect("lms:trainer_workspace")
        return render(request, "lms/classroom_trainer_login.html", {
            "error": "Invalid trainer credentials.",
        })
    return render(request, "lms/classroom_trainer_login.html")


@login_required(login_url="lms:trainer_login")
@require_POST
def trainer_logout(request):
    logout(request)
    return redirect("lms:trainer_login")


@login_required
def staff_workspace(request):
    staff = _staff_can_assign(request)
    if not staff:
        return HttpResponseForbidden("Branch staff access required.")
    enrollments = list(_allowed_enrollments(staff, request).order_by(
        "student__name", "id"
    ))
    selected_id = request.GET.get("course", "")
    course = Course.objects.filter(
        pk=selected_id, training_checklist_items__is_published=True,
    ).first() if selected_id.isdigit() else None
    allowed = [e for e in enrollments if course and _course_for(e, course.id)]
    trainers = ClassroomTrainer.objects.filter(is_active=True)
    if not _can_manage(request, staff):
        trainers = trainers.filter(branch__iexact=staff.branch)
    assignments = WeeklyTeachingAssignment.objects.filter(
        enrollment_id__in=[e.id for e in enrollments],
    ).select_related(
        "enrollment__student", "topic__course", "trainer",
    ).order_by("-week_start", "-id")[:100]
    reports = TrainerTeachingReport.objects.filter(
        assignment__enrollment_id__in=[e.id for e in enrollments],
    ).select_related(
        "assignment__enrollment__student", "assignment__topic",
        "submitted_by", "assignment__trainer",
    ).order_by("-submitted_at")[:100]
    return render(request, "lms/classroom_staff.html", {
        "staff": staff,
        "is_head_office": _can_manage(request, staff),
        "courses": Course.objects.filter(
            training_checklist_items__is_published=True,
        ).distinct().order_by("title"),
        "course": course,
        "enrollments": allowed,
        "topics": TrainingChecklistItem.objects.filter(
            course=course, is_published=True,
        ).order_by("module_order", "order", "id") if course else [],
        "trainers": trainers.order_by("name"),
        "assignments": assignments,
        "reports": reports,
        "this_monday": timezone.localdate() - timedelta(
            days=timezone.localdate().weekday()
        ),
    })


@login_required
@require_POST
def create_trainer(request):
    staff = _staff_can_assign(request)
    if not staff:
        return HttpResponseForbidden("Branch staff access required.")
    name = request.POST.get("name", "").strip()[:120]
    username = request.POST.get("username", "").strip().lower()[:150]
    password = request.POST.get("password", "")
    branch = request.POST.get("branch", "").strip().lower()
    valid_branches = {value for value, _ in StaffProfile.BRANCH_CHOICES}
    if not _can_manage(request, staff):
        branch = staff.branch
    if not name or not username or len(password) < 10 or branch not in valid_branches:
        return HttpResponseForbidden("Enter name, unique username, branch and a 10+ character password.")
    if branch == "head_office":
        return HttpResponseForbidden("Select a teaching branch.")
    User = get_user_model()
    if User.objects.filter(username__iexact=username).exists():
        return HttpResponseForbidden("Trainer username already exists.")
    with transaction.atomic():
        user = User.objects.create_user(username=username, password=password)
        ClassroomTrainer.objects.create(user=user, name=name, branch=branch)
    return redirect("lms:staff_classroom")



# SEVEN_TOPIC_QUEUE_V1
def _training_completed_topics(enrollment_id):
    """Latest non-rejected report determines each topic's completion."""
    latest = {}
    records = TrainerTeachingReport.objects.filter(
        assignment__enrollment_id=enrollment_id,
    ).exclude(review_status="rejected").order_by("-submitted_at", "-id")
    for report in records:
        latest.setdefault(report.assignment.topic_id, report)
    return {
        topic_id for topic_id, report in latest.items()
        if report.closed_at or (
            report.student_response == "satisfied"
            and report.trainer_approved_at
        )
    }


def _refill_training_queue(anchor):
    """Maintain up to seven pending topics; never change LMS access."""
    with transaction.atomic():
        enrollment = type(anchor.enrollment).objects.select_for_update().get(
            pk=anchor.enrollment_id,
        )
        trainer = anchor.trainer
        if (
            enrollment.status != "active"
            or not trainer.is_active
            or not trainer.user.is_active
        ):
            return 0

        branch = (
            enrollment.branch or enrollment.student.branch or ""
        ).strip().lower()
        if trainer.branch.strip().lower() != branch:
            return 0

        course = enrollment.course
        if course.is_package:
            course_ids = list(
                course.included_courses.filter(is_active=True)
                .order_by("display_order", "pk")
                .values_list("pk", flat=True)
            )
        else:
            course_ids = [course.pk]

        if anchor.topic.course_id not in course_ids:
            return 0

        items = []
        for course_id in course_ids:
            items.extend(
                TrainingChecklistItem.objects.filter(
                    course_id=course_id, is_published=True,
                ).order_by("module_order", "order", "pk")
            )
        if not items:
            return 0

        assigned_ids = set(
            WeeklyTeachingAssignment.objects.filter(
                enrollment_id=enrollment.pk,
            ).values_list("topic_id", flat=True)
        )
        completed = _training_completed_topics(enrollment.pk)
        slots = max(0, 7 - len(assigned_ids - completed))
        if not slots:
            return 0

        # Preserve the existing starting point for previously trained students.
        positions = [
            i for i, item in enumerate(items)
            if item.pk in assigned_ids
        ]
        if not positions:
            return 0
        start = min(positions)
        today = timezone.localdate()
        monday = today - timedelta(days=today.weekday())
        created = 0

        for item in items[start:]:
            if item.pk in assigned_ids or item.pk in completed:
                continue
            WeeklyTeachingAssignment.objects.create(
                enrollment=enrollment,
                topic=item,
                trainer=trainer,
                week_start=monday,
                assigned_by=anchor.assigned_by,
                instructions=(
                    "Automatically assigned in the seven-topic training queue. "
                    "Record the actual teaching date and practical evidence."
                ),
            )
            assigned_ids.add(item.pk)
            created += 1
            if created >= slots:
                break
        return created

@login_required
@require_POST
def assign_weekly_topic(request):
    staff = _staff_can_assign(request)
    if not staff:
        return HttpResponseForbidden("Branch staff access required.")
    enrollment = get_object_or_404(
        _allowed_enrollments(staff, request),
        pk=request.POST.get("enrollment_id"),
    )
    topic = get_object_or_404(
        TrainingChecklistItem,
        pk=request.POST.get("topic_id"), is_published=True,
    )
    trainer = get_object_or_404(
        ClassroomTrainer, pk=request.POST.get("trainer_id"), is_active=True,
        user__is_active=True,
    )
    if not _course_for(enrollment, topic.course_id):
        return HttpResponseForbidden("Topic does not belong to this student course.")
    branch = (enrollment.branch or enrollment.student.branch or "").strip().lower()
    if trainer.branch.lower() != branch:
        return HttpResponseForbidden("Trainer and student must belong to the same branch.")
    instructions = request.POST.get("instructions", "").strip()[:2000]
    with transaction.atomic():
        # Serialise assignments for this enrollment to prevent duplicate topics.
        type(enrollment).objects.select_for_update().get(pk=enrollment.pk)
        existing = WeeklyTeachingAssignment.objects.filter(
            enrollment=enrollment, topic=topic,
        ).order_by("-week_start", "-id").first()
        if existing:
            if existing.teaching_reports.exists():
                return HttpResponseForbidden(
                    "A class was submitted for this topic. Contact management to change its trainer."
                )
            existing.trainer = trainer
            existing.instructions = instructions
            existing.assigned_by = staff
            existing.save(update_fields=["trainer", "instructions", "assigned_by"])
        else:
            assigned_ids = set(
                WeeklyTeachingAssignment.objects.filter(
                    enrollment=enrollment,
                ).values_list("topic_id", flat=True)
            )
            completed = _training_completed_topics(enrollment.pk)
            if len(assigned_ids - completed) >= 7:
                return HttpResponseForbidden(
                    "Seven topics are pending. Complete a topic before adding another."
                )
            today = timezone.localdate()
            WeeklyTeachingAssignment.objects.create(
                enrollment=enrollment,
                topic=topic,
                trainer=trainer,
                week_start=today - timedelta(days=today.weekday()),
                assigned_by=staff,
                instructions=instructions,
            )
    anchor = WeeklyTeachingAssignment.objects.filter(
        enrollment=enrollment, topic=topic,
    ).order_by("-week_start", "-id").first()
    if anchor:
        _refill_training_queue(anchor)
    return redirect(f"/lms/classroom/staff/?course={topic.course_id}")


def _trainer(request):
    if not request.user.is_authenticated:
        return None
    return ClassroomTrainer.objects.filter(
        user=request.user, user__is_active=True, is_active=True,
    ).first()


@login_required(login_url="lms:trainer_login")
def trainer_workspace(request):
    trainer = _trainer(request)
    if not trainer:
        return HttpResponseForbidden("Trainer access required.")
    assignments = list(WeeklyTeachingAssignment.objects.filter(
        trainer=trainer,
        enrollment__status="active",
    ).select_related(
        "enrollment__student", "topic", "topic__course",
    ).prefetch_related("teaching_reports").order_by("-week_start", "id")[:200])
    current_monday = timezone.localdate() - timedelta(
        days=timezone.localdate().weekday()
    )
    coverage_assignments = list(WeeklyTeachingAssignment.objects.filter(
        trainer__branch__iexact=trainer.branch,
        enrollment__status="active",
    ).exclude(trainer=trainer).select_related(
        "trainer", "enrollment__student", "topic", "topic__course",
    ).prefetch_related("teaching_reports").order_by("id")[:100])
    for assignment in assignments + coverage_assignments:
        reports = sorted(
            assignment.teaching_reports.all(),
            key=lambda report: (report.submitted_at, report.id),
        )
        assignment.latest_report = reports[-1] if reports else None
    return render(request, "lms/classroom_trainer.html", {
        "trainer": trainer, "assignments": assignments,
        "coverage_assignments": coverage_assignments,
        "today": timezone.localdate(),
    })


@login_required(login_url="lms:trainer_login")
@require_POST
def submit_class(request, assignment_id):
    trainer = _trainer(request)
    if not trainer:
        return HttpResponseForbidden("Trainer access required.")
    assignment = get_object_or_404(
        WeeklyTeachingAssignment.objects.select_related(
            "enrollment", "topic", "trainer",
        ),
        pk=assignment_id,
    )
    is_substitute = assignment.trainer_id != trainer.id
    if is_substitute and (
        assignment.trainer.branch.lower() != trainer.branch.lower()
        or assignment.enrollment.status != "active"
    ):
        return HttpResponseForbidden("You may cover only an active class in your branch.")
    try:
        taught_on = datetime.strptime(
            request.POST.get("taught_on", ""), "%Y-%m-%d"
        ).date()
    except ValueError:
        return HttpResponseForbidden("Invalid teaching date.")
    if taught_on > timezone.localdate() or taught_on < assignment.enrollment.enrollment_date:
        return HttpResponseForbidden("Class date is outside enrollment or in the future.")
    if is_substitute and taught_on != timezone.localdate():
        return HttpResponseForbidden("A substitute must submit on the class day.")
    coverage_reason = request.POST.get("coverage_reason", "").strip()[:1000]
    if is_substitute and len(coverage_reason) < 5:
        return HttpResponseForbidden("Enter why you covered this class.")
    teaching_note = request.POST.get("teaching_note", "").strip()[:2000]
    lab_completed = request.POST.get("lab_completed") == "on"
    lab_evidence = request.POST.get("lab_evidence", "").strip()[:1000]
    if len(teaching_note) < 10:
        return HttpResponseForbidden("Describe what was taught.")
    if lab_completed and len(lab_evidence) < 5:
        messages.error(
            request,
            "Lab practice tick kiya hai. Student ne kya practical complete kiya, likhiye.",
        )
        return redirect("lms:trainer_workspace")
    with transaction.atomic():
        # Preserve submission locks; there is no daily topic cap.
        ClassroomTrainer.objects.select_for_update().get(pk=trainer.pk)
        Student.objects.select_for_update().get(pk=assignment.enrollment.student_id)
        assignment = WeeklyTeachingAssignment.objects.select_for_update().get(
            pk=assignment.pk
        )
        last = assignment.teaching_reports.order_by("-submitted_at", "-id").first()

        # Staff review is a non-blocking quality audit.
        # Trainer may re-teach only when the student has raised a doubt.
        if last and last.closed_at:
            return HttpResponseForbidden("This topic is already closed.")

        if last and last.student_response == "pending":
            return HttpResponseForbidden(
                "Wait for the student's response before teaching this topic again."
            )

        if last and last.student_response == "satisfied":
            return HttpResponseForbidden(
                "Student has completed this topic. Continue with the next assigned topic."
            )

        TrainerTeachingReport.objects.create(
            assignment=assignment, submitted_by=trainer,
            taught_on=taught_on, teaching_note=teaching_note,
            coverage_reason=coverage_reason if is_substitute else "",
            lab_completed=lab_completed, lab_evidence=lab_evidence,
        )
    return redirect("lms:trainer_workspace")


@login_required(login_url="lms:trainer_login")
@require_POST
def trainer_approve_completion(request, report_id):
    trainer = _trainer(request)
    if not trainer:
        return HttpResponseForbidden("Trainer access required.")

    initial = get_object_or_404(
        TrainerTeachingReport.objects.select_related(
            "assignment__enrollment",
        ),
        pk=report_id,
    )
    if initial.submitted_by_id != trainer.pk:
        return HttpResponseForbidden(
            "Only the trainer who taught this class can approve completion."
        )

    with transaction.atomic():
        enrollment = initial.assignment.enrollment
        type(enrollment).objects.select_for_update().get(pk=enrollment.pk)
        report = get_object_or_404(
            TrainerTeachingReport.objects.select_for_update(),
            pk=report_id,
        )
        if report.submitted_by_id != trainer.pk:
            return HttpResponseForbidden("Trainer mismatch.")
        if enrollment.status != "active":
            return HttpResponseForbidden("Enrollment is not active.")
        if report.review_status == "rejected":
            return HttpResponseForbidden("Correct the rejected report first.")
        if report.student_response != "satisfied":
            return HttpResponseForbidden(
                "Student must mark the topic satisfied before trainer approval."
            )

        latest = TrainerTeachingReport.objects.filter(
            assignment__enrollment_id=enrollment.pk,
            assignment__topic_id=report.assignment.topic_id,
        ).exclude(review_status="rejected").order_by(
            "-submitted_at", "-id",
        ).first()
        if not latest or latest.pk != report.pk:
            return HttpResponseForbidden("Approve only the latest training record.")

        if not report.trainer_approved_at:
            if report.closed_at:
                return HttpResponseForbidden("This topic is already closed.")
            report.trainer_approved_at = timezone.now()
            report.save(update_fields=["trainer_approved_at"])

        added = _refill_training_queue(report.assignment)

    messages.success(
        request,
        f"Completion approved. {added} topic(s) added to the training queue."
    )
    return redirect("lms:trainer_workspace")


@login_required
@require_POST
def review_class(request, report_id):
    staff = _staff_can_assign(request)
    if not staff:
        return HttpResponseForbidden("Staff access required.")
    report = get_object_or_404(
        TrainerTeachingReport.objects.select_related(
            "assignment__enrollment__student", "assignment__trainer",
        ),
        pk=report_id,
        assignment__enrollment_id__in=_allowed_enrollments(
            staff, request
        ).values_list("id", flat=True),
    )
    action = request.POST.get("decision")
    reason = request.POST.get("review_note", "").strip()[:2000]
    if action not in ("approved", "rejected"):
        return HttpResponseForbidden("Choose approve or reject.")
    if action == "rejected" and len(reason) < 5:
        return HttpResponseForbidden("Add a correction reason.")
    with transaction.atomic():
        report = TrainerTeachingReport.objects.select_for_update().get(pk=report.pk)
        if report.review_status != "submitted":
            return HttpResponseForbidden("Report has already been reviewed.")
        if report.assignment.teaching_reports.order_by("-submitted_at", "-id").first().pk != report.pk:
            return HttpResponseForbidden("Only the latest submission can be reviewed.")
        report.review_status = action
        report.reviewed_by = staff
        report.reviewed_at = timezone.now()
        report.review_note = reason
        report.save(update_fields=[
            "review_status", "reviewed_by", "reviewed_at", "review_note",
        ])
        if action == "approved":
            from .models import ClassroomTrainerAttendance
            ClassroomTrainerAttendance.objects.get_or_create(
                trainer=report.submitted_by,
                attendance_date=report.taught_on,
                defaults={
                    "source_report": report,
                    "approved_by": staff,
                },
            )
    return redirect("lms:staff_classroom")


@login_required
def student_classroom(request):
    student = get_object_or_404(Student, user=request.user)
    assignments = WeeklyTeachingAssignment.objects.filter(
        enrollment__student=student, enrollment__status="active",
    ).select_related(
        "enrollment__course", "topic", "topic__course",
    ).prefetch_related("teaching_reports").order_by(
        "topic__course__title", "topic__module_order", "topic__order"
    )
    grouped = {}
    for assignment in assignments:
        key = (assignment.enrollment_id, assignment.topic_id)
        # Trainer submission is immediately visible to the student.
        # Staff review remains a separate, non-blocking quality audit.
        visible_reports = [
            r for r in assignment.teaching_reports.all()
            if r.review_status != "rejected"
        ]
        existing = grouped.get(key)
        if not existing or (
            assignment.week_start, assignment.id
        ) > (
            existing["assignment"].week_start, existing["assignment"].id
        ):
            grouped[key] = {"assignment": assignment, "report": None}
        for report in visible_reports:
            row = grouped[key]
            if not row["report"] or (
                report.submitted_at, report.id
            ) > (
                row["report"].submitted_at, row["report"].id
            ):
                row["report"] = report
    rows = list(grouped.values())
    rows.sort(key=lambda row: (
        row["assignment"].topic.course.title,
        row["assignment"].topic.module_order,
        row["assignment"].topic.order,
    ))
    return render(request, "lms/classroom_student.html", {
        "student": student, "rows": rows,
    })


@login_required
@require_POST
def student_feedback(request, report_id):
    student = get_object_or_404(Student, user=request.user)
    choice = request.POST.get("response")
    note = request.POST.get("student_note", "").strip()[:1000]
    if choice not in ("satisfied", "doubt"):
        return HttpResponseForbidden("Choose satisfied or doubt.")
    if choice == "doubt" and len(note) < 5:
        return HttpResponseForbidden("Please describe your doubt.")
    with transaction.atomic():
        report = get_object_or_404(
            TrainerTeachingReport.objects.select_for_update().select_related(
                "assignment__enrollment"
            ),
            pk=report_id,
            assignment__enrollment__student=student,
            assignment__enrollment__status="active",
        )
        if report.student_response != "pending" or report.closed_at:
            return HttpResponseForbidden("Feedback is already submitted.")
        latest_report = TrainerTeachingReport.objects.filter(
            assignment__enrollment_id=report.assignment.enrollment_id,
            assignment__topic_id=report.assignment.topic_id,
        ).exclude(
            review_status="rejected",
        ).order_by("-submitted_at", "-id").first()
        if not latest_report or latest_report.pk != report.pk:
            return HttpResponseForbidden("Respond to the latest training record.")
        report.student_response = choice
        report.student_note = note
        report.student_responded_at = timezone.now()
        report.save(update_fields=[
            "student_response", "student_note", "student_responded_at",
        ])

        # Student feedback is now saved here only.
        # Next-topic progression happens after trainer approval.

    return redirect("lms:student_delivery")


@login_required
@require_POST
def close_topic(request, report_id):
    staff = _staff_can_assign(request)
    if not staff:
        return HttpResponseForbidden("Staff access required.")
    report = get_object_or_404(
        TrainerTeachingReport,
        pk=report_id,
        assignment__enrollment_id__in=_allowed_enrollments(
            staff, request
        ).values_list("id", flat=True),
    )
    with transaction.atomic():
        report = TrainerTeachingReport.objects.select_for_update().get(pk=report.pk)
        if (report.review_status != "approved"
                or report.student_response != "satisfied"
                or not report.lab_completed
                or report.closed_at):
            return HttpResponseForbidden(
                "Staff can close only approved classes with verified lab and satisfied student."
            )
        latest_for_topic = TrainerTeachingReport.objects.filter(
            assignment__enrollment_id=report.assignment.enrollment_id,
            assignment__topic_id=report.assignment.topic_id,
            review_status="approved",
        ).order_by("-submitted_at", "-id").first()
        if not latest_for_topic or latest_for_topic.pk != report.pk:
            return HttpResponseForbidden("Only the latest approved class can be closed.")
        report.closed_by = staff
        report.closed_at = timezone.now()
        report.save(update_fields=["closed_by", "closed_at"])

        # Staff closure is audit-only.
        # Training progression is controlled by trainer approval.
    return redirect("lms:staff_classroom")


@login_required
@require_POST
def deactivate_trainer(request, trainer_id):
    staff = _staff_can_assign(request)
    if not staff:
        return HttpResponseForbidden("Staff access required.")
    trainer = get_object_or_404(ClassroomTrainer, pk=trainer_id, is_active=True)
    if not _can_manage(request, staff) and trainer.branch.lower() != staff.branch.lower():
        return HttpResponseForbidden("Trainer belongs to another branch.")
    trainer.is_active = False
    trainer.save(update_fields=["is_active"])
    return redirect("lms:staff_classroom")
