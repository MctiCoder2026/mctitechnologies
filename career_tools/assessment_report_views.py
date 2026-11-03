from datetime import date, datetime, time, timedelta
from io import BytesIO
from xml.sax.saxutils import escape

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import CharField, Value, OuterRef, Subquery
from django.db.models.functions import Coalesce, Lower, NullIf, Trim
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Count, Q, Max
from urllib.parse import quote
import re
from django.urls import reverse
from django.utils import timezone

from .models import (AptitudeAttempt, CareerCompassAttempt, AssessmentBranchAssignment, AssessmentBranchAssignmentLog, AssessmentFollowUp)
from assessments.models import AssessmentAttempt, HiringApplication

BRANCHES = (
    "kharghar", "panvel", "koperkhairane", "kamothe",
    "ghansoli", "nerul", "head_office",
)
KINDS = {
    "aptitude": "Aptitude",
    "compass": "Career Compass",
    "ai": "AI Ready",
    "scholarship": "Scholarship",
    "cyber": "Cyber Awareness",
    "hiring": "Hiring",
    "ssc": "SSC Practice",
}


def _branch_expression(*fields):
    return Lower(Trim(Coalesce(
        *[NullIf(Trim(field), Value("")) for field in fields],
        Value("unassigned"), output_field=CharField(),
    )))


def _assigned_branch(kind, fallback):
    override = AssessmentBranchAssignment.objects.filter(
        kind=kind, attempt_id=OuterRef("pk")
    ).values("branch")[:1]
    return Coalesce(Subquery(override, output_field=CharField()), fallback, output_field=CharField())


def _related(obj, name):
    try:
        return getattr(obj, name)
    except ObjectDoesNotExist:
        return None


def _dates(params):
    today = timezone.localdate()
    period = params.get("period", "today")
    if period == "today":
        return today, today, period
    if period == "week":
        return today - timedelta(days=6), today, period
    if period == "all":
        return None, None, period
    if period != "custom":
        raise ValueError("Invalid date filter.")
    start = date.fromisoformat(params.get("start", ""))
    end = date.fromisoformat(params.get("end", ""))
    if start > end:
        raise ValueError("Start date must be before end date.")
    return start, end, period


def _filter(qs, date_field, start, end, branch):
    if branch:
        qs = qs.filter(report_branch=branch)
    if start:
        zone = timezone.get_current_timezone()
        lower = timezone.make_aware(datetime.combine(start, time.min), zone)
        upper = timezone.make_aware(
            datetime.combine(end + timedelta(days=1), time.min), zone
        )
        qs = qs.filter(**{
            date_field + "__gte": lower,
            date_field + "__lt": upper,
        })
    return qs


def _row(kind, obj, name, mobile, when, score, detail, url=""):
    return {
        "kind": kind, "label": KINDS[kind], "name": name,
        "mobile": mobile, "branch": obj.report_branch,
        "date": when, "score": score, "detail": detail, "url": url,
        "id": obj.pk,
    }


def _collect(start, end, branch, selected_kind, management, search):
    rows = []
    if selected_kind in ("", "aptitude"):
        qs = AptitudeAttempt.objects.filter(status="completed").select_related(
            "profile", "profile__enquiry", "profile__student"
        ).annotate(report_branch=_assigned_branch("aptitude", _branch_expression(
            "profile__preferred_branch", "profile__enquiry__branch",
            "profile__student__branch",
        )))
        for a in _filter(qs, "completed_at", start, end, branch).iterator():
            detail = (
                f"Correct: {a.correct_answers}/{a.total_questions}; "
                f"Numerical: {a.numerical_score}%; Logical: {a.logical_score}%; "
                f"Verbal: {a.verbal_score}%; Computer: {a.computer_score}%; "
                f"Career: {a.career_score}%"
            )
            rows.append(_row(
                "aptitude", a, a.profile.full_name, a.profile.mobile,
                a.completed_at, a.score_percentage, detail,
                reverse("career_tools:counsellor_profile_detail",
                        args=[a.profile_id]),
            ))

    if selected_kind in ("", "compass"):
        qs = CareerCompassAttempt.objects.filter(
            status="completed"
        ).select_related("profile", "profile__enquiry", "profile__student").annotate(
            report_branch=_assigned_branch("compass", _branch_expression(
                "profile__preferred_branch", "profile__enquiry__branch",
                "profile__student__branch",
            ))
        )
        for a in _filter(qs, "completed_at", start, end, branch).iterator():
            detail = (
                f"Directions: {a.top_direction}, {a.second_direction}, "
                f"{a.third_direction}; Counselling: "
                f"{a.get_counselling_status_display()}"
            )
            rows.append(_row(
                "compass", a, a.profile.full_name, a.profile.mobile,
                a.completed_at, None, detail,
                reverse("career_tools:counsellor_profile_detail",
                        args=[a.profile_id]),
            ))

    slugs = {
        "ai": [
            "ai-ready-maharashtra-2026",
            "ai-ready-maharashtra-2026-marathi",
        ],
        "cyber": ["mcti-cyber-fraud-awareness-2026"],
    }
    for kind in ("ai", "scholarship", "cyber", "ssc"):
        if selected_kind not in ("", kind):
            continue
        qs = AssessmentAttempt.objects.filter(status="completed").select_related(
            "assessment", "participant_profile",
            "participant_profile__enquiry", "result", "scholarship_result",
        )
        if kind == "scholarship":
            qs = qs.filter(scholarship_result__isnull=False)
        elif kind == "ssc":
            qs = qs.filter(assessment__assessment_type="exam_preparation", assessment__slug__startswith="ssc-")
        else:
            qs = qs.filter(assessment__slug__in=slugs[kind])
        qs = qs.annotate(report_branch=_assigned_branch(kind, _branch_expression(
            "scholarship_result__preferred_branch",
            "participant_profile__enquiry__branch",
        )))
        for a in _filter(qs, "completed_at", start, end, branch).iterator():
            result = _related(a, "result")
            detail = f"Marks: {a.score}/{a.total_marks}"
            if kind == "ssc":
                detail += f"; Subject: {a.assessment.title}"
            if result:
                detail += f"; Result: {result.result_title or result.result_band}"
            scholarship = _related(a, "scholarship_result")
            if kind == "scholarship" and scholarship:
                detail += (
                    f"; Scholarship: {scholarship.scholarship_percentage}%; "
                    f"Course: {scholarship.selected_course}; "
                    f"Status: {scholarship.get_claim_status_display()}"
                )
            rows.append(_row(
                kind, a, a.participant_name, a.participant_mobile,
                a.completed_at, a.percentage, detail,
            ))

    if management and selected_kind in ("", "hiring") and branch in ("", "unassigned"):
        qs = HiringApplication.objects.select_related(
            "candidate", "job_role", "assessment_attempt"
        ).annotate(report_branch=Value("unassigned", output_field=CharField()))
        for a in _filter(qs, "created_at", start, end, branch).iterator():
            attempt = a.assessment_attempt
            score = attempt.percentage if attempt and attempt.status == "completed" else None
            detail = (
                f"Role: {a.job_role}; Status: {a.get_status_display()}; "
                f"Employment: {a.get_employment_type_display()}"
            )
            rows.append(_row(
                "hiring", a, a.candidate.full_name, a.candidate.mobile,
                a.created_at, score, detail,
            ))

    if search:
        needle = search.casefold()
        rows = [r for r in rows if needle in (
            r["name"] + " " + r["mobile"] + " " + r["detail"]
        ).casefold()]
    rows.sort(key=lambda r: (
        r["date"].timestamp() if r["date"] else 0, r["id"]
    ), reverse=True)
    return rows


def _export(rows, format_name, title):
    headers = ["Date", "Assessment", "Name", "Mobile", "Branch", "Score (%)", "Performance"]
    values = [
        [
            timezone.localtime(r["date"]).strftime("%d %b %Y %H:%M") if r["date"] else "",
            r["label"], r["name"], r["mobile"], r["branch"],
            float(r["score"]) if r["score"] is not None else "",
            r["detail"],
        ]
        for r in rows
    ]
    if format_name == "xlsx":
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment
        wb = Workbook()
        ws = wb.active
        ws.title = "Assessment Reports"
        ws.append(headers)
        for data in values:
            ws.append(data)
            for cell in ws[ws.max_row]:
                if isinstance(cell.value, str):
                    cell.data_type = "s"
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="171717")
        for column, width in zip("ABCDEFG", (22, 22, 26, 18, 20, 15, 90)):
            ws.column_dimensions[column].width = width
        for row in ws.iter_rows(min_row=2):
            row[-1].alignment = Alignment(wrap_text=True, vertical="top")
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        output = BytesIO()
        wb.save(output)
        response = HttpResponse(
            output.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    else:
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, LongTable, TableStyle
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        font = "Helvetica"
        if __import__("os").path.exists(font_path):
            if "MCTIReport" not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont("MCTIReport", font_path))
            font = "MCTIReport"
        styles = getSampleStyleSheet()
        small = ParagraphStyle("ReportCell", fontName=font, fontSize=7, leading=10)
        output = BytesIO()
        doc = SimpleDocTemplate(
            output, pagesize=landscape(A4),
            rightMargin=22, leftMargin=22, topMargin=25, bottomMargin=30,
        )
        story = [
            Paragraph("MCTI Technologies — Assessment Reports", styles["Title"]),
            Paragraph(escape(title), styles["Normal"]),
            Paragraph(f"Records: {len(rows)}", styles["Normal"]),
            Spacer(1, 12),
        ]
        data = [[Paragraph(escape(str(v)), small) for v in headers]]
        data += [[Paragraph(escape(str(v)), small) for v in row] for row in values]
        table = LongTable(data, repeatRows=1, colWidths=[80, 80, 100, 75, 75, 55, 330])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#ff7200")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#dddddd")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f7f7")]),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        # Fit the table inside landscape A4.
        table._argW = [w * (landscape(A4)[0] - 44) / 795 for w in table._argW]
        story.append(table)
        def footer(canvas, document):
            canvas.setFont("Helvetica", 8)
            canvas.drawString(22, 15, "An Initiative by Maharashtra Computer Training Institute")
            canvas.drawRightString(landscape(A4)[0]-22, 15, f"Page {document.page}")
        doc.build(story, onFirstPage=footer, onLaterPages=footer)
        response = HttpResponse(output.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="MCTI-Assessment-Reports.{format_name}"'
    )
    response["Cache-Control"] = "private, no-store"
    return response


@login_required(login_url="staff_login")
def assessment_reports(request):
    user = request.user
    if not user.is_active or not (user.is_staff or user.is_superuser):
        return HttpResponseForbidden("Staff access required.")
    staff = _related(user, "staff_profile")
    management = user.is_superuser or bool(
        staff and staff.is_active
        and (staff.branch or "").strip().lower() == "head_office"
    )
    if not management and not (staff and staff.is_active and staff.branch):
        return HttpResponseForbidden("An active staff branch is required.")
    branch = (
        request.GET.get("branch", "").strip().lower()
        if management else staff.branch.strip().lower()
    )
    if branch and branch not in (*BRANCHES, "unassigned"):
        return HttpResponseBadRequest("Invalid branch.")
    kind = request.GET.get("kind", "").strip()
    if kind and (kind not in KINDS or (kind == "hiring" and not management)):
        return HttpResponseForbidden("This report is not available.")
    try:
        start, end, period = _dates(request.GET)
    except ValueError:
        return HttpResponseBadRequest("Choose valid start and end dates.")
    search = request.GET.get("q", "").strip()
    rows = _collect(start, end, branch, kind, management, search)
    title = (
        f"Branch: {branch.title() if branch else 'All branches'} | "
        f"Period: {start or 'All dates'} to {end or 'All dates'}"
    )
    export = request.GET.get("export", "")
    if export:
        if export not in ("xlsx", "pdf"):
            return HttpResponseBadRequest("Invalid export format.")
        return _export(rows, export, title)
    params = request.GET.copy()
    params.pop("page", None)
    params.pop("export", None)
    summary = {}
    for row in rows:
        summary[row["branch"]] = summary.get(row["branch"], 0) + 1
    cards = [
        {"key": key, "label": label, "count": sum(r["kind"] == key for r in rows)}
        for key, label in KINDS.items() if management or key != "hiring"
    ]
    latest = {}
    for item in AssessmentFollowUp.objects.filter(
        kind__in=[r["kind"] for r in rows],
        attempt_id__in=[r["id"] for r in rows], action="outcome"
    ).order_by("-created_at", "-pk"):
        latest.setdefault((item.kind, item.attempt_id), item)
    for row in rows:
        candidate = latest.get((row["kind"], row["id"]))
        row["followup"] = candidate if candidate and candidate.branch == row["branch"] else None
    response = render(request, "career_tools/assessment_reports.html", {
        "page": Paginator(rows, 50).get_page(request.GET.get("page")),
        "total": len(rows), "cards": cards,
        "summary": sorted(summary.items()),
        "management": management, "branches": (*BRANCHES, "unassigned"),
        "selected_branch": branch, "selected_kind": kind,
        "period": period, "start": start, "end": end, "search": search,
        "params": params.urlencode(), "title": title,
    })
    response["Cache-Control"] = "private, no-store"
    return response


@login_required(login_url="staff_login")
def assign_assessment_branch(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    user = request.user
    if not user.is_active or not (user.is_staff or user.is_superuser):
        return HttpResponseForbidden("Staff access required")
    staff = _related(user, "staff_profile")
    management = user.is_superuser or bool(
        staff and staff.is_active and (staff.branch or "").strip().lower() == "head_office"
    )
    if not management:
        return HttpResponseForbidden("HO only")
    kind = request.POST.get("kind", "").strip()
    branch = request.POST.get("branch", "").strip().lower()
    if kind not in ("aptitude", "compass", "ai", "scholarship", "cyber", "ssc"):
        return HttpResponseBadRequest("Invalid assessment")
    if branch not in BRANCHES or branch == "head_office":
        return HttpResponseBadRequest("Invalid destination branch")
    try:
        attempt_id = int(request.POST.get("attempt_id", ""))
        if attempt_id < 1:
            raise ValueError()
    except (TypeError, ValueError):
        return HttpResponseBadRequest("Invalid attempt ID")
    if kind == "aptitude":
        exists = AptitudeAttempt.objects.filter(pk=attempt_id, status="completed").exists()
    elif kind == "compass":
        exists = CareerCompassAttempt.objects.filter(pk=attempt_id, status="completed").exists()
    else:
        qs = AssessmentAttempt.objects.filter(pk=attempt_id, status="completed")
        if kind == "ssc":
            qs = qs.filter(assessment__assessment_type="exam_preparation", assessment__slug__startswith="ssc-")
        elif kind == "ai":
            qs = qs.filter(assessment__slug__in=["ai-ready-maharashtra-2026", "ai-ready-maharashtra-2026-marathi"])
        elif kind == "cyber":
            qs = qs.filter(assessment__slug="mcti-cyber-fraud-awareness-2026")
        elif kind == "scholarship":
            qs = qs.filter(scholarship_result__isnull=False)
        exists = qs.exists()
    if not exists:
        return HttpResponseBadRequest("Completed assessment not found")
    with transaction.atomic():
        # Serialize concurrent updates for this attempt with an advisory lock.
        from django.db import connection
        lock_key = f"mcti_assessment:{kind}:{attempt_id}"
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))", [lock_key])
        record, created = AssessmentBranchAssignment.objects.get_or_create(
            kind=kind, attempt_id=attempt_id,
            defaults={"branch": branch, "assigned_by": user},
        )
        old_branch = "" if created else record.branch
        if created or old_branch != branch:
            if not created:
                record.branch = branch
                record.assigned_by = user
                record.save(update_fields=["branch", "assigned_by", "assigned_at"])
            AssessmentBranchAssignmentLog.objects.create(
                kind=kind, attempt_id=attempt_id, old_branch=old_branch,
                new_branch=branch, changed_by=user,
            )
    return redirect("career_tools:assessment_reports")


FOLLOWUP_RESULTS = {"contacted", "sent", "no_answer", "interested", "not_interested"}


def _followup_access(request, kind, attempt_id):
    user = request.user
    if not user.is_active or not (user.is_staff or user.is_superuser):
        return None
    staff = _related(user, "staff_profile")
    management = user.is_superuser or bool(staff and staff.is_active and (staff.branch or "").strip().lower() == "head_office")
    if not management and not (staff and staff.is_active and staff.branch):
        return None
    if kind not in KINDS or kind == "hiring":
        return None
    branch = "" if management else staff.branch.strip().lower()
    rows = _collect(None, None, branch, kind, management, "")
    for row in rows:
        if row["id"] == attempt_id and row["kind"] == kind:
            return row
    return None


@login_required(login_url="staff_login")
@require_POST
def assessment_followup(request):
    kind = request.POST.get("kind", "").strip()
    try:
        attempt_id = int(request.POST.get("attempt_id", ""))
        if attempt_id <= 0:
            raise ValueError()
    except ValueError:
        return HttpResponseBadRequest("Invalid attempt")
    row = _followup_access(request, kind, attempt_id)
    if row is None or row["branch"] not in BRANCHES:
        return HttpResponseForbidden("Assessment is not assigned to your branch")
    action = request.POST.get("action", "")
    if action == "whatsapp":
        mobile = re.sub(r"\D", "", str(row["mobile"] or ""))
        if len(mobile) == 12 and mobile.startswith("91"):
            mobile = mobile[2:]
        if len(mobile) != 10 or mobile[0] not in "6789":
            return HttpResponseBadRequest("Valid mobile number unavailable")
        AssessmentFollowUp.objects.create(kind=kind, attempt_id=attempt_id, branch=row["branch"], created_by=request.user, action="whatsapp_opened")
        if kind == "ssc":
            from local_site.models import Branch

            centre = Branch.objects.filter(
                slug__iexact=row["branch"],
                is_active=True
            ).first()

            centre_details = ""
            if centre:
                centre_details = (
                    f"\n\n📍 *Your MCTI Centre: {centre.name}*\n"
                    f"🏢 *Address:* {centre.address.strip()}"
                )
                if centre.google_map_url:
                    centre_details += (
                        f"\n🗺️ *Google Maps:* {centre.google_map_url.strip()}"
                    )

            message = (
                f"🎓 *Hello {row['name']},*\n\n"
                "⭐ *इयत्ता १० वीच्या बोर्ड परीक्षेसाठी मनःपूर्वक शुभेच्छा!* 🌸\n\n"
                "तुमची मेहनत, नियमित सराव आणि आत्मविश्वास तुम्हाला नक्कीच यश मिळवून देईल! ⭐\n\n"
                "📚 *सराव सुरूच ठेवा!*\n"
                "MCTI च्या मोफत SSC Online Practice Test वर नियमित सराव करा.\n\n"
                "📝 *Free SSC Practice Test:*\n"
                "https://mctitechnologies.com/ssc-exam-preparation/\n\n"
                "🎁 *तुमचे Scholarship Coupon जपून ठेवा!*\n"
                "बोर्ड परीक्षेनंतर उन्हाळ्याच्या सुट्टीत MCTI च्या Computer व Career-Oriented Courses मध्ये प्रवेश घेताना या कूपनद्वारे विशेष शिष्यवृत्ती मिळवण्याची संधी आहे.\n\n"
                "💪 *नियमित सराव करा आणि यशस्वी व्हा!*\n\n"
                "🧡 *Maharashtra Computer Training Institute (MCTI)*"
            )
            if row["branch"].strip().lower() == "kharghar":
                review_message = (
                "⭐ आमचा मोफत SSC Practice उपक्रम उपयुक्त वाटला असेल, तर Google वर तुमचा अनुभव शेअर करा.\n"
                "👉 *Google Review:*\n"
                "https://maps.app.goo.gl/YTDBzs4AQMCoEEnMA?g_st=ic\n\n"
                )
                message += "\n\n" + review_message.strip()
            message += centre_details
        else:
            message = f"Hello {row['name']}, this is Maharashtra Computer Training Institute. Thank you for participating in our {row['label']} assessment. We would like to guide you on courses and career opportunities. Please reply when convenient."
        if kind == "ssc":
            from django.http import HttpResponse
            from django.utils.html import escape
            import json

            phone = "91" + mobile
            encoded_message = json.dumps(message, ensure_ascii=True)
            encoded_phone = json.dumps(phone)

            response = HttpResponse(
                '<!doctype html><html><head><meta charset="utf-8">'
                '<meta name="referrer" content="no-referrer">'
                '<title>Opening WhatsApp</title></head><body>'
                '<p>Opening WhatsApp...</p>'
                '<script>'
                'const phone=' + encoded_phone + ';'
                'const message=' + encoded_message + ';'
                'const url="https://api.whatsapp.com/send?phone="'
                '+phone+"&text="+encodeURIComponent(message);'
                'window.location.replace(url);'
                '</script>'
                '<p>If WhatsApp does not open, please return to CRM and try again.</p>'
                '</body></html>',
                content_type="text/html; charset=utf-8"
            )
        else:
            response = redirect("https://wa.me/91" + mobile + "?text=" + quote(message))
        response["Cache-Control"] = "no-store"
        return response
    if action != "outcome":
        return HttpResponseBadRequest("Invalid action")
    result = request.POST.get("result", "")
    notes = request.POST.get("notes", "").strip()
    if result not in FOLLOWUP_RESULTS or not notes or len(notes) > 2000:
        return HttpResponseBadRequest("Choose an outcome and add notes (up to 2000 characters)")
    next_date = None
    if result != "not_interested":
        value = request.POST.get("next_followup", "").strip()
        try:
            next_date = date.fromisoformat(value)
            if next_date <= timezone.localdate():
                raise ValueError()
        except ValueError:
            return HttpResponseBadRequest("Next follow-up date must be in the future")
    AssessmentFollowUp.objects.create(kind=kind, attempt_id=attempt_id, branch=row["branch"], created_by=request.user, action="outcome", result=result, notes=notes, next_followup=next_date)
    messages.success(request, "Assessment follow-up saved")
    return redirect("career_tools:assessment_reports")


def assessment_followup_summary(user, start_date=None, end_date=None):
    staff = _related(user, "staff_profile")
    management = user.is_superuser or bool(staff and staff.is_active and (staff.branch or "").strip().lower() == "head_office")
    qs = AssessmentFollowUp.objects.all()
    if not management:
        if not staff or not staff.is_active or not staff.branch:
            return {"allowed": False}
        qs = qs.filter(branch=staff.branch.strip().lower())
    if start_date:
        qs = qs.filter(created_at__date__gte=start_date)
    if end_date:
        qs = qs.filter(created_at__date__lte=end_date)
    stats = qs.aggregate(opened=Count("pk", filter=Q(action="whatsapp_opened")), completed=Count("pk", filter=Q(action="outcome")), interested=Count("pk", filter=Q(action="outcome", result="interested")))
    branch_rows = list(qs.values("branch").annotate(opened=Count("pk", filter=Q(action="whatsapp_opened")), completed=Count("pk", filter=Q(action="outcome")), interested=Count("pk", filter=Q(result="interested", action="outcome"))).order_by("branch"))
    staff_rows = list(qs.values("created_by__username", "branch").annotate(opened=Count("pk", filter=Q(action="whatsapp_opened")), completed=Count("pk", filter=Q(action="outcome"))).order_by("-completed", "-opened")[:30])
    return {"allowed": True, "management": management, "stats": stats, "branch_rows": branch_rows, "staff_rows": staff_rows}
