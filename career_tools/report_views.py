import io
import re

import qrcode
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core import signing
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .models import CareerProfile
from .services import get_course_suggestions


ORANGE = colors.HexColor("#F36A21")
BLACK = colors.HexColor("#111111")
DARK_GREY = colors.HexColor("#555555")
LIGHT_GREY = colors.HexColor("#F3F3F3")
BORDER = colors.HexColor("#E4E4E4")


def clean_text(value):
    text = str(value or "")
    replacements = {
        "–": "-",
        "—": "-",
        "₹": "Rs.",
        "’": "'",
        "“": '"',
        "”": '"',
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return escape(text)


def proportional_logo(path, width):
    reader = ImageReader(str(path))
    original_width, original_height = reader.getSize()

    height = (
        width
        * float(original_height)
        / float(original_width)
    )

    return Image(
        str(path),
        width=width,
        height=height,
    )


def build_aptitude_qr(aptitude_url):
    qr = qrcode.QRCode(
        version=1,
        box_size=8,
        border=2,
    )
    qr.add_data(aptitude_url)
    qr.make(fit=True)

    image = qr.make_image(
        fill_color="#111111",
        back_color="white",
    )

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    return Image(
        buffer,
        width=1.38 * inch,
        height=1.38 * inch,
    )


@staff_member_required
def career_report_pdf(request, profile_id):
    profile = (
        CareerProfile.objects
        .select_related("enquiry", "student")
        .filter(id=profile_id)
        .first()
    )

    if profile is None:
        return redirect(
            "career_tools:quick_career_enquiry"
        )

    attempt = (
        profile.aptitude_attempts
        .filter(status="completed")
        .order_by("-completed_at", "-id")
        .first()
    )

    recommendation = None

    if attempt:
        recommendation = (
            profile.career_recommendations
            .filter(aptitude_attempt=attempt)
            .prefetch_related("items")
            .order_by("-created_at", "-id")
            .first()
        )

    suggestions = get_course_suggestions(profile)

    token = signing.Signer(
        salt="mcti-career-aptitude"
    ).sign(str(profile.id))

    aptitude_url = request.build_absolute_uri(
        reverse(
            "career_tools:aptitude_access",
            kwargs={"token": token},
        )
    )

    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=32,
        bottomMargin=32,
        title=(
            f"MCTI Career Report - "
            f"{profile.full_name}"
        ),
        author="MCTI Technologies",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "MCTITitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=BLACK,
        alignment=0,
        spaceAfter=4,
    )

    orange_style = ParagraphStyle(
        "MCTIOrange",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=ORANGE,
        spaceAfter=4,
    )

    heading_style = ParagraphStyle(
        "MCTIHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=BLACK,
        spaceBefore=12,
        spaceAfter=8,
    )

    body_style = ParagraphStyle(
        "MCTIBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=DARK_GREY,
    )

    small_style = ParagraphStyle(
        "MCTISmall",
        parent=body_style,
        fontSize=8,
        leading=11,
    )

    story = []

    logo_path = (
        settings.BASE_DIR
        / "lms"
        / "static"
        / "lms"
        / "certificate"
        / "mcti_technologies_logo.png"
    )

    report_type = (
        "Detailed Career Recommendation Report"
        if attempt
        else "Initial Career Recommendation Report"
    )

    report_id = (
        f"MCTI-CR-{profile.id:06d}"
        + (
            f"-A{attempt.id:05d}"
            if attempt
            else "-INITIAL"
        )
    )

    header_text = [
        Paragraph(
            clean_text(report_type),
            title_style,
        ),
        Paragraph(
            f"Report ID: {clean_text(report_id)}",
            small_style,
        ),
    ]

    header_right = Table(
        [[item] for item in header_text],
        colWidths=[5.4 * inch],
    )
    header_right.setStyle(
        TableStyle(
            [
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]
        )
    )

    if logo_path.exists():
        logo = proportional_logo(
            logo_path,
            1.05 * inch,
        )

        header = Table(
            [[logo, header_right]],
            colWidths=[
                1.25 * inch,
                5.45 * inch,
            ],
        )
    else:
        header = Table(
            [[header_right]],
            colWidths=[6.7 * inch],
        )

    header.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 1, BORDER),
                ("LINEBELOW", (0, 0), (-1, -1), 4, ORANGE),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )

    story.append(header)
    story.append(Spacer(1, 14))

    story.append(
        Paragraph(
            "STUDENT CAREER PROFILE",
            heading_style,
        )
    )

    profile_data = [
        [
            Paragraph(
                "<b>Name</b><br/>"
                + clean_text(profile.full_name),
                body_style,
            ),
            Paragraph(
                "<b>Mobile</b><br/>"
                + clean_text(profile.mobile),
                body_style,
            ),
        ],
        [
            Paragraph(
                "<b>Qualification</b><br/>"
                + clean_text(
                    profile.highest_qualification
                ),
                body_style,
            ),
            Paragraph(
                "<b>Stream</b><br/>"
                + clean_text(profile.stream),
                body_style,
            ),
        ],
        [
            Paragraph(
                "<b>Current Status</b><br/>"
                + clean_text(profile.current_status),
                body_style,
            ),
            Paragraph(
                "<b>Preferred Branch</b><br/>"
                + clean_text(profile.preferred_branch),
                body_style,
            ),
        ],
        [
            Paragraph(
                "<b>Career Interest</b><br/>"
                + clean_text(
                    profile.career_interest
                    or "Not specified"
                ),
                body_style,
            ),
            Paragraph(
                "<b>Report Status</b><br/>"
                + (
                    "Aptitude Completed"
                    if attempt
                    else "Aptitude Pending"
                ),
                body_style,
            ),
        ],
    ]

    profile_table = Table(
        profile_data,
        colWidths=[3.35 * inch, 3.35 * inch],
    )
    profile_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GREY),
                ("BOX", (0, 0), (-1, -1), .7, BORDER),
                ("INNERGRID", (0, 0), (-1, -1), .5, BORDER),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ]
        )
    )
    story.append(profile_table)

    if attempt:
        story.append(
            Paragraph(
                "APTITUDE PERFORMANCE",
                heading_style,
            )
        )

        score_data = [
            [
                Paragraph("<b>Overall</b>", body_style),
                Paragraph("<b>Numerical</b>", body_style),
                Paragraph("<b>Logical</b>", body_style),
                Paragraph("<b>Verbal</b>", body_style),
                Paragraph("<b>Computer</b>", body_style),
                Paragraph("<b>Career</b>", body_style),
            ],
            [
                f"{attempt.score_percentage}%",
                str(attempt.numerical_score),
                str(attempt.logical_score),
                str(attempt.verbal_score),
                str(attempt.computer_score),
                str(attempt.career_score),
            ],
        ]

        score_table = Table(
            score_data,
            colWidths=[
                1.12 * inch,
                1.12 * inch,
                1.12 * inch,
                1.12 * inch,
                1.12 * inch,
                1.10 * inch,
            ],
        )
        score_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), BLACK),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("BACKGROUND", (0, 1), (-1, 1), colors.white),
                    ("TEXTCOLOR", (0, 1), (-1, 1), BLACK),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("BOX", (0, 0), (-1, -1), .7, BORDER),
                    ("INNERGRID", (0, 0), (-1, -1), .5, BORDER),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        story.append(score_table)

    if recommendation:
        story.append(
            Paragraph(
                "CAREER GUIDANCE SUMMARY",
                heading_style,
            )
        )

        story.append(
            Paragraph(
                clean_text(
                    recommendation.overall_summary
                ),
                body_style,
            )
        )
        story.append(Spacer(1, 8))

        strength_table = Table(
            [
                [
                    Paragraph(
                        "<b>Strongest Area</b><br/>"
                        + clean_text(
                            recommendation.strongest_area
                        ),
                        body_style,
                    ),
                    Paragraph(
                        "<b>Improvement Area</b><br/>"
                        + clean_text(
                            recommendation.improvement_area
                        ),
                        body_style,
                    ),
                ]
            ],
            colWidths=[3.35 * inch, 3.35 * inch],
        )
        strength_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#FFF2EA")),
                    ("BACKGROUND", (1, 0), (1, 0), LIGHT_GREY),
                    ("BOX", (0, 0), (-1, -1), .7, BORDER),
                    ("INNERGRID", (0, 0), (-1, -1), .5, BORDER),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
                ]
            )
        )
        story.append(strength_table)

        story.append(
            Paragraph(
                "TOP CAREER MATCHES",
                heading_style,
            )
        )

        for item in recommendation.items.all():
            card = Table(
                [
                    [
                        Paragraph(
                            f"<b>#{item.rank} "
                            f"{clean_text(item.career_title)}</b>"
                            f"<br/>Match: {item.match_percentage}%",
                            body_style,
                        ),
                        Paragraph(
                            "<b>Recommended Course</b><br/>"
                            + clean_text(
                                item.recommended_course
                                or "Counsellor review"
                            ),
                            body_style,
                        ),
                    ],
                    [
                        Paragraph(
                            "<b>Why this matches</b><br/>"
                            + clean_text(item.reason),
                            body_style,
                        ),
                        Paragraph(
                            "<b>Skills to Improve</b><br/>"
                            + clean_text(
                                item.skills_to_improve
                            ),
                            body_style,
                        ),
                    ],
                    [
                        Paragraph(
                            "<b>Next Step</b><br/>"
                            + clean_text(item.next_step),
                            body_style,
                        ),
                        "",
                    ],
                ],
                colWidths=[3.35 * inch, 3.35 * inch],
            )
            card.setStyle(
                TableStyle(
                    [
                        ("SPAN", (0, 2), (1, 2)),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#FFF2EA")),
                        ("BOX", (0, 0), (-1, -1), .8, BORDER),
                        ("INNERGRID", (0, 0), (-1, -2), .5, BORDER),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 10),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                        ("TOPPADDING", (0, 0), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ]
                )
            )
            story.append(
                KeepTogether(
                    [
                        card,
                        Spacer(1, 9),
                    ]
                )
            )

    else:
        story.append(
            Paragraph(
                "INITIAL COURSE RECOMMENDATIONS",
                heading_style,
            )
        )

        for index, item in enumerate(
            suggestions,
            start=1,
        ):
            course = item["course"]

            course_card = Table(
                [
                    [
                        Paragraph(
                            f"<b>{index}. "
                            f"{clean_text(course.title)}</b>",
                            body_style,
                        ),
                        Paragraph(
                            "<b>Duration</b><br/>"
                            + clean_text(
                                course.duration or "Ask counsellor"
                            ),
                            body_style,
                        ),
                    ],
                    [
                        Paragraph(
                            clean_text(item["reason"]),
                            body_style,
                        ),
                        "",
                    ],
                ],
                colWidths=[5.15 * inch, 1.55 * inch],
            )
            course_card.setStyle(
                TableStyle(
                    [
                        ("SPAN", (0, 1), (1, 1)),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#FFF2EA")),
                        ("BOX", (0, 0), (-1, -1), .7, BORDER),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 10),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                        ("TOPPADDING", (0, 0), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ]
                )
            )
            story.append(course_card)
            story.append(Spacer(1, 8))

    story.append(
        Paragraph(
            "NEXT STEP",
            heading_style,
        )
    )

    if attempt:
        cta_data = [
            [
                Paragraph(
                    "<b>Your Detailed Career Report is Ready</b>"
                    "<br/><br/>"
                    "Contact an MCTI career counsellor to discuss "
                    "your aptitude results, career matches and the "
                    "right learning roadmap."
                    "<br/><br/>"
                    "<b>Call:</b> +91 8655556219"
                    "<br/><b>Email:</b> "
                    "info@mctitechnologies.com",
                    body_style,
                )
            ]
        ]
        cta_widths = [6.7 * inch]

    else:
        qr_image = build_aptitude_qr(aptitude_url)

        cta_data = [
            [
                qr_image,
                Paragraph(
                    "<b>Scan for MCTI Aptitude Test</b>"
                    "<br/><br/>"
                    "Scan this personal QR to complete the MCTI "
                    "Aptitude Test from home or anywhere. After "
                    "completion, the same report will include "
                    "detailed aptitude scores and Top 3 career "
                    "matches."
                    "<br/><br/>"
                    "<b>Call:</b> +91 8655556219"
                    "<br/><b>Email:</b> "
                    "info@mctitechnologies.com",
                    body_style,
                ),
            ]
        ]
        cta_widths = [1.7 * inch, 5 * inch]

    cta_table = Table(
        cta_data,
        colWidths=cta_widths,
    )
    cta_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GREY),
                ("BOX", (0, 0), (-1, -1), 1, ORANGE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    story.append(cta_table)
    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            "MCTI Technologies | Education | IT Solutions | AI | SaaS"
            "<br/>An Initiative by Maharashtra Computer Training Institute"
            "<br/>Kharghar | Panvel | Koperkhairane | Kamothe | "
            "Ghansoli | Nerul",
            ParagraphStyle(
                "Footer",
                parent=small_style,
                alignment=1,
                textColor=DARK_GREY,
            ),
        )
    )

    document.build(story)

    buffer.seek(0)

    filename_name = re.sub(
        r"[^A-Za-z0-9]+",
        "-",
        profile.full_name,
    ).strip("-") or "student"

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/pdf",
    )
    response["Content-Disposition"] = (
        f'attachment; filename="MCTI-Career-Report-'
        f'{filename_name}.pdf"'
    )
    return response
