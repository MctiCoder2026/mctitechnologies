from django.db import transaction
from assessments.models import Assessment, AssessmentQuestion, AssessmentOption

ASSESSMENT_SLUG = "ssc-marathi-mathematics-part-1-practice"

SOURCES = {
    2024: {
        "name": "Maharashtra SSC Board – Mathematics Part 1 (Marathi)",
        "reference": "2024 III 13-1100 / N 620",
    },
    2025: {
        "name": "Maharashtra SSC Board – Mathematics Part 1 (Marathi)",
        "reference": "2025 III 05-1100 / N 820",
    },
    2026: {
        "name": "Maharashtra SSC Board – Mathematics Part 1 (Marathi)",
        "reference": "2026 III 06-1100 / N 920",
    },
}

assessment = Assessment.objects.get(slug=ASSESSMENT_SLUG)

print("Assessment:", assessment.title)
print("Assessment ID:", assessment.id)

for year, source in SOURCES.items():
    print(year, "=>", source["reference"])

print("Current questions:", assessment.questions.count())
print("3-year source configuration ready.")

def add_question(
    *,
    year,
    question_text,
    category,
    options,
    correct_index,
    origin="board_based",
    marks=1,
):
    source = SOURCES[year]

    question, created = AssessmentQuestion.objects.update_or_create(
        assessment=assessment,
        question_text=question_text,
        board_year=year,
        defaults={
            "category": category,
            "order": AssessmentQuestion.objects.filter(assessment=assessment).count() + 1,
            "marks": marks,
            "is_active": True,
            "question_origin": origin,
            "source_name": source["name"],
            "source_reference": source["reference"],
        },
    )

    AssessmentOption.objects.filter(question=question).delete()

    for index, option_text in enumerate(options):
        AssessmentOption.objects.create(
            question=question,
            option_text=str(option_text),
            is_correct=(index == correct_index),
            order=index + 1,
        )

    return created


print("Question import helper ready.")

# ============================================================
# 2024 – EXACT BOARD MCQs – Q.1(A)
# Source: 2024 III 13-1100 / N 620
# ============================================================

created_count = 0

created_count += add_question(
    year=2024,
    question_text="kx² − 7x + 12 = 0 या वर्गसमीकरणाचे एक मूळ 3 आहे, तर k = ............",
    category="Quadratic Equations",
    options=["1", "−1", "3", "−3"],
    correct_index=0,
    origin="board_verified",
)

created_count += add_question(
    year=2024,
    question_text="x + 2y = 4 या आलेख काढण्यासाठी y = 1 असताना x ची किंमत किती?",
    category="Linear Equations in Two Variables",
    options=["1", "2", "−2", "6"],
    correct_index=1,
    origin="board_verified",
)

created_count += add_question(
    year=2024,
    question_text="दिलेल्या अंकगणिती श्रेढीचे t₇ = 4 व d = −4, तर a = ............",
    category="Arithmetic Progression",
    options=["6", "7", "20", "28"],
    correct_index=3,
    origin="board_verified",
)

created_count += add_question(
    year=2024,
    question_text="GSTIN मध्ये एकूण किती अंकाक्षरे असतात?",
    category="Financial Planning",
    options=["9", "10", "15", "16"],
    correct_index=2,
    origin="board_verified",
)

print("2024 newly created:", created_count)
print("TOTAL BANK QUESTIONS:", assessment.questions.count())

# ============================================================
# 2025 – EXACT BOARD MCQs – Q.1(A)
# Source: 2025 III 05-1100 / N 820
# ============================================================

created_2025 = 0

created_2025 += add_question(
    year=2025,
    question_text="|1  2; 3  4| या निर्धारकाची कोटी लिहा.",
    category="Linear Equations in Two Variables",
    options=["1", "2", "3", "4"],
    correct_index=1,
    origin="board_verified",
)

created_2025 += add_question(
    year=2025,
    question_text="खालीलपैकी कोणते समीकरण वर्गसमीकरण आहे?",
    category="Quadratic Equations",
    options=[
        "5/x − 3 = x²",
        "x(x + 5) = 2",
        "n − 1 = 2n",
        "(1/x²)(x + 2) = x",
    ],
    correct_index=1,
    origin="board_verified",
)

created_2025 += add_question(
    year=2025,
    question_text="खालील अंकगणिती श्रेढीचा साधारण फरक काढा : 4, 4, 4, ...",
    category="Arithmetic Progression",
    options=["1", "8", "4", "0"],
    correct_index=3,
    origin="board_verified",
)

created_2025 += add_question(
    year=2025,
    question_text="खालील पर्यायांपैकी कोणती संभाव्यता असू शकणार नाही?",
    category="Probability",
    options=["2/3", "15/10", "15%", "0.7"],
    correct_index=1,
    origin="board_verified",
)

print("2025 newly created:", created_2025)
print("TOTAL BANK QUESTIONS:", assessment.questions.count())

# ============================================================
# 2026 – EXACT BOARD MCQs – Q.1(A)
# Source: 2026 III 06-1100 / N 920
# ============================================================

created_2026 = 0

created_2026 += add_question(
    year=2026,
    question_text="जीवनावश्यक वस्तूंवरील वस्तू व सेवा कराचा दर ............ आहे.",
    category="Financial Planning",
    options=["5%", "12%", "0%", "18%"],
    correct_index=2,
    origin="board_verified",
)

created_2026 += add_question(
    year=2026,
    question_text="खालीलपैकी कोणते समीकरण वर्गसमीकरण नाही?",
    category="Quadratic Equations",
    options=[
        "x² + 4x = 11 + x²",
        "x² = 4x",
        "5x² = 90",
        "2x − x² = x² + 5",
    ],
    correct_index=0,
    origin="board_verified",
)

created_2026 += add_question(
    year=2026,
    question_text="4x + 5y = 19 या आलेख काढण्यासाठी x = 1 असताना y ची किंमत किती?",
    category="Linear Equations in Two Variables",
    options=["4", "3", "2", "−3"],
    correct_index=1,
    origin="board_verified",
)

created_2026 += add_question(
    year=2026,
    question_text="3 च्या पहिल्या पाच पटींची बेरीज ............ आहे.",
    category="Arithmetic Progression",
    options=["45", "55", "15", "75"],
    correct_index=0,
    origin="board_verified",
)

print("2026 newly created:", created_2026)
print("TOTAL BANK QUESTIONS:", assessment.questions.count())

# ============================================================
# 2024 – BOARD-BASED PRACTICE MCQs
# Derived from clearly readable questions in the 2024 paper
# ============================================================

created_2024_based = 0

created_2024_based += add_question(
    year=2024,
    question_text="17x + 15y = 11 आणि 15x + 17y = 21 असल्यास x − y ची किंमत किती?",
    category="Linear Equations in Two Variables",
    options=["−5", "5", "−10", "10"],
    correct_index=0,
    origin="board_based",
)

created_2024_based += add_question(
    year=2024,
    question_text="tₙ = 3n − 2 या अंकगणिती श्रेढीचे पहिले पद कोणते?",
    category="Arithmetic Progression",
    options=["1", "2", "3", "−2"],
    correct_index=0,
    origin="board_based",
)

created_2024_based += add_question(
    year=2024,
    question_text="(0, 2) हा बिंदू 2x + 3y = k या समीकरणाच्या आलेखावर असल्यास k ची किंमत किती?",
    category="Linear Equations in Two Variables",
    options=["2", "3", "6", "8"],
    correct_index=2,
    origin="board_based",
)

created_2024_based += add_question(
    year=2024,
    question_text="एका वर्गसमीकरणाची मुळे 2 आणि 5 असल्यास खालीलपैकी योग्य वर्गसमीकरण कोणते?",
    category="Quadratic Equations",
    options=[
        "x² − 7x + 10 = 0",
        "x² + 7x + 10 = 0",
        "x² − 3x + 10 = 0",
        "x² + 3x − 10 = 0",
    ],
    correct_index=0,
    origin="board_based",
)

created_2024_based += add_question(
    year=2024,
    question_text="x² + x − 20 = 0 या वर्गसमीकरणाची मुळे कोणती?",
    category="Quadratic Equations",
    options=[
        "4 आणि −5",
        "5 आणि −4",
        "4 आणि 5",
        "−4 आणि −5",
    ],
    correct_index=0,
    origin="board_based",
)

print("2024 board-based newly created:", created_2024_based)
print("TOTAL BANK QUESTIONS:", assessment.questions.count())
