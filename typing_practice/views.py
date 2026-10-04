import json

from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.models import Student

from .models import (
    TypingActivity,
    TypingAttempt,
    TypingExam,
    TypingExamAttempt,
    TypingGameAttempt,
    TypingLesson,
    TypingLevelProgress,
    TypingProgress,
)


def get_student(request):
    return get_object_or_404(
        Student,
        user=request.user
    )


def student_branch(student):
    return (student.branch or "").strip()


def parse_decimal(value, default="0"):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal(default)


def previous_exam_passed(student, lesson):
    previous = (
        TypingLesson.objects
        .filter(
            is_active=True,
            order__lt=lesson.order
        )
        .order_by("-order", "-id")
        .first()
    )

    if previous is None:
        return True

    return TypingLevelProgress.objects.filter(
        student=student,
        lesson=previous,
        exam_passed=True
    ).exists()


@login_required
def dashboard(request):

    student = get_student(request)

    lessons = list(
        TypingLesson.objects
        .filter(is_active=True)
        .order_by("order", "id")
    )

    practice_progress = {
        p.lesson_id: p
        for p in TypingProgress.objects.filter(
            student=student
        )
    }

    level_progress = {
        p.lesson_id: p
        for p in TypingLevelProgress.objects.filter(
            student=student
        )
    }

    lesson_data = []

    for item in lessons:

        lp = level_progress.get(item.id)

        lesson_data.append({
            "lesson": item,
            "practice": practice_progress.get(item.id),
            "level": lp,
            "exam_unlocked": previous_exam_passed(
                student,
                item
            ),
        })

    total = len(lessons)

    passed = sum(
        1
        for item in lesson_data
        if item["level"] and
        item["level"].exam_passed
    )

    attempts = TypingAttempt.objects.filter(
        student=student
    )

    best_attempt = attempts.order_by(
        "-wpm"
    ).first()

    return render(
        request,
        "typing_practice/dashboard.html",
        {
            "student": student,
            "certificate_cards": typing_certificate_cards(student),
            "lesson_data": lesson_data,
            "total_lessons": total,
            "passed_lessons": passed,
            "best_wpm": (
                best_attempt.wpm
                if best_attempt else 0
            ),
        }
    )


@login_required
def lesson(request, slug):

    student = get_student(request)

    lesson_obj = get_object_or_404(
        TypingLesson,
        slug=slug,
        is_active=True
    )

    progress_obj = TypingProgress.objects.filter(
        student=student,
        lesson=lesson_obj
    ).first()

    return render(
        request,
        "typing_practice/lesson.html",
        {
            "student": student,
            "lesson": lesson_obj,
            "progress": progress_obj,
        }
    )


@login_required
@require_POST
def save_attempt(request, slug):

    student = get_student(request)

    lesson_obj = get_object_or_404(
        TypingLesson,
        slug=slug,
        is_active=True
    )

    try:
        data = json.loads(
            request.body.decode("utf-8")
        )
    except Exception:
        return JsonResponse(
            {"ok": False, "error": "Invalid data"},
            status=400
        )

    wpm = parse_decimal(data.get("wpm"))
    accuracy = parse_decimal(
        data.get("accuracy")
    )

    try:
        errors = int(data.get("errors", 0))
        typed_characters = int(
            data.get("typed_characters", 0)
        )
        duration_seconds = int(
            data.get("duration_seconds", 0)
        )
    except (TypeError, ValueError):
        return JsonResponse(
            {"ok": False, "error": "Invalid metrics"},
            status=400
        )

    if (
        wpm < 0 or wpm > 300 or
        accuracy < 0 or accuracy > 100 or
        errors < 0 or
        typed_characters < 0 or
        duration_seconds <= 0 or
        duration_seconds > 7200
    ):
        return JsonResponse(
            {"ok": False, "error": "Invalid metrics"},
            status=400
        )

    try:
        active_seconds = int(data.get("active_seconds", 0))
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "Invalid active time"}, status=400)
    if active_seconds < 0 or active_seconds > min(duration_seconds, 300):
        return JsonResponse({"ok": False, "error": "Invalid active time"}, status=400)

    practice_target_met = (
        wpm >= lesson_obj.target_wpm and
        accuracy >= lesson_obj.target_accuracy
    )

    TypingAttempt.objects.create(
        student=student,
        lesson=lesson_obj,
        wpm=wpm,
        accuracy=accuracy,
        errors=errors,
        typed_characters=typed_characters,
        duration_seconds=duration_seconds,
        passed=practice_target_met
    )

    progress_obj, _ = (
        TypingProgress.objects.get_or_create(
            student=student,
            lesson=lesson_obj
        )
    )

    progress_obj.attempts_count += 1

    if wpm > progress_obj.best_wpm:
        progress_obj.best_wpm = wpm

    if accuracy > progress_obj.best_accuracy:
        progress_obj.best_accuracy = accuracy

    if (
        progress_obj.attempts_count == 1 or
        errors < progress_obj.best_errors
    ):
        progress_obj.best_errors = errors

    if practice_target_met:
        progress_obj.is_completed = True

        if not progress_obj.completed_at:
            progress_obj.completed_at = timezone.now()

    progress_obj.save()

    TypingActivity.objects.create(
        student=student,
        branch=student_branch(student),
        activity_type="practice",
        active_seconds=active_seconds,
        duration_seconds=duration_seconds,
        typed_characters=typed_characters
    )

    return JsonResponse({
        "ok": True,
        "passed": practice_target_met,
        "wpm": float(wpm),
        "accuracy": float(accuracy),
        "errors": errors,
        "target_wpm": lesson_obj.target_wpm,
        "target_accuracy": float(
            lesson_obj.target_accuracy
        ),
    })


@login_required
def exam(request, slug):

    student = get_student(request)

    lesson_obj = get_object_or_404(
        TypingLesson,
        slug=slug,
        is_active=True
    )

    exam_obj = get_object_or_404(
        TypingExam,
        lesson=lesson_obj,
        is_active=True
    )

    unlocked = previous_exam_passed(
        student,
        lesson_obj
    )

    level = TypingLevelProgress.objects.filter(
        student=student,
        lesson=lesson_obj
    ).first()

    return render(
        request,
        "typing_practice/exam.html",
        {
            "student": student,
            "lesson": lesson_obj,
            "exam": exam_obj,
            "unlocked": unlocked,
            "level": level,
        }
    )


@login_required
@require_POST
def save_exam_attempt(request, slug):

    student = get_student(request)

    lesson_obj = get_object_or_404(
        TypingLesson,
        slug=slug,
        is_active=True
    )

    exam_obj = get_object_or_404(
        TypingExam,
        lesson=lesson_obj,
        is_active=True
    )

    if not previous_exam_passed(
        student,
        lesson_obj
    ):
        return JsonResponse(
            {
                "ok": False,
                "error": "Complete the previous exam first."
            },
            status=403
        )

    try:
        data = json.loads(
            request.body.decode("utf-8")
        )
    except Exception:
        return JsonResponse(
            {"ok": False, "error": "Invalid data"},
            status=400
        )

    wpm = parse_decimal(data.get("wpm"))
    accuracy = parse_decimal(
        data.get("accuracy")
    )

    try:
        errors = int(data.get("errors", 0))
        typed_characters = int(
            data.get("typed_characters", 0)
        )
        duration_seconds = int(
            data.get("duration_seconds", 0)
        )
    except (TypeError, ValueError):
        return JsonResponse(
            {"ok": False, "error": "Invalid metrics"},
            status=400
        )

    if (
        wpm < 0 or wpm > 300 or
        accuracy < 0 or accuracy > 100 or
        errors < 0 or
        typed_characters < 0 or
        duration_seconds <= 0 or
        duration_seconds > 7200
    ):
        return JsonResponse(
            {"ok": False, "error": "Invalid metrics"},
            status=400
        )

    # Master benchmark requires a complete five-minute attempt.
    passed = (
        wpm >= exam_obj.target_wpm and
        accuracy >= exam_obj.target_accuracy and
        (
            not (11 <= lesson_obj.order <= 20)
            or duration_seconds >= 300
        )
    )

    TypingExamAttempt.objects.create(
        student=student,
        exam=exam_obj,
        branch=student_branch(student),
        wpm=wpm,
        accuracy=accuracy,
        errors=errors,
        typed_characters=typed_characters,
        duration_seconds=duration_seconds,
        passed=passed
    )

    level, _ = (
        TypingLevelProgress.objects
        .get_or_create(
            student=student,
            lesson=lesson_obj
        )
    )

    level.exam_attempts += 1

    if wpm > level.best_exam_wpm:
        level.best_exam_wpm = wpm

    if accuracy > level.best_exam_accuracy:
        level.best_exam_accuracy = accuracy

    if passed:
        level.exam_passed = True

        if not level.passed_at:
            level.passed_at = timezone.now()

    level.save()

    TypingActivity.objects.create(
        student=student,
        branch=student_branch(student),
        activity_type="exam",
        duration_seconds=duration_seconds,
        typed_characters=typed_characters
    )

    speed_needed = max(
        Decimal("0"),
        Decimal(str(exam_obj.target_wpm)) - wpm
    )

    accuracy_needed = max(
        Decimal("0"),
        exam_obj.target_accuracy - accuracy
    )

    return JsonResponse({
        "ok": True,
        "passed": passed,
        "wpm": float(wpm),
        "accuracy": float(accuracy),
        "errors": errors,
        "speed_needed": float(speed_needed),
        "accuracy_needed": float(
            accuracy_needed
        ),
        "target_wpm": exam_obj.target_wpm,
        "target_accuracy": float(
            exam_obj.target_accuracy
        ),
    })


@login_required
def letter_rush(request):

    student = get_student(request)

    return render(
        request,
        "typing_practice/letter_rush.html",
        {"student": student}
    )


@login_required
@require_POST
def save_game_attempt(request):

    student = get_student(request)

    try:
        data = json.loads(
            request.body.decode("utf-8")
        )

        score = max(
            0,
            int(data.get("score", 0))
        )

        duration = max(
            1,
            min(
                600,
                int(
                    data.get(
                        "duration_seconds",
                        60
                    )
                )
            )
        )

        accuracy = parse_decimal(
            data.get("accuracy", 0)
        )

        wpm = parse_decimal(
            data.get("wpm", 0)
        )

    except Exception:
        return JsonResponse(
            {"ok": False},
            status=400
        )

    if (
        accuracy < 0 or accuracy > 100 or
        wpm < 0 or wpm > 300
    ):
        return JsonResponse(
            {"ok": False},
            status=400
        )

    TypingGameAttempt.objects.create(
        student=student,
        game_type="letter_rush",
        branch=student_branch(student),
        score=score,
        wpm=wpm,
        accuracy=accuracy,
        duration_seconds=duration
    )

    TypingActivity.objects.create(
        student=student,
        branch=student_branch(student),
        activity_type="game",
        duration_seconds=duration,
        typed_characters=score
    )

    return JsonResponse({"ok": True})


@login_required
def progress(request):

    student = get_student(request)

    levels = (
        TypingLevelProgress.objects
        .filter(student=student)
        .select_related("lesson")
        .order_by("lesson__order")
    )

    activities = (
        TypingActivity.objects
        .filter(student=student)
    )

    total_seconds = sum(
        item.duration_seconds
        for item in activities
    )

    practice_attempts = (
        TypingAttempt.objects
        .filter(student=student)
        .count()
    )

    exam_attempts = (
        TypingExamAttempt.objects
        .filter(student=student)
        .count()
    )

    exams_passed = (
        TypingLevelProgress.objects
        .filter(
            student=student,
            exam_passed=True
        )
        .count()
    )

    best = (
        TypingExamAttempt.objects
        .filter(student=student)
        .order_by("-wpm")
        .first()
    )

    return render(
        request,
        "typing_practice/progress.html",
        {
            "student": student,
            "levels": levels,
            "certificate_eligible": (
                TypingCertificate.objects.filter(student=student, certificate_type="basic").exists()
                or typing_certificate_status(student)[0]
            ),
            "total_minutes": total_seconds // 60,
            "practice_attempts": practice_attempts,
            "exam_attempts": exam_attempts,
            "exams_passed": exams_passed,
            "best_exam_wpm": (
                best.wpm if best else 0
            ),
            "best_exam_accuracy": (
                best.accuracy if best else 0
            ),
        }
    )


# ============================================================
# PUBLIC TYPING MARKETING FUNNEL
# ============================================================

from django.contrib import messages
from django.shortcuts import redirect
from core.models import Enquiry


PUBLIC_TYPING_LESSON_ORDERS = [1, 2]

TYPING_BRANCHES = [
    ("kharghar", "Kharghar"),
    ("panvel", "Panvel"),
    ("koperkhairane", "Koperkhairane"),
    ("kamothe", "Kamothe"),
    ("ghansoli", "Ghansoli"),
    ("nerul", "Nerul"),
]


def public_typing(request):

    lessons = (
        TypingLesson.objects
        .filter(
            is_active=True,
            order__in=PUBLIC_TYPING_LESSON_ORDERS
        )
        .order_by("order")
    )

    return render(
        request,
        "typing_practice/public_typing.html",
        {"lessons": lessons}
    )


def public_practice(request, slug):

    lesson_obj = get_object_or_404(
        TypingLesson,
        slug=slug,
        is_active=True,
        order__in=PUBLIC_TYPING_LESSON_ORDERS
    )

    return render(
        request,
        "typing_practice/public_practice.html",
        {"lesson": lesson_obj}
    )


def public_game(request):

    return render(
        request,
        "typing_practice/public_game.html"
    )


def public_register(request):

    if request.method == "POST":

        name = request.POST.get(
            "name", ""
        ).strip()

        mobile = request.POST.get(
            "mobile", ""
        ).strip()

        branch = request.POST.get(
            "branch", ""
        ).strip()

        digits = "".join(
            c for c in mobile if c.isdigit()
        )

        if len(digits) > 10 and digits.startswith("91"):
            digits = digits[-10:]

        if (
            not name or
            len(digits) != 10
        ):
            return render(
                request,
                "typing_practice/public_register.html",
                {
                    "branches": TYPING_BRANCHES,
                    "error": (
                        "Please enter your name "
                        "and valid 10-digit mobile number."
                    )
                }
            )

        existing_student = (
            Student.objects
            .filter(mobile__icontains=digits)
            .first()
        )

        if existing_student:
            return render(
                request,
                "typing_practice/public_registered.html",
                {
                    "existing_student": True,
                    "name": existing_student.name,
                }
            )

        recent = (
            Enquiry.objects
            .filter(
                mobile=digits,
                message__icontains="MCTI Typing Lab"
            )
            .order_by("-created_at")
            .first()
        )

        if not recent:
            Enquiry.objects.create(
                name=name,
                mobile=digits,
                branch=branch or None,
                current_status="Student / Typing Practice",
                message=(
                    "MCTI Typing Lab - Free Public Registration. "
                    "Lead Source: Typing Practice."
                ),
                status="new"
            )

        request.session["typing_public_registered"] = True
        request.session["typing_public_name"] = name
        request.session["typing_public_mobile"] = digits
        request.session["typing_public_branch"] = branch

        return render(
            request,
            "typing_practice/public_registered.html",
            {
                "existing_student": False,
                "name": name,
            }
        )

    return render(
        request,
        "typing_practice/public_register.html",
        {"branches": TYPING_BRANCHES}
    )


# ============================================================
# TYPING V2 - STAFF / MANAGEMENT ACCOUNTABILITY
# ============================================================

from datetime import timedelta
from django.contrib.auth.decorators import user_passes_test
from django.db.models import (
    Count,
    Sum,
    Max,
    Q,
)
from core.models import StaffProfile


def typing_staff_profile(user):

    if not user.is_authenticated:
        return None

    try:
        profile = user.staff_profile
    except StaffProfile.DoesNotExist:
        return None

    if not profile.is_active:
        return None

    return profile


def typing_management_user(user):

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if not user.is_staff:
        return False

    profile = typing_staff_profile(user)

    return bool(
        profile and
        profile.branch == "head_office"
    )


def typing_staff_user(user):

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if not user.is_staff:
        return False

    return typing_staff_profile(user) is not None


@login_required
def staff_typing_report(request):
    from django.db.models import Sum, Max
    from django.http import HttpResponseForbidden

    if not typing_staff_user(request.user):
        return HttpResponseForbidden("Staff access required.")

    profile = typing_staff_profile(request.user)
    can_filter_branches = typing_management_user(request.user)
    if can_filter_branches:
        selected_branch = request.GET.get("branch", "").strip().lower()
    else:
        selected_branch = (profile.branch or "").strip().lower() if profile else ""
        if not selected_branch:
            return HttpResponseForbidden("Your staff branch is not assigned.")

    students = Student.objects.all()
    if selected_branch:
        students = students.filter(branch__iexact=selected_branch)
    students = list(students.order_by("name", "id"))
    ids = [student.pk for student in students]
    today = timezone.localdate()
    week_ago = timezone.now() - timedelta(days=7)

    activities = TypingActivity.objects.filter(student_id__in=ids)
    totals = {
        row["student_id"]: row
        for row in activities.values("student_id").annotate(
            seconds=Sum("duration_seconds"), latest=Max("created_at")
        )
    }
    daily = {
        row["student_id"]: row["seconds"] or 0
        for row in activities.filter(
            activity_type="practice", created_at__date=today
        ).values("student_id").annotate(seconds=Sum("duration_seconds"))
    }
    active_ids = set(activities.filter(
        created_at__gte=week_ago
    ).values_list("student_id", flat=True))
    lesson_ids = list(TypingLesson.objects.filter(
        is_active=True
    ).order_by("order", "id").values_list("pk", flat=True))
    passed_map = {}
    for student_id, lesson_id in TypingLevelProgress.objects.filter(
        student_id__in=ids, lesson_id__in=lesson_ids, exam_passed=True
    ).values_list("student_id", "lesson_id"):
        passed_map.setdefault(student_id, set()).add(lesson_id)

    best_map = {}
    final_passed_ids = set()
    for attempt in TypingExamAttempt.objects.filter(
        student_id__in=ids
    ).select_related("exam").order_by("-wpm", "-accuracy", "-created_at"):
        best_map.setdefault(attempt.student_id, attempt)
        if lesson_ids and attempt.passed and attempt.exam.lesson_id == lesson_ids[-1]:
            final_passed_ids.add(attempt.student_id)

    certificates = {
        item.student_id: item
        for item in TypingCertificate.objects.filter(student_id__in=ids)
    }
    rows = []
    for student in students:
        total = totals.get(student.pk, {})
        best = best_map.get(student.pk)
        seconds = daily.get(student.pk, 0)
        passed = len(passed_map.get(student.pk, set()))
        certificate = certificates.get(student.pk)
        eligible = bool(lesson_ids) and passed == len(lesson_ids) and student.pk in final_passed_ids
        rows.append({
            "student": student,
            "active_week": student.pk in active_ids,
            "last_activity": total.get("latest"),
            "minutes": (total.get("seconds") or 0) // 60,
            "today_minutes": round(seconds / 60, 1),
            "daily_done": seconds >= 300,
            "passed": passed,
            "best_wpm": best.wpm if best else 0,
            "best_accuracy": best.accuracy if best else 0,
            "certificate_status": "Issued" if certificate else ("Unlocked" if eligible else "Locked"),
        })

    from datetime import datetime, time
    from urllib.parse import urlencode
    from django.db.models.functions import TruncDate

    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=7)
    zone = timezone.get_current_timezone()
    begin = timezone.make_aware(datetime.combine(week_start, time.min), zone)
    finish = timezone.make_aware(datetime.combine(week_end, time.min), zone)

    weekly_days = {}
    weekly_seconds = {}
    for item in activities.filter(
        activity_type="practice", created_at__gte=begin, created_at__lt=finish
    ).annotate(day=TruncDate("created_at", tzinfo=zone)).values(
        "student_id", "day"
    ).annotate(seconds=Sum("active_seconds")):
        sid = item["student_id"]
        seconds = item["seconds"] or 0
        weekly_seconds[sid] = weekly_seconds.get(sid, 0) + seconds
        if seconds >= 300:
            weekly_days.setdefault(sid, set()).add(item["day"])

    weekly_best = {}
    for attempt in TypingExamAttempt.objects.filter(
        student_id__in=ids, created_at__gte=begin, created_at__lt=finish,
        duration_seconds__gte=60,
    ).order_by("-accuracy", "-wpm", "created_at", "pk"):
        weekly_best.setdefault(attempt.student_id, attempt)

    stars = {}
    for row in rows:
        sid = row["student"].pk
        row["weekly_days"] = len(weekly_days.get(sid, set()))
        row["weekly_minutes"] = round(weekly_seconds.get(sid, 0)/60, 1)
        row["weekly_eligible"] = row["weekly_days"] >= 5
        attempt = weekly_best.get(sid)
        row["weekly_wpm"] = attempt.wpm if attempt else None
        row["weekly_accuracy"] = attempt.accuracy if attempt else None
        row["weekly_star"] = False
        row["whatsapp_url"] = ""
        if row["weekly_eligible"] and attempt:
            branch = (row["student"].branch or "").strip().lower()
            rank = (attempt.accuracy, attempt.wpm, -sid)
            if branch not in stars or rank > stars[branch][0]:
                stars[branch] = (rank, row)

    for rank, row in stars.values():
        row["weekly_star"] = True

    for row in rows:
        if not row["weekly_eligible"]:
            continue
        student = row["student"]
        phone = "".join(c for c in (student.mobile or "") if c.isdigit())
        if len(phone)==10:
            phone="91"+phone
        elif len(phone)==14 and phone.startswith("0091"):
            phone=phone[2:]
        if len(phone)!=12 or not phone.startswith("91"):
            continue
        title = "Weekly Typing Star" if row["weekly_star"] else "Consistent Performer"
        message = (
            f"Congratulations {student.name}!\n"
            f"You are an MCTI {title}!\n"
            f"Week: {week_start:%d %b} to {(week_end-timedelta(days=1)):%d %b %Y}\n"
            f"Practice goal achieved on {row['weekly_days']} days.\n"
        )
        if row["weekly_wpm"] is not None:
            message += (
                f"Weekly benchmark: {row['weekly_wpm']} WPM | "
                f"{row['weekly_accuracy']}% accuracy.\n"
            )
        message += (
            "Your regular practice deserves appreciation. "
            "Please contact your trainer for centre recognition.\n"
            "Keep practising!\nMCTI Technologies"
        )
        row["whatsapp_url"]="https://wa.me/"+phone+"?"+urlencode({"text":message})

    branches = sorted({
        value.strip().lower()
        for value in Student.objects.exclude(branch__isnull=True)
        .values_list("branch", flat=True)
        if value and value.strip()
    }) if can_filter_branches else []
    # Two certificate statuses; batch queries for all report students.
    issued_types = {}
    for sid, kind in TypingCertificate.objects.filter(
        student_id__in=ids,
    ).values_list("student_id", "certificate_type"):
        issued_types.setdefault(sid, set()).add(kind)

    qualifying = {"basic": set(), "master": set()}
    for kind, order, target, duration in [
        ("basic", 10, 30, 60), ("master", 20, 40, 300),
    ]:
        qualifying[kind] = set(TypingExamAttempt.objects.filter(
            student_id__in=ids, passed=True,
            exam__lesson__order=order, exam__lesson__is_active=True,
            wpm__gte=target, accuracy__gte=95,
            duration_seconds__gte=duration,
        ).values_list("student_id", flat=True))

    group_lessons = {
        kind: list(TypingLesson.objects.filter(
            is_active=True, order__gte=first, order__lte=last,
        ).values_list("pk", "order"))
        for kind, first, last in [("basic", 1, 10), ("master", 11, 20)]
    }
    for row in rows:
        sid = row["student"].pk
        labels = []
        for kind, first, last, label in [
            ("basic", 1, 10, "30 WPM"), ("master", 11, 20, "40 WPM"),
        ]:
            group = group_lessons[kind]
            complete_group = sorted(order for pk, order in group) == list(range(first, last + 1))
            ready = (
                complete_group and sid in qualifying[kind]
                and all(pk in passed_map.get(sid, set()) for pk, order in group)
            )
            status = (
                "Issued" if kind in issued_types.get(sid, set())
                else "Unlocked" if ready else "Locked"
            )
            labels.append(label + ": " + status)
        row["certificate_status"] = " | ".join(labels)

    return render(request, "typing_practice/staff_report.html", {
        "rows": rows,
        "selected_branch": selected_branch,
        "branches": branches,
        "total_students": len(rows),
        "active_students": len(active_ids),
        "total_benchmarks": len(lesson_ids),
        "daily_completed": sum(row["daily_done"] for row in rows),
        "can_filter_branches": can_filter_branches,
        "week_start": week_start,
        "week_end": week_end - timedelta(days=1),

    })


@login_required
def management_typing_report(request):

    if not typing_management_user(
        request.user
    ):
        return redirect("branch_dashboard")

    now = timezone.now()
    week_ago = now - timedelta(days=7)

    branches = sorted({
        value.strip().lower()
        for value in Student.objects.exclude(branch__isnull=True)
        .values_list("branch", flat=True)
        if value and value.strip()
    })

    branch_rows = []

    for branch in branches:

        students = Student.objects.filter(
            branch__iexact=branch
        )

        ids = list(
            students.values_list(
                "id",
                flat=True
            )
        )

        activities = TypingActivity.objects.filter(
            student_id__in=ids
        )

        weekly = activities.filter(
            created_at__gte=week_ago
        )

        active_ids = set(
            weekly.values_list(
                "student_id",
                flat=True
            )
        )

        total_seconds = (
            weekly.aggregate(
                total=Sum("duration_seconds")
            )["total"] or 0
        )

        practice_count = weekly.filter(
            activity_type="practice"
        ).count()

        exam_count = weekly.filter(
            activity_type="exam"
        ).count()

        game_count = weekly.filter(
            activity_type="game"
        ).count()

        exams_passed = (
            TypingExamAttempt.objects
            .filter(
                student_id__in=ids,
                passed=True,
                created_at__gte=week_ago
            )
            .count()
        )

        total_students = students.count()

        participation = (
            round(
                len(active_ids) /
                total_students * 100
            )
            if total_students else 0
        )

        branch_rows.append({
            "branch": branch,
            "students": total_students,
            "active": len(active_ids),
            "inactive": max(
                0,
                total_students - len(active_ids)
            ),
            "participation": participation,
            "minutes": total_seconds // 60,
            "practice": practice_count,
            "exam": exam_count,
            "game": game_count,
            "passed": exams_passed,
        })

    public_leads = (
        Enquiry.objects
        .filter(
            message__icontains="MCTI Typing Lab"
        )
        .count()
    )

    total_activity = (
        TypingActivity.objects
        .filter(created_at__gte=week_ago)
    )

    total_active = (
        total_activity
        .values("student_id")
        .distinct()
        .count()
    )

    total_minutes = (
        total_activity.aggregate(
            total=Sum("duration_seconds")
        )["total"] or 0
    ) // 60

    return render(
        request,
        "typing_practice/management_report.html",
        {
            "branch_rows": branch_rows,
            "public_leads": public_leads,
            "total_active": total_active,
            "total_minutes": total_minutes,
        }
    )


# Typing achievement certificates
from .models import TypingCertificate
from django.http import HttpResponse, HttpResponseForbidden
from django.urls import reverse
from django.conf import settings


def typing_certificate_status(student, certificate_type="basic"):
    if certificate_type not in {"basic", "master"}:
        return False, [], None
    first, last, target, seconds = (
        (1, 10, 30, 60) if certificate_type == "basic"
        else (11, 20, 40, 300)
    )
    lessons = list(TypingLesson.objects.filter(
        is_active=True, order__gte=first, order__lte=last,
    ).order_by("order", "pk"))
    if [lesson.order for lesson in lessons] != list(range(first, last + 1)):
        return False, lessons, None
    passed_ids = set(TypingLevelProgress.objects.filter(
        student=student, exam_passed=True,
        lesson_id__in=[lesson.pk for lesson in lessons],
    ).values_list("lesson_id", flat=True))
    if not all(lesson.pk in passed_ids for lesson in lessons):
        return False, lessons, None
    attempt = TypingExamAttempt.objects.filter(
        student=student, exam__lesson=lessons[-1], passed=True,
        wpm__gte=target, accuracy__gte=95,
        duration_seconds__gte=seconds,
    ).order_by("created_at", "pk").first()
    return attempt is not None, lessons, attempt


def typing_certificate_cards(student):
    issued = {
        item.certificate_type: item
        for item in TypingCertificate.objects.filter(student=student)
    }
    cards = []
    for kind, title, description in [
        ("basic", "English Typing - 30 Words Per Minute",
         "Complete Levels 1–10 and the 30 WPM / 95% final benchmark."),
        ("master", "Master in English Typing - 40 Words Per Minute",
         "Complete Levels 11–20 and the five-minute 40 WPM / 95% final benchmark."),
    ]:
        ready = kind in issued or typing_certificate_status(student, kind)[0]
        cards.append({
            "kind": kind, "title": title, "description": description,
            "ready": ready, "issued": kind in issued,
        })
    if "legacy" in issued:
        cards.append({
            "kind": "legacy", "title": "Previously Issued Achievement",
            "description": "Your original certificate remains available.",
            "ready": True, "issued": True,
        })
    return cards


@login_required
def download_typing_certificate(request):
    import io
    import qrcode
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.colors import HexColor
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfbase.pdfmetrics import stringWidth, registerFont
    from reportlab.pdfbase.ttfonts import TTFont

    registerFont(TTFont(
        "MCTITypingRegular",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    ))
    registerFont(TTFont(
        "MCTITypingBold",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    ))

    from pathlib import Path
    from types import SimpleNamespace

    certificate_type = request.GET.get("type", "basic")
    if certificate_type not in {"basic", "master", "legacy"}:
        return HttpResponseForbidden("Unknown certificate type.")
    achievement_title = {
        "basic": "English Typing - 30 Words Per Minute",
        "master": "Master in English Typing - 40 Words Per Minute",
        "legacy": "MCTI English Typing",
    }[certificate_type]
    preview = request.GET.get("preview") == "1"
    if preview and not request.user.is_superuser:
        return HttpResponseForbidden("Preview is available to superusers only.")

    if preview:
        certificate = SimpleNamespace(
            student_name="Sample Student",
            student_identifier="SAMPLE",
            certificate_number="MCTI-TYP-" + certificate_type.upper() + "-PREVIEW",
            achievement_title=achievement_title,
            final_wpm=Decimal("42.00" if certificate_type == "master" else "35.00"),
            final_accuracy=Decimal("96.00"),
            benchmarks_completed=10,
            completed_at=timezone.now(),
            issued_at=timezone.now(),
        )
    else:
        student = get_student(request)
        certificate = TypingCertificate.objects.filter(
            student=student, certificate_type=certificate_type,
        ).first()
    if not preview and certificate is None:
        eligible, lessons, attempt = typing_certificate_status(student, certificate_type)
        if not eligible:
            return HttpResponseForbidden(
                "Complete the required ten levels and qualifying final benchmark for this certificate."
            )
        completed_at = max(
            TypingLevelProgress.objects.filter(
                student=student,
                lesson_id__in=[lesson.pk for lesson in lessons],
                exam_passed=True,
                passed_at__isnull=False,
            ).values_list("passed_at", flat=True),
            default=attempt.created_at,
        )
        certificate, _ = TypingCertificate.objects.get_or_create(
            student=student, certificate_type=certificate_type,
            defaults={
                "student_name": student.name,
                "student_identifier": str(student.student_id),
                "final_wpm": attempt.wpm,
                "final_accuracy": attempt.accuracy,
                "benchmarks_completed": len(lessons),
                "completed_at": completed_at,
            },
        )

    verify_url = (
        request.build_absolute_uri(reverse("typing_practice:dashboard"))
        if preview else request.build_absolute_uri(reverse(
            "typing_practice:verify_certificate",
            args=[certificate.verification_token],
        ))
    )
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="{certificate.certificate_number}.pdf"'
    )
    response["Cache-Control"] = "private, no-store"
    c = canvas.Canvas(response, pagesize=landscape(A4))
    width, height = landscape(A4)
    orange = HexColor("#ff7200")
    dark = HexColor("#171717")
    c.setTitle(certificate.achievement_title + " - Certificate of Achievement")
    c.setStrokeColor(orange)
    c.setLineWidth(4)
    c.rect(25, 25, width-50, height-50)
    c.setStrokeColor(dark)
    c.setLineWidth(1)
    c.rect(34, 34, width-68, height-68)

    assets = Path(settings.BASE_DIR) / "lms/static/lms/certificate"
    logo = assets / "mcti_technologies_logo.png"
    if logo.exists():
        c.drawImage(str(logo), width/2-85, height-115,
                    width=170, height=65, preserveAspectRatio=True, mask="auto")
    else:
        c.setFillColor(orange)
        c.setFont("MCTITypingBold", 26)
        c.drawCentredString(width/2, height-85, "MCTI Technologies")

    def center(value, y, size=14, bold=False, color=dark):
        c.setFillColor(color)
        c.setFont("MCTITypingBold" if bold else "MCTITypingRegular", size)
        c.drawCentredString(width/2, y, str(value))

    center("CERTIFICATE OF ACHIEVEMENT", height-165, 27, True, orange)
    center(certificate.achievement_title, height-198, 17, True)
    center("This certificate is awarded to", height-240, 14)
    name_size = 30
    while name_size > 10 and stringWidth(
        certificate.student_name, "MCTITypingBold", name_size
    ) > width-130:
        name_size -= 1
    center(certificate.student_name, height-280, name_size, True)
    center("For successfully completing all required typing benchmarks.", height-315, 14)
    center(
        f"Final Benchmark: {certificate.final_wpm} WPM  |  "
        f"Accuracy: {certificate.final_accuracy}%",
        height-350, 18, True, orange,
    )
    center(f"Benchmarks Completed: {certificate.benchmarks_completed}", height-377, 12)

    c.setFillColor(dark)
    c.setFont("MCTITypingRegular", 10)
    c.drawString(60, 145, f"Student ID: {certificate.student_identifier}")
    c.drawString(60, 126, f"Certificate No: {certificate.certificate_number}")
    c.drawString(60, 107,
        "Completed: " + timezone.localtime(certificate.completed_at).strftime("%d %b %Y"))
    c.drawString(60, 88,
        "Issued: " + timezone.localtime(certificate.issued_at).strftime("%d %b %Y"))

    qr_buffer = io.BytesIO()
    qrcode.make(verify_url).save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    c.drawImage(ImageReader(qr_buffer), width-155, 88, width=85, height=85)
    c.setFont("MCTITypingRegular", 9)
    c.drawCentredString(width-112, 76, "Demo QR" if preview else "Scan to verify")

    signature = assets / "director_signature.png"
    if signature.exists():
        c.drawImage(str(signature), width/2-60, 100,
                    width=120, height=45, preserveAspectRatio=True, mask="auto")
    center("Authorized Signatory", 88, 11, True)
    center("An Initiative by Maharashtra Computer Training Institute", 55, 10)
    if preview:
        c.saveState()
        c.setFillColor(orange)
        c.setFont("MCTITypingBold", 12)
        c.drawRightString(width-50, height-55, "SAMPLE / PREVIEW")
        c.restoreState()
    c.showPage()
    c.save()
    return response


def verify_typing_certificate(request, verification_token):
    certificate = get_object_or_404(
        TypingCertificate, verification_token=verification_token
    )
    response = render(request, "typing_practice/verify_certificate.html", {
        "certificate": certificate,
    })
    response["X-Robots-Tag"] = "noindex, nofollow"
    return response
