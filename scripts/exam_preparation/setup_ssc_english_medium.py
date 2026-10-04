from assessments.models import Assessment

SUBJECTS = [
    (
        "ssc-english-medium-mathematics-part-1-practice",
        "SSC English Medium – Mathematics Part I Practice",
    ),
    (
        "ssc-english-medium-mathematics-part-2-practice",
        "SSC English Medium – Mathematics Part II Practice",
    ),
    (
        "ssc-english-medium-science-technology-part-1-practice",
        "SSC English Medium – Science & Technology Part I Practice",
    ),
    (
        "ssc-english-medium-science-technology-part-2-practice",
        "SSC English Medium – Science & Technology Part II Practice",
    ),
    (
        "ssc-english-medium-social-science-paper-1-practice",
        "SSC English Medium – History & Political Science Practice",
    ),
    (
        "ssc-english-medium-geography-paper-2-practice",
        "SSC English Medium – Geography Practice",
    ),
]

print("=" * 72)
print("SSC ENGLISH MEDIUM ARCHITECTURE")
print("=" * 72)

for slug, title in SUBJECTS:
    a, created = Assessment.objects.update_or_create(
        slug=slug,
        defaults={
            "title": title,
            "assessment_type": "exam_preparation",
            "description": (
                "English-medium SSC practice assessment. "
                "Question bank will be populated from the existing "
                "MCTI Board-based practice material in English."
            ),
            "total_questions": 25,
            "passing_score": 0,
            "duration_minutes": 25,
            "is_active": True,
            "certificate_enabled": False,
            "lead_capture_enabled": False,
        },
    )

    print(
        "CREATED" if created else "READY",
        a.id,
        a.slug,
        "questions=",
        a.questions.filter(is_active=True).count(),
    )

# Existing English First Language assessment is shared.
english = Assessment.objects.filter(
    slug="ssc-english-first-language-practice"
).first()

print("-" * 72)
print(
    "ENGLISH FIRST LANGUAGE:",
    english.id if english else "NOT FOUND",
    english.slug if english else ""
)
print("=" * 72)
