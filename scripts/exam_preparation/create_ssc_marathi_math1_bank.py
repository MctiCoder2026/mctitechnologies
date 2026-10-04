from assessments.models import Assessment

assessment, created = Assessment.objects.update_or_create(
    slug="ssc-marathi-mathematics-part-1-practice",
    defaults={
        "title": "SSC Marathi Medium – Mathematics Part 1 Practice",
        "assessment_type": "exam_preparation",
        "description": (
            "SSC Marathi Medium Mathematics Part 1 practice question bank. "
            "Questions with Board references must be verified from the "
            "official Maharashtra Board source."
        ),
        "total_questions": 25,
        "passing_score": 0,
        "duration_minutes": 25,
        "is_active": True,
        "certificate_enabled": False,
        "lead_capture_enabled": False,
    },
)

print("ASSESSMENT ID:", assessment.id)
print("CREATED:", created)
print("TITLE:", assessment.title)
print("SLUG:", assessment.slug)
print("CURRENT BANK QUESTIONS:", assessment.questions.count())
