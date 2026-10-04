from datetime import date, datetime, time, timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Enquiry, EnquiryActivity

MARKER = "followup_completed"
RESULTS = {
    "contacted": "Contacted successfully",
    "message_sent": "WhatsApp message sent (staff confirmed)",
    "no_answer": "No answer / retry required",
    "closed": "Closed / not interested",
}

def work_summary(request, enquiries):
    today = timezone.localdate()
    period = request.GET.get("work_period", "today")
    start = end = today
    error = ""
    if period == "week":
        start = today - timedelta(days=6)
    elif period == "custom":
        try:
            start = date.fromisoformat(request.GET.get("work_start", ""))
            end = date.fromisoformat(request.GET.get("work_end", ""))
            if start > end:
                raise ValueError()
        except ValueError:
            start = end = today
            error = "Invalid custom dates; showing today."
    else:
        period = "today"
    zone = timezone.get_current_timezone()
    lower = timezone.make_aware(datetime.combine(start, time.min), zone)
    upper = timezone.make_aware(datetime.combine(end + timedelta(days=1), time.min), zone)
    activities = EnquiryActivity.objects.filter(
        enquiry_id__in=enquiries.values("pk"),
        created_at__gte=lower, created_at__lt=upper,
    )
    # Staff work only; public website notes are not staff activity.
    activities = activities.filter(
        Q(created_by__is_staff=True) | Q(created_by__is_superuser=True)
    ).filter(
        Q(activity_type__in=("call", "whatsapp")) |
        Q(activity_type="followup", campaign_key=MARKER)
    )
    confirmed = Q(activity_type="followup", campaign_key=MARKER)
    activity_map = {
        r["created_by_id"]: r
        for r in activities.values("created_by_id").annotate(
            calls=Count("pk", filter=Q(activity_type="call")),
            whatsapp=Count("pk", filter=Q(activity_type="whatsapp")),
            completed=Count("pk", filter=confirmed),
            contacted=Count("pk", filter=confirmed & Q(message__startswith="Follow-up result recorded: Contacted successfully.")),
            sent=Count("pk", filter=confirmed & Q(message__startswith="Follow-up result recorded: WhatsApp message sent")),
            retry=Count("pk", filter=confirmed & Q(message__startswith="Follow-up result recorded: No answer")),

            handled=Count("enquiry_id", filter=confirmed, distinct=True),
        )
    }
    pending = enquiries.exclude(status__in=("converted", "closed"))
    assignments = {
        r["assigned_user_id"]: r
        for r in pending.values("assigned_user_id").annotate(
            today=Count("pk", filter=Q(followup_date=today)),
            overdue=Count("pk", filter=Q(followup_date__lt=today)),
        )
    }
    ids = set(activity_map) | set(assignments)
    from django.contrib.auth import get_user_model
    users = {
        u.pk: u for u in get_user_model().objects.filter(
            pk__in=[i for i in ids if i is not None]
        )
    }
    rows = []
    for uid in ids:
        if uid is None:
            continue
        a = activity_map.get(uid, {})
        p = assignments.get(uid, {})
        user = users.get(uid)
        if uid is not None and (
            user is None or not (user.is_staff or user.is_superuser)
        ):
            continue
        if not any(a.get(key, 0) for key in (
            "calls", "whatsapp", "completed", "handled"
        )) and not any(p.get(key, 0) for key in ("today", "overdue")):
            continue
        rows.append({
            "name": (user.get_full_name() or user.username) if user else "Unassigned enquiries",
            "calls": a.get("calls", 0), "whatsapp": a.get("whatsapp", 0),
            "completed": a.get("completed", 0), "handled": a.get("handled", 0),
            "contacted": a.get("contacted", 0),
            "sent": a.get("sent", 0), "retry": a.get("retry", 0),

            "today": p.get("today", 0), "overdue": p.get("overdue", 0),
        })
    rows.sort(key=lambda r: (-r["handled"], -r["calls"], r["name"]))
    params = request.GET.copy()
    for key in ("work_period", "work_start", "work_end"):
        params.pop(key, None)
    return {
        "period": period, "start": start, "end": end, "error": error,
        "rows": rows, "preserved": list(params.lists()),
        "calls": activities.filter(activity_type="call").count(),
        "whatsapp": activities.filter(activity_type="whatsapp").count(),
        "handled": activities.filter(confirmed).values("enquiry_id").distinct().count(),
        "completed": activities.filter(confirmed).count(),
        "today": pending.filter(followup_date=today).count(),
        "overdue": pending.filter(followup_date__lt=today).count(),
    }

@login_required(login_url="staff_login")
@require_POST
def complete_enquiry_followup(request, enquiry_id):
    from .views import user_can_access_enquiry
    user = request.user
    if not user.is_active or not (user.is_staff or user.is_superuser):
        return HttpResponseForbidden("Active staff access required.")
    if not user.is_superuser:
        profile = getattr(user, "staff_profile", None)
        if not profile or not profile.is_active or not profile.branch:
            return HttpResponseForbidden("Active staff branch required.")
    result = request.POST.get("contact_result", "")
    notes = request.POST.get("contact_notes", "").strip()
    next_date = None
    error = ""
    if result not in RESULTS:
        error = "Choose a valid result."
    elif not notes or len(notes) > 2000:
        error = "Add notes (maximum 2000 characters)."
    elif result != "closed":
        value = request.POST.get("next_contact_date", "").strip()
        try:
            next_date = (
                date.fromisoformat(value) if value
                else timezone.localdate() + timedelta(
                    days=1 if result == "no_answer" else 2
                )
            )
            if next_date <= timezone.localdate():
                raise ValueError()
        except ValueError:
            error = "Choose a next follow-up date after today."
    with transaction.atomic():
        enquiry = get_object_or_404(Enquiry.objects.select_for_update(), pk=enquiry_id)
        if not user_can_access_enquiry(user, enquiry):
            return HttpResponseForbidden("Another branch enquiry.")
        if enquiry.status in ("converted", "closed"):
            error = "This enquiry is already converted or closed."
        if error:
            messages.error(request, error)
        else:
            old_date = enquiry.followup_date
            enquiry.followup_date = next_date
            enquiry.followup_notes = notes
            enquiry.status = "closed" if result == "closed" else "followup"
            enquiry.save(update_fields=["followup_date", "followup_notes", "status"])
            EnquiryActivity.objects.create(
                enquiry=enquiry, activity_type="followup",
                campaign_key=MARKER, created_by=user,
                message=(
                    f"Follow-up result recorded: {RESULTS[result]}. "
                    f"Previous due: {old_date or 'Not scheduled'}. "
                    f"Next follow-up: {next_date or 'Closed'}. Notes: {notes}"
                ),
            )
            messages.success(request, "Follow-up result saved; pending schedule updated.")
    return redirect("enquiry_detail", enquiry_id=enquiry_id)

def decorate_leads(groups, today):
    groups = [list(group) for group in groups]
    ids = {e.pk for group in groups for e in group}
    latest = {}
    for activity in EnquiryActivity.objects.filter(
        enquiry_id__in=ids, activity_type="followup", campaign_key=MARKER,
    ).select_related("created_by").order_by("-created_at", "-pk"):
        latest.setdefault(activity.enquiry_id, activity)
    for group in groups:
        for enquiry in group:
            enquiry.work_pending = ""
            if enquiry.status not in ("converted", "closed"):
                if enquiry.followup_date:
                    if enquiry.followup_date < today:
                        enquiry.work_pending = "Overdue"
                    elif enquiry.followup_date == today:
                        enquiry.work_pending = "Due today"
                    else:
                        enquiry.work_pending = "Upcoming"
                else:
                    enquiry.work_pending = "Not scheduled"
            a = latest.get(enquiry.pk)
            enquiry.work_result = ""
            enquiry.work_actor = ""
            enquiry.work_when = None
            enquiry.work_retry = False
            if a:
                enquiry.work_result = a.message.split(". Previous due:", 1)[0].replace(
                    "Follow-up result recorded: ", "", 1
                ).rstrip(".")
                enquiry.work_retry = a.message.startswith(
                    "Follow-up result recorded: No answer"
                )
                enquiry.work_when = a.created_at
                enquiry.work_actor = (
                    a.created_by.get_full_name() or a.created_by.username
                ) if a.created_by else "Deleted user"
    return groups


def schedule_action_followup(enquiry_id, user, action, campaign_key=None):
    days = (
        1 if action == "call"
        else 7 if campaign_key == "kamotheAnniversaryExistingStudent"
        else 2
    )
    with transaction.atomic():
        enquiry = Enquiry.objects.select_for_update().get(pk=enquiry_id)
        if enquiry.status in ("converted", "closed"):
            return enquiry.followup_date
        old_date = enquiry.followup_date
        next_date = timezone.localdate() + timedelta(days=days)
        enquiry.followup_date = next_date
        enquiry.status = "followup"
        enquiry.save(update_fields=["followup_date", "status"])
        EnquiryActivity.objects.create(
            enquiry=enquiry, activity_type="followup", created_by=user,
            message=(
                f"Next follow-up automatically scheduled after {action} action. "
                f"Previous due: {old_date or 'Not scheduled'}. "
                f"Next follow-up: {next_date}. "
                "Action initiation does not confirm successful contact."
            ),
        )
        return next_date
