from exam_preparation.models import SSCResource

OFFICIAL_QUESTION_PAPER_URL = "https://www.mahahsscboard.in/en/questionPaper"

subjects = [
    ("maths_1", "Mathematics Part 1"),
    ("maths_2", "Mathematics Part 2"),
    ("science_1", "Science & Technology Part 1"),
    ("science_2", "Science & Technology Part 2"),
    ("english", "English"),
    ("marathi", "Marathi"),
    ("history", "History & Political Science"),
    ("geography", "Geography"),
]

mediums = [
    ("english", "English"),
    ("marathi", "Marathi"),
    ("semi_english", "Semi-English"),
]

created = 0
updated = 0

for medium, medium_name in mediums:
    for subject, subject_name in subjects:

        obj, was_created = SSCResource.objects.update_or_create(
            subject=subject,
            medium=medium,
            resource_type="sample_paper",
            source_name="Maharashtra State Board of Secondary & Higher Secondary Education",
            defaults={
                "title": f"{subject_name} – Official Maharashtra Board Question Paper Resources",
                "year": None,
                "source_url": OFFICIAL_QUESTION_PAPER_URL,
                "is_official_source": True,
                "is_active": True,
            },
        )

        if was_created:
            created += 1
        else:
            updated += 1

print("====================================")
print("SSC OFFICIAL RESOURCES SEEDED")
print("Created:", created)
print("Updated:", updated)
print("Total expected:", len(subjects) * len(mediums))
print("====================================")
