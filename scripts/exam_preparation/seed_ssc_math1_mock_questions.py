from assessments.models import Assessment, AssessmentQuestion, AssessmentOption

assessment = Assessment.objects.get(
    slug="ssc-mathematics-part-1-mock-1"
)

QUESTIONS = [
    # LINEAR EQUATIONS
    ("Linear Equations", "If x + y = 7 and x - y = 1, what is x?", ["2", "3", "4", "5"], "4"),
    ("Linear Equations", "If 2x + y = 9 and x + y = 5, what is x?", ["2", "3", "4", "5"], "4"),
    ("Linear Equations", "Which ordered pair satisfies x + y = 6?", ["(1,2)", "(2,4)", "(3,4)", "(4,4)"], "(2,4)"),
    ("Linear Equations", "The graph of x = 3 is a line parallel to which axis?", ["X-axis", "Y-axis", "Both axes", "Neither axis"], "Y-axis"),
    ("Linear Equations", "If 3x + 2y = 12 and x = 2, what is y?", ["1", "2", "3", "4"], "3"),

    # QUADRATIC EQUATIONS
    ("Quadratic Equations", "Which of the following is a quadratic equation?", ["x + 5 = 0", "x² + 3x + 2 = 0", "x³ = 8", "2x - 7 = 0"], "x² + 3x + 2 = 0"),
    ("Quadratic Equations", "What are the roots of x² - 5x + 6 = 0?", ["1, 6", "2, 3", "-2, -3", "3, 4"], "2, 3"),
    ("Quadratic Equations", "For ax² + bx + c = 0, the discriminant is:", ["b² + 4ac", "b² - 4ac", "4ac - b²", "a² - 4bc"], "b² - 4ac"),
    ("Quadratic Equations", "If the discriminant is zero, the roots are:", ["Real and equal", "Real and unequal", "Not real", "Always zero"], "Real and equal"),
    ("Quadratic Equations", "The product of roots of x² - 7x + 10 = 0 is:", ["5", "7", "10", "17"], "10"),

    # ARITHMETIC PROGRESSION
    ("Arithmetic Progression", "What is the common difference of 3, 7, 11, 15, ...?", ["2", "3", "4", "5"], "4"),
    ("Arithmetic Progression", "What is the next term of 5, 10, 15, 20, ...?", ["22", "24", "25", "30"], "25"),
    ("Arithmetic Progression", "Which formula gives the nth term of an AP?", ["a + nd", "a + (n-1)d", "an + d", "a(n-d)"], "a + (n-1)d"),
    ("Arithmetic Progression", "Find the 5th term of the AP 2, 5, 8, 11, ...", ["11", "12", "14", "17"], "14"),
    ("Arithmetic Progression", "If a = 4 and d = 3, what is the 10th term?", ["27", "30", "31", "34"], "31"),

    # FINANCIAL PLANNING
    ("Financial Planning", "A product costs ₹1,000 before 18% GST. What is the GST amount?", ["₹18", "₹80", "₹180", "₹1,180"], "₹180"),
    ("Financial Planning", "If marked price is ₹2,000 and discount is 10%, what is the discount?", ["₹100", "₹200", "₹250", "₹400"], "₹200"),
    ("Financial Planning", "After a 20% discount on ₹1,500, the selling price is:", ["₹1,000", "₹1,100", "₹1,200", "₹1,300"], "₹1,200"),
    ("Financial Planning", "Simple interest on ₹5,000 at 10% per annum for 2 years is:", ["₹500", "₹1,000", "₹1,500", "₹2,000"], "₹1,000"),
    ("Financial Planning", "If taxable value is ₹2,500 and GST is 12%, total amount is:", ["₹2,620", "₹2,700", "₹2,800", "₹3,000"], "₹2,800"),

    # PROBABILITY / STATISTICS
    ("Probability & Statistics", "Probability of getting a head when a fair coin is tossed once is:", ["0", "1/4", "1/2", "1"], "1/2"),
    ("Probability & Statistics", "Probability of getting 6 on a fair die is:", ["1/2", "1/3", "1/6", "1/12"], "1/6"),
    ("Probability & Statistics", "What is the mean of 2, 4, 6, 8, 10?", ["5", "6", "7", "8"], "6"),
    ("Probability & Statistics", "What is the median of 3, 5, 7, 9, 11?", ["5", "6", "7", "9"], "7"),
    ("Probability & Statistics", "The probability of an impossible event is:", ["0", "1/2", "1", "2"], "0"),
]

if len(QUESTIONS) != 25:
    raise RuntimeError("Exactly 25 questions are required.")

for order, (category, text, options, correct) in enumerate(QUESTIONS, start=1):

    question, _ = AssessmentQuestion.objects.update_or_create(
        assessment=assessment,
        order=order,
        defaults={
            "question_text": text,
            "category": category,
            "marks": 1,
            "is_active": True,
        },
    )

    # Rebuild options only for this question.
    question.options.all().delete()

    for option_order, option_text in enumerate(options, start=1):
        AssessmentOption.objects.create(
            question=question,
            option_text=option_text,
            is_correct=(option_text == correct),
            order=option_order,
        )

    if question.options.filter(is_correct=True).count() != 1:
        raise RuntimeError(
            f"Question {order} does not have exactly one correct option."
        )

print("================================")
print("SSC MATHS PART 1 MOCK SEEDED")
print("Questions:", assessment.questions.filter(is_active=True).count())
print("Options:", AssessmentOption.objects.filter(question__assessment=assessment).count())
print("Correct options:", AssessmentOption.objects.filter(
    question__assessment=assessment,
    is_correct=True
).count())
print("================================")
