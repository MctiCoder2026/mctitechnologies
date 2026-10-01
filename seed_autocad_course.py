"""
MCTI LMS - AutoCAD Course Seeder
Course ID: 37
Target: 10 Modules / 50 Topics / 250 MCQs

SAFETY:
- Only operates on AutoCAD Course ID 37.
- Refuses to run if course identity does not match.
- Refuses to overwrite existing AutoCAD LMS content.
"""

from core.models import Course
from lms.models import LMSModule, LMSTopic, QuizQuestion

COURSE_ID = 37
EXPECTED_SLUG = "autocad"

course = Course.objects.get(id=COURSE_ID)

if course.slug != EXPECTED_SLUG:
    raise RuntimeError(
        f"Safety stop: Course {COURSE_ID} is '{course.slug}', "
        f"expected '{EXPECTED_SLUG}'."
    )

module_count = LMSModule.objects.filter(course=course).count()
topic_count = LMSTopic.objects.filter(module__course=course).count()
quiz_count = QuizQuestion.objects.filter(
    topic__module__course=course
).count()

print("===== AUTOCAD SEED SAFETY CHECK =====")
print("Course:", course.id, "|", course.title)
print("Existing Modules:", module_count)
print("Existing Topics:", topic_count)
print("Existing MCQs:", quiz_count)

if module_count or topic_count or quiz_count:
    raise RuntimeError(
        "Safety stop: AutoCAD already contains LMS content. "
        "Nothing was changed."
    )

print("\nREADY FOR AUTOCAD CONTENT SEED ✅")
print("Target: 10 Modules | 50 Topics | 250 MCQs")
print("No database changes made by this safety script.")
