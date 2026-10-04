from assessments.models import Assessment

assessment, created = Assessment.objects.update_or_create(
    slug="ssc-mathematics-part-1-mock-1",
    defaults={
        "title": "SSC Mathematics Part 1 – Mock Test 1",
        "assessment_type": "exam_preparation",
        "description": (
            "Free MCTI-created practice mock test for Maharashtra SSC "
            "Mathematics Part 1 preparation."
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
print("TYPE:", assessment.assessment_type)
print("QUESTIONS:", assessment.total_questions)
print("DURATION:", assessment.duration_minutes)
