from datetime import date, timedelta
from fractions import Fraction
from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from .models import Attendance, StudentAttendanceAward

def attendance_awards(request, branch):
    if not request.user.is_active or not request.user.is_superuser:
        return HttpResponse("Owner access required.", status=403)
    current = timezone.localdate().replace(day=1)
    previous = (current-timedelta(days=1)).replace(day=1)
    value = request.GET.get("award_month", previous.strftime("%Y-%m"))
    try:
        month = date.fromisoformat(value+"-01")
        if month >= current:
            raise ValueError()
    except ValueError:
        return HttpResponse("Select a completed month using YYYY-MM.", status=400)
    next_month = (month.replace(day=28)+timedelta(days=4)).replace(day=1)
    records = Attendance.objects.filter(
        attendance_date__gte=month, attendance_date__lt=next_month,
    )
    if branch:
        records = records.filter(student__branch__iexact=branch)
    rows = list(records.values(
        "student_id", "student__name", "student__student_id", "student__branch",
    ).annotate(
        present=Count("pk", filter=Q(status="present")),
        absent=Count("pk", filter=Q(status="absent")),
        leave=Count("pk", filter=Q(status="leave")),
        marked=Count("pk", filter=Q(status__in=("present", "absent", "leave"))),
    ))
    best = {}
    for r in rows:
        r["branch"] = (r["student__branch"] or "").strip().lower()
        r["ratio"] = Fraction(r["present"], r["marked"]) if r["marked"] else Fraction(0)
        r["percentage"] = round(float(r["ratio"])*100, 1)
        r["eligible"] = r["marked"] >= 10 and r["present"] > 0 and bool(r["branch"])
        if r["eligible"]:
            rank = (
                (r["ratio"], r["present"])
                if month >= date(2026, 10, 1)
                else (r["ratio"], 0)
            )
            best[r["branch"]] = max(
                best.get(r["branch"], (Fraction(0), 0)), rank
            )
    awards = {
        a.student_id: a for a in StudentAttendanceAward.objects.filter(
            month=month, student_id__in=[r["student_id"] for r in rows],
        )
    }
    for r in rows:
        rank = (
            (r["ratio"], r["present"])
            if month >= date(2026, 10, 1)
            else (r["ratio"], 0)
        )
        r["winner"] = r["eligible"] and rank == best.get(r["branch"])
        r["award"] = awards.get(r["student_id"])
    rows.sort(key=lambda r: (
        not r["winner"], not r["eligible"], -r["ratio"],
        -r["present"], r["student__name"],
    ))
    action = request.POST.get("action", "")
    if request.method == "POST" and action in ("student_award_approve", "student_award_given"):
        try:
            sid = int(request.POST.get("student_id", ""))
        except ValueError:
            return HttpResponse("Invalid student.", status=400)
        row = next((r for r in rows if r["student_id"] == sid), None)
        if row is None:
            return HttpResponse("Student not in selected report.", status=400)
        with transaction.atomic():
            if action == "student_award_approve":
                if month < date(2026, 10, 1):
                    return HttpResponse(
                        "Reward points start with October 2026 attendance. "
                        "October awards can be approved from 1 November 2026.",
                        status=400,
                    )
                gift = "500 reward points for the next course"
                if not row["winner"] or not gift or len(gift) > 255:
                    return HttpResponse("Winner and reward description required.", status=400)
                award, created = StudentAttendanceAward.objects.get_or_create(
                    student_id=sid, month=month,
                    defaults={
                        "branch": row["branch"], "present_days": row["present"],
                        "marked_days": row["marked"], "gift_description": gift,
                        "approved_by": request.user,
                    },
                )
                if created:
                    from .student_reward_points import credit_attendance_points
                    credit_attendance_points(award, request.user)
                messages.success(
                    request,
                    "500 reward points credited." if created else "Award already exists.",
                )
            else:
                award = StudentAttendanceAward.objects.select_for_update().filter(
                    student_id=sid, month=month,
                ).first()
                if not award:
                    return HttpResponse("Approve award first.", status=400)
                if award.status == "approved" and not award.reward_points:
                    award.status = "given"
                    award.fulfilled_by = request.user
                    award.fulfilled_at = timezone.now()
                    award.save(update_fields=["status", "fulfilled_by", "fulfilled_at"])
                messages.success(request, "Student award marked as given.")
        return redirect(request.get_full_path()+"#student-attendance-awards")
    history = StudentAttendanceAward.objects.select_related(
        "student", "approved_by", "fulfilled_by",
    )
    if branch:
        history = history.filter(branch__iexact=branch)
    return {
        "award_month": month.strftime("%Y-%m"), "award_month_label": month,
        "award_latest_month": previous.strftime("%Y-%m"),
        "award_points_enabled": month >= date(2026, 10, 1),
        "award_rows": rows, "award_winners": sum(r["winner"] for r in rows),
        "award_history": history[:30],
    }
