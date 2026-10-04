from assessments.models import Assessment, AssessmentQuestion, AssessmentOption

SLUG = "ssc-marathi-mathematics-part-1-practice"

assessment = Assessment.objects.get(slug=SLUG)

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


def add(year, text, category, options, correct):
    source = SOURCES[year]

    q, created = AssessmentQuestion.objects.get_or_create(
        assessment=assessment,
        question_text=text,
        board_year=year,
        defaults={
            "category": category,
            "order": assessment.questions.count() + 1,
            "marks": 1,
            "is_active": True,
            "question_origin": "board_based",
            "source_name": source["name"],
            "source_reference": source["reference"],
        }
    )

    # Existing question ko destructive way se touch nahi karna.
    if not created:
        return False

    AssessmentOption.objects.bulk_create([
        AssessmentOption(
            question=q,
            option_text=str(option),
            is_correct=(i == correct),
            order=i + 1,
        )
        for i, option in enumerate(options)
    ])

    return True


QUESTIONS = [

    # ========================================================
    # 2024
    # ========================================================

    (
        2024,
        "3x − 4y = 10 आणि 4x + 3y = 5 असल्यास x ची किंमत किती?",
        "Linear Equations in Two Variables",
        ["1", "2", "3", "4"],
        1,
    ),

    (
        2024,
        "3x − 4y = 10 आणि 4x + 3y = 5 असल्यास y ची किंमत किती?",
        "Linear Equations in Two Variables",
        ["−1", "1", "2", "−2"],
        0,
    ),

    (
        2024,
        "3m² − m − 10 = 0 या वर्गसमीकरणाचे अवयव कोणते?",
        "Quadratic Equations",
        [
            "(3m + 5)(m − 2)",
            "(3m − 5)(m + 2)",
            "(3m + 2)(m − 5)",
            "(m + 5)(3m − 2)",
        ],
        0,
    ),

    (
        2024,
        "3m² − m − 10 = 0 या समीकरणाची मुळे कोणती?",
        "Quadratic Equations",
        ["2 आणि −5/3", "−2 आणि 5/3", "2 आणि 5/3", "−2 आणि −5/3"],
        0,
    ),

    (
        2024,
        "7, 13, 19, 25, ... या अंकगणिती श्रेढीचा समान फरक किती?",
        "Arithmetic Progression",
        ["4", "5", "6", "7"],
        2,
    ),

    (
        2024,
        "7, 13, 19, 25, ... या अंकगणिती श्रेढीचे पहिले पद किती?",
        "Arithmetic Progression",
        ["6", "7", "13", "19"],
        1,
    ),

    (
        2024,
        "₹2360 या GST सहित किमतीत GST दर 18% असल्यास GST पूर्व किंमत किती?",
        "Financial Planning",
        ["₹1800", "₹1900", "₹2000", "₹2180"],
        2,
    ),

    (
        2024,
        "₹2000 वर 18% GST किती?",
        "Financial Planning",
        ["₹180", "₹360", "₹400", "₹236"],
        1,
    ),

    # ========================================================
    # 2025
    # ========================================================

    (
        2025,
        "2x + y = 7 आणि x + 2y = 11 असल्यास x + y ची किंमत किती?",
        "Linear Equations in Two Variables",
        ["4", "5", "6", "7"],
        2,
    ),

    (
        2025,
        "2x + y = 7 आणि x + 2y = 11 असल्यास x ची किंमत किती?",
        "Linear Equations in Two Variables",
        ["1", "2", "3", "5"],
        0,
    ),

    (
        2025,
        "2x + y = 7 आणि x + 2y = 11 असल्यास y ची किंमत किती?",
        "Linear Equations in Two Variables",
        ["2", "3", "4", "5"],
        3,
    ),

    (
        2025,
        "tₙ = 3n − 4 या अंकगणिती श्रेढीचे पहिले पद किती?",
        "Arithmetic Progression",
        ["−1", "1", "3", "4"],
        0,
    ),

    (
        2025,
        "tₙ = 3n − 4 या अंकगणिती श्रेढीचा समान फरक किती?",
        "Arithmetic Progression",
        ["−4", "1", "3", "4"],
        2,
    ),

    (
        2025,
        "x + y = 3 आणि 3x − 2y = 4 असल्यास x ची किंमत किती?",
        "Linear Equations in Two Variables",
        ["1", "2", "3", "4"],
        1,
    ),

    (
        2025,
        "x + y = 3 आणि 3x − 2y = 4 असल्यास y ची किंमत किती?",
        "Linear Equations in Two Variables",
        ["0", "1", "2", "3"],
        1,
    ),

    (
        2025,
        "m² + 14m + 13 = 0 या वर्गसमीकरणाची मुळे कोणती?",
        "Quadratic Equations",
        [
            "1 आणि 13",
            "−1 आणि −13",
            "1 आणि −13",
            "−1 आणि 13",
        ],
        1,
    ),

    (
        2025,
        "7, 13, 19, 25, ... या अंकगणिती श्रेढीचा समान फरक किती?",
        "Arithmetic Progression",
        ["5", "6", "7", "12"],
        1,
    ),

    (
        2025,
        "4x + 3y = 18 आणि 3x − 2y = 5 असल्यास x ची किंमत किती?",
        "Linear Equations in Two Variables",
        ["1", "2", "3", "4"],
        2,
    ),

    (
        2025,
        "4x + 3y = 18 आणि 3x − 2y = 5 असल्यास y ची किंमत किती?",
        "Linear Equations in Two Variables",
        ["1", "2", "3", "4"],
        1,
    ),

    (
        2025,
        "x² − 2x − 3 = 0 या वर्गसमीकरणाची मुळे कोणती?",
        "Quadratic Equations",
        ["3 आणि −1", "−3 आणि 1", "3 आणि 1", "−3 आणि −1"],
        0,
    ),

    (
        2025,
        "2, 3 आणि 5 या अंकांपासून पुनरावृत्ती न करता दोन अंकी संख्या तयार केल्यास एकूण किती शक्यता आहेत?",
        "Probability",
        ["3", "4", "6", "9"],
        2,
    ),

    # ========================================================
    # 2026
    # ========================================================

    (
        2026,
        "70, 60, 50, 40, ... या अंकगणिती श्रेढीचा समान फरक किती?",
        "Arithmetic Progression",
        ["10", "−10", "20", "−20"],
        1,
    ),

    (
        2026,
        "70, 60, 50, 40, ... या अंकगणिती श्रेढीचे पहिले पद किती?",
        "Arithmetic Progression",
        ["40", "50", "60", "70"],
        3,
    ),

    (
        2026,
        "x + y = 4 आणि 2x − y = 2 असल्यास x ची किंमत किती?",
        "Linear Equations in Two Variables",
        ["1", "2", "3", "4"],
        1,
    ),

    (
        2026,
        "x + y = 4 आणि 2x − y = 2 असल्यास y ची किंमत किती?",
        "Linear Equations in Two Variables",
        ["1", "2", "3", "4"],
        1,
    ),

    (
        2026,
        "x² + x − 20 = 0 या वर्गसमीकरणाची मुळे कोणती?",
        "Quadratic Equations",
        ["4 आणि −5", "5 आणि −4", "4 आणि 5", "−4 आणि −5"],
        0,
    ),

    (
        2026,
        "12, 16, 20, 24, ... या अंकगणिती श्रेढीचा समान फरक किती?",
        "Arithmetic Progression",
        ["2", "4", "6", "8"],
        1,
    ),

    (
        2026,
        "12, 16, 20, 24, ... या अंकगणिती श्रेढीत 24 हे कितवे पद आहे?",
        "Arithmetic Progression",
        ["3 रे", "4 थे", "5 वे", "6 वे"],
        1,
    ),

    (
        2026,
        "एका वस्तूची किंमत ₹50,000 असून 10% सूट दिल्यास सूट किती?",
        "Financial Planning",
        ["₹4,000", "₹5,000", "₹5,500", "₹10,000"],
        1,
    ),

    (
        2026,
        "₹50,000 च्या वस्तूवर 10% सूट दिल्यानंतरची किंमत किती?",
        "Financial Planning",
        ["₹40,000", "₹45,000", "₹46,000", "₹49,000"],
        1,
    ),

    (
        2026,
        "₹45,000 करपात्र किमतीवर GST 18% असल्यास CGST चा दर किती?",
        "Financial Planning",
        ["5%", "9%", "12%", "18%"],
        1,
    ),

    (
        2026,
        "₹45,000 वर 9% CGST किती?",
        "Financial Planning",
        ["₹4,050", "₹4,500", "₹8,100", "₹9,000"],
        0,
    ),

    (
        2026,
        "₹45,000 वर CGST ₹4,050 आणि SGST ₹4,050 असल्यास अंतिम किंमत किती?",
        "Financial Planning",
        ["₹49,050", "₹53,100", "₹54,000", "₹58,100"],
        1,
    ),

    (
        2026,
        "5m² + 2m + k = 0 या समीकरणाचे एक मूळ −7/5 असल्यास k ची किंमत किती?",
        "Quadratic Equations",
        ["−7", "7", "−5", "5"],
        0,
    ),

    (
        2026,
        "नमुना अवकाश S = {1,2,3,4,5,6} आणि घटना A = {2,3,5} असल्यास P(A) किती?",
        "Probability",
        ["1/6", "1/3", "1/2", "2/3"],
        2,
    ),
]


created = 0

for row in QUESTIONS:
    if add(*row):
        created += 1

print("=" * 60)
print("SSC MARATHI MATHEMATICS PART 1 – BULK IMPORT COMPLETE")
print("New questions added:", created)
print("Total questions now:", assessment.questions.count())
print("=" * 60)
