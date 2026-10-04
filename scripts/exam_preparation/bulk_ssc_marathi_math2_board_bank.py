from assessments.models import Assessment, AssessmentQuestion, AssessmentOption

SLUG = "ssc-marathi-mathematics-part-2-practice"

SOURCES = {
    2024: {
        "name": "Maharashtra SSC Board – Mathematics Part 2 Geometry (Marathi)",
        "ref": "2024 III 15-1100 / N 633",
    },
    2025: {
        "name": "Maharashtra SSC Board – Mathematics Part 2 Geometry (Marathi)",
        "ref": "2025 III 07-1100 / N 833",
    },
    2026: {
        "name": "Maharashtra SSC Board – Mathematics Part 2 Geometry (Marathi)",
        "ref": "2026 III 09-1100 / N 933",
    },
}

# text, options, correct_index, category, year, origin
QUESTIONS = [

    # =========================
    # 2024
    # =========================
    (
        "खालीलपैकी कोणत्या तीन संख्या पायथागोरस त्रिकूट तयार करतात?",
        ["1, 5, 10", "3, 4, 5", "2, 2, 2", "5, 5, 2"],
        1, "Pythagoras Theorem", 2024, "board_based"
    ),
    (
        "sin θ × cosec θ याची किंमत किती?",
        ["1", "0", "1/2", "2"],
        0, "Trigonometry", 2024, "board_verified"
    ),
    (
        "दोन समरूप त्रिकोणांच्या संगत बाजूंचे प्रमाण 2 : 3 असल्यास त्यांच्या क्षेत्रफळांचे प्रमाण किती?",
        ["2 : 3", "4 : 9", "3 : 2", "9 : 4"],
        1, "Similarity", 2024, "board_based"
    ),
    (
        "वर्तुळात ∠ABC = 60° असून A आणि C हे वर्तुळावरील बिंदू आहेत. त्याच AC चापाने केंद्रावर तयार होणारा ∠AOC किती?",
        ["30°", "60°", "120°", "180°"],
        2, "Circle", 2024, "board_based"
    ),
    (
        "sin² θ + cos² θ = ?",
        ["0", "1", "2", "sin θ"],
        1, "Trigonometry", 2024, "board_based"
    ),
    (
        "A(2, 3) आणि B(4, 7) या बिंदूंमधील अंतर किती?",
        ["√20", "2√5", "4√5", "5"],
        1, "Coordinate Geometry", 2024, "board_based"
    ),
    (
        "A(1, −3), B(2, −5), C(−4, 7) हे बिंदू एका सरळ रेषेत आहेत का?",
        ["होय", "नाही", "फक्त A व B", "निश्चित करता येत नाही"],
        0, "Coordinate Geometry", 2024, "board_based"
    ),
    (
        "△ABC ~ △LMN. BC = 6 आणि BC/MN = 5/4 असल्यास MN किती?",
        ["4", "4.8", "5", "7.5"],
        1, "Similarity", 2024, "board_based"
    ),
    (
        "समकोनी त्रिकोणात कर्णावर काढलेल्या मध्यिकेची लांबी 9 आहे. कर्णाची लांबी किती?",
        ["9", "12", "18", "27"],
        2, "Pythagoras Theorem", 2024, "board_based"
    ),
    (
        "वर्तुळाबाहेरील P बिंदूपासून PA व PB या स्पर्शिका काढल्या आहेत. ∠APB = 70° असल्यास ∠AOB किती?",
        ["70°", "90°", "110°", "140°"],
        2, "Circle", 2024, "board_based"
    ),

    # =========================
    # 2025
    # =========================
    (
        "खालीलपैकी कोणते पायथागोरस त्रिकूट आहे?",
        ["1, 5, 10", "3, 4, 5", "2, 2, 2", "5, 5, 2"],
        1, "Pythagoras Theorem", 2025, "board_verified"
    ),
    (
        "वर्तुळात ∠ACB = 65° असल्यास त्याच AB चापाचा प्रमुख चाप AXB किती अंशांचा असेल?",
        ["65°", "230°", "295°", "130°"],
        1, "Circle", 2025, "board_based"
    ),
    (
        "बिंदू (3, 4) चे उगमापासून अंतर किती?",
        ["7", "1", "5", "−5"],
        2, "Coordinate Geometry", 2025, "board_based"
    ),
    (
        "समकोनी त्रिकोणाच्या दोन बाजू 5 आणि 12 असल्यास कर्ण किती?",
        ["17", "4", "13", "60"],
        2, "Pythagoras Theorem", 2025, "board_based"
    ),
    (
        "△ABC मध्ये D हा BC वर असून BD = 7 आणि BC = 20. A(△ABD) : A(△ABC) किती?",
        ["7 : 20", "13 : 20", "7 : 13", "20 : 7"],
        0, "Area of Triangles", 2025, "board_based"
    ),
    (
        "समकोनी त्रिकोण MNP मध्ये NQ ⟂ MP, MQ = 9 आणि QP = 4 असल्यास NQ किती?",
        ["6", "13", "5", "√13"],
        0, "Similarity", 2025, "board_based"
    ),
    (
        "चतुर्भुज ABCD मध्ये ∠A = 100° आणि ABCD चक्रीय चतुर्भुज असल्यास ∠C किती?",
        ["80°", "100°", "180°", "90°"],
        0, "Circle", 2025, "board_based"
    ),
    (
        "त्रिज्या 10 आणि केंद्रीय कोन 90° असलेल्या sector चे क्षेत्रफळ (π = 3.14) किती?",
        ["31.4", "78.5", "157", "314"],
        1, "Mensuration", 2025, "board_based"
    ),
    (
        "दोन छेदणाऱ्या जीवा MN आणि RS, D येथे छेदतात. RD = 15, DS = 4, MD = 8 असल्यास DN किती?",
        ["6", "7.5", "8", "10"],
        1, "Circle", 2025, "board_based"
    ),
    (
        "उंची 10 असलेल्या वस्तूचा elevation angle 60° असल्यास, tan 60° = √3 वापरून क्षैतिज अंतर किती?",
        ["10√3", "10/√3", "20", "5√3"],
        1, "Trigonometry", 2025, "board_based"
    ),
    (
        "A(1, −3) आणि B(2, −5) या दोन बिंदूंचा मध्यबिंदू कोणता?",
        ["(3/2, −4)", "(1, −4)", "(3, −8)", "(−3/2, 4)"],
        0, "Coordinate Geometry", 2025, "board_based"
    ),
    (
        "sin θ = 11/61 असल्यास, θ तीव्रकोन मानून cos θ किती?",
        ["60/61", "11/60", "61/60", "50/61"],
        0, "Trigonometry", 2025, "board_based"
    ),
    (
        "XY ∥ AC, 2AX = 3BX आणि XY = 9 असल्यास AC किती?",
        ["12", "15", "18", "22.5"],
        3, "Similarity", 2025, "board_based"
    ),
    (
        "DE ∥ BC, DE = 4, BC = 8 आणि A(△ADE)=25 असल्यास A(△ABC) किती?",
        ["50", "75", "100", "125"],
        2, "Similarity", 2025, "board_based"
    ),
    (
        "DE : BC = 3 : 5 असल्यास A(△ADE) : A(△ABC) किती?",
        ["3 : 5", "9 : 25", "6 : 10", "25 : 9"],
        1, "Similarity", 2025, "board_based"
    ),

    # =========================
    # 2026
    # =========================
    (
        "खालीलपैकी कोणते पायथागोरस त्रिकूट आहे?",
        ["1, 5, 10", "3, 4, 5", "2, 2, 2", "5, 5, 2"],
        1, "Pythagoras Theorem", 2026, "board_verified"
    ),
    (
        "sec θ = 25/7 असल्यास tan θ किती?",
        ["7/24", "24/7", "25/24", "24/25"],
        1, "Trigonometry", 2026, "board_based"
    ),
    (
        "PQ = 3.6, QR = 6.4 आणि स्पर्शिका-छेदिका प्रमेयानुसार PS² = PQ × PR असल्यास PS किती?",
        ["3.6", "6", "10", "36"],
        1, "Circle", 2026, "board_based"
    ),
    (
        "त्रिज्या 7 असलेल्या वर्तुळाचे क्षेत्रफळ π = 22/7 घेतल्यास किती?",
        ["44", "77", "154", "308"],
        2, "Mensuration", 2026, "board_based"
    ),
    (
        "त्रिज्या 7 असलेल्या वर्तुळाचे क्षेत्रफळ 154 cm² आहे. त्यातून 38.5 cm² sector वजा केल्यास उरलेले क्षेत्रफळ किती?",
        ["115.5 cm²", "192.5 cm²", "77 cm²", "38.5 cm²"],
        0, "Mensuration", 2026, "board_based"
    ),
    (
        "△RST मध्ये ∠S = 90°, ∠T = 30° आणि RT = 12 असल्यास 30° समोरील बाजू RS किती?",
        ["3", "6", "12", "6√3"],
        1, "Trigonometry", 2026, "board_based"
    ),
    (
        "दोन छेदणाऱ्या जीवा MN आणि RS, D येथे छेदतात. RD = 15, DS = 4, MD = 8 असल्यास DN किती?",
        ["6", "7.5", "8", "10"],
        1, "Circle", 2026, "board_based"
    ),
    (
        "P(0, 6) आणि Q(12, 20) यांमधील अंतर किती?",
        ["14", "√340", "2√85", "26"],
        2, "Coordinate Geometry", 2026, "board_based"
    ),
    (
        "sin² θ + cos² θ याची किंमत किती?",
        ["0", "1", "sin θ", "cos θ"],
        1, "Trigonometry", 2026, "board_based"
    ),
    (
        "XY ∥ AC, 2AX = 3BX आणि XY = 9 असल्यास AC किती?",
        ["15", "18", "22.5", "27"],
        2, "Similarity", 2026, "board_based"
    ),
    (
        "A(−1, 7) आणि B(4, −3) यांना 2 : 3 या अंतर्गत प्रमाणात विभागणाऱ्या P बिंदूचे निर्देशांक कोणते?",
        ["(1, 3)", "(2, 1)", "(1, 1)", "(3, 1)"],
        2, "Coordinate Geometry", 2026, "board_based"
    ),
    (
        "△ABC ~ △ADE आणि AB/AD = 7/5 असल्यास A(△ABC) : A(△ADE) किती?",
        ["7 : 5", "49 : 25", "25 : 49", "14 : 10"],
        1, "Similarity", 2026, "board_based"
    ),
    (
        "वर्तुळाची त्रिज्या 28 असल्यास त्याचा व्यास किती?",
        ["14", "28", "44", "56"],
        3, "Circle", 2026, "board_based"
    ),
    (
        "समकोनी त्रिकोणात एक तीव्र कोन 60° असल्यास दुसरा तीव्र कोन किती?",
        ["20°", "30°", "45°", "60°"],
        1, "Trigonometry", 2026, "board_based"
    ),
    (
        "10√3 उंचीच्या मनोऱ्याच्या पायापासून एका बिंदूवरील elevation angle 60° असल्यास त्या बिंदूचे मनोऱ्यापासून अंतर किती?",
        ["10", "10√3", "20", "30"],
        0, "Trigonometry", 2026, "board_based"
    ),
]


def add_question(assessment, text, options, correct, category, year, origin):
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
            "question_origin": origin,
            "source_name": source["name"],
            "source_reference": source["ref"],
        },
    )

    if created:
        for i, option in enumerate(options):
            AssessmentOption.objects.create(
                question=q,
                option_text=option,
                is_correct=(i == correct),
                order=i + 1,
            )

    return created


assessment = Assessment.objects.get(slug=SLUG)

added = 0
for row in QUESTIONS:
    if add_question(assessment, *row):
        added += 1

assessment.total_questions = 25
assessment.duration_minutes = 25
assessment.is_active = True
assessment.save(update_fields=["total_questions", "duration_minutes", "is_active"])

print("=" * 65)
print("SSC MARATHI MATHEMATICS PART II – BOARD BANK COMPLETE")
print("=" * 65)
print("New questions added:", added)
print("Total questions:", assessment.questions.filter(is_active=True).count())

for year in (2024, 2025, 2026):
    print(
        year,
        assessment.questions.filter(
            is_active=True,
            board_year=year
        ).count()
    )

print("Board verified:",
      assessment.questions.filter(question_origin="board_verified").count())
print("Board based:",
      assessment.questions.filter(question_origin="board_based").count())
print("=" * 65)
