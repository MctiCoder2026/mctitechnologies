
"""Read-only PDF and Excel exports for MCTI V3 course analytics."""

from io import BytesIO
from decimal import Decimal

from django.http import HttpResponse


COLUMNS = [
    ("course", "Course"),
    ("admissions", "Admissions"),
    ("enrollments", "Enrollments"),
    ("billing", "Billing"),
    ("collection", "Collection"),
    ("discounts", "Discounts"),
    ("outstanding", "Cohort Due"),
    ("lifetime_outstanding", "Lifetime Due"),
    ("cancelled_collection", "Cancelled Collection"),
]

MONEY_FIELDS = {
    "billing",
    "collection",
    "discounts",
    "outstanding",
    "lifetime_outstanding",
    "cancelled_collection",
}


def _filters_text(filters):
    return (
        f"Branch: {filters.get('branch') or 'all'} | "
        f"Course ID: {filters.get('course') or 'all'} | "
        f"From: {filters.get('start_date') or 'all'} | "
        f"To: {filters.get('end_date') or 'all'}"
    )


def _value(row, key):
    value = row.get(key, "")
    return value if value is not None else ""


def export_excel(report, filters):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ws = wb.active
    ws.title = "Course Business Report"

    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(COLUMNS))
    ws["A1"] = "MCTI TECHNOLOGIES | COURSE & BUSINESS INTELLIGENCE"
    ws["A1"].font = Font(bold=True, size=15, color="FFFFFF")
    ws["A1"].fill = PatternFill("solid", fgColor="171717")
    ws["A1"].alignment = Alignment(vertical="center")
    ws.row_dimensions[1].height = 30

    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(COLUMNS))
    ws["A2"] = _filters_text(filters)

    for col, (_, title) in enumerate(COLUMNS, 1):
        cell = ws.cell(row=4, column=col, value=title)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="EA580C")
        cell.alignment = Alignment(wrap_text=True)

    for row_number, item in enumerate(report["rows"], 5):
        for col, (key, _) in enumerate(COLUMNS, 1):
            value = _value(item, key)
            if isinstance(value, Decimal):
                value = float(value)
            cell = ws.cell(row=row_number, column=col, value=value)
            if key in MONEY_FIELDS:
                cell.number_format = '#,##0.00'
            if row_number % 2 == 0:
                cell.fill = PatternFill("solid", fgColor="FFF4EB")

    total_row = 5 + len(report["rows"])
    ws.cell(row=total_row, column=1, value="TOTAL")
    for col, (key, _) in enumerate(COLUMNS[1:], 2):
        value = report["totals"].get(key, "")
        if isinstance(value, Decimal):
            value = float(value)
        cell = ws.cell(row=total_row, column=col, value=value)
        if key in MONEY_FIELDS:
            cell.number_format = '#,##0.00'

    for cell in ws[total_row]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="171717")

    note_row = total_row + 2
    ws.cell(
        row=note_row,
        column=1,
        value="Billing: enrollment date | Collection: payment date | "
              "Outstanding: current balance, not historical month-end."
    )

    ws.column_dimensions["A"].width = 38
    for col in range(2, len(COLUMNS) + 1):
        ws.column_dimensions[get_column_letter(col)].width = 21

    ws.freeze_panes = "B5"
    ws.auto_filter.ref = f"A4:I{max(4, total_row - 1)}"
    ws.sheet_view.showGridLines = False

    output = BytesIO()
    wb.save(output)

    response = HttpResponse(
        output.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = (
        'attachment; filename="MCTI_Course_Business_Report.xlsx"'
    )
    return response


def export_pdf(report, filters):
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, LongTable, TableStyle, Spacer
    )
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER

    output = BytesIO()
    doc = SimpleDocTemplate(
        output,
        pagesize=landscape(A4),
        rightMargin=22,
        leftMargin=22,
        topMargin=28,
        bottomMargin=28,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "MCTITitle",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#EA580C"),
        alignment=TA_CENTER,
        spaceAfter=10,
    )
    cell_style = ParagraphStyle(
        "MCTICell",
        parent=styles["Normal"],
        fontSize=7,
        leading=9,
    )

    from xml.sax.saxutils import escape

    elements = [
        Paragraph("MCTI TECHNOLOGIES", title_style),
        Paragraph("Course &amp; Business Intelligence", styles["Heading3"]),
        Paragraph(escape(_filters_text(filters)), styles["Normal"]),
        Spacer(1, 12),
    ]

    headers = [title for _, title in COLUMNS]
    data = [[Paragraph(escape(str(x)), cell_style) for x in headers]]

    for item in report["rows"]:
        data.append([
            Paragraph(
                escape(
                    f"{_value(item, key):,.2f}"
                    if key in MONEY_FIELDS
                    else str(_value(item, key))
                ),
                cell_style,
            )
            for key, _ in COLUMNS
        ])

    totals = report["totals"]
    data.append([
        Paragraph(
            escape(
                "TOTAL" if key == "course"
                else (
                    f"{totals.get(key, 0):,.2f}"
                    if key in MONEY_FIELDS
                    else str(totals.get(key, ""))
                )
            ),
            cell_style,
        )
        for key, _ in COLUMNS
    ])

    table = LongTable(
        data,
        colWidths=[150, 58, 62, 78, 78, 72, 78, 78, 90],
        repeatRows=1,
        hAlign="LEFT",
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EA580C")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#E5E7EB")),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D1D5DB")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 18))

    # MCTI PDF FINANCIAL SUMMARY V1
    elements.append(Paragraph(
        "EXECUTIVE FINANCIAL SUMMARY",
        title_style,
    ))

    summary_fields = [
        ("Total Admissions", "admissions"),
        ("Business Billing", "billing"),
        ("Total Collection", "collection"),
        ("Eligible Collection", "eligible_collection"),
        ("Current Cohort Outstanding", "outstanding"),
        ("Displayed Courses Lifetime Outstanding", "lifetime_outstanding"),
        ("Discounts", "discounts"),
        ("Cancelled Collection", "cancelled_collection"),
    ]

    summary_data = []
    for label, key in summary_fields:
        value = totals.get(key, 0)
        formatted = (
            f"{value:,}"
            if key == "admissions"
            else f"INR {value:,.2f}"
        )
        summary_data.append([
            Paragraph(escape(label), cell_style),
            Paragraph(escape(formatted), cell_style),
        ])

    summary_table = LongTable(
        summary_data,
        colWidths=[300, 160],
        hAlign="CENTER",
    )

    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF4EB")),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1),
         [colors.HexColor("#FFF4EB"), colors.white]),
        ("LINEBELOW", (0, -1), (-1, -1), 1, colors.HexColor("#EA580C")),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#D1D5DB")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(
        "Billing uses enrollment date. Collection uses payment date. "
        "Outstanding is the current unpaid balance, not historical month-end dues. "
        "Cancelled collections are included in total collection and disclosed separately.",
        styles["Normal"],
    ))

    doc.build(elements)

    response = HttpResponse(
        output.getvalue(),
        content_type="application/pdf",
    )
    response["Content-Disposition"] = (
        'attachment; filename="MCTI_Course_Business_Report.pdf"'
    )
    return response


# MCTI V3 SECURE DOWNLOAD VIEWS
from datetime import date
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .management_course_analytics_v3 import course_business_report
from .models import Course


def _report_from_request(request):
    branch = request.GET.get("branch", "all")
    allowed = {
        "all", "kharghar", "panvel", "koperkhairane",
        "kamothe", "ghansoli", "nerul"
    }
    if branch not in allowed:
        branch = "all"

    raw_course = request.GET.get("course", "")
    course_id = None
    if raw_course.isdigit():
        candidate = int(raw_course)
        if Course.objects.filter(pk=candidate).exists():
            course_id = candidate

    def parse_date(value):
        try:
            return date.fromisoformat(value) if value else None
        except ValueError:
            return None

    start_date = parse_date(request.GET.get("start_date", ""))
    end_date = parse_date(request.GET.get("end_date", ""))

    if start_date and end_date and start_date > end_date:
        start_date, end_date = end_date, start_date

    filters = {
        "branch": branch,
        "course": str(course_id or ""),
        "start_date": start_date.isoformat() if start_date else "",
        "end_date": end_date.isoformat() if end_date else "",
    }

    report = course_business_report(
        branch=branch,
        course_id=course_id,
        start_date=start_date,
        end_date=end_date,
    )
    return report, filters


@login_required(login_url="staff_login")
def download_course_business_pdf(request):
    if not request.user.is_active or not request.user.is_superuser:
        raise PermissionDenied
    report, filters = _report_from_request(request)
    return export_pdf(report, filters)


@login_required(login_url="staff_login")
def download_course_business_excel(request):
    if not request.user.is_active or not request.user.is_superuser:
        raise PermissionDenied
    report, filters = _report_from_request(request)
    return export_excel(report, filters)
