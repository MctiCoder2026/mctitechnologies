from assessments.models import Assessment, AssessmentQuestion, AssessmentOption

ASSESSMENT_SLUG = "ssc-marathi-mathematics-part-1-practice"

SOURCE_NAME = "Maharashtra SSC Board – Mathematics Part 1 (Marathi)"
SOURCE_REFERENCE = "2024 III 13-1100 / N 620"
BOARD_YEAR = 2024

assessment = Assessment.objects.get(slug=ASSESSMENT_SLUG)

print("Assessment:", assessment.title)
print("Assessment ID:", assessment.id)
print("Source:", SOURCE_NAME)
print("Board Year:", BOARD_YEAR)
print("Reference:", SOURCE_REFERENCE)
print("Existing questions:", assessment.questions.count())

# Verified questions from the uploaded 2024 Board paper
# will be added below in the next step.

