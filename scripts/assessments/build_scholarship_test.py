from assessments.models import Assessment, AssessmentQuestion, AssessmentOption


QUESTIONS = [
    # =========================================================
    # APTITUDE & LOGICAL REASONING — 10
    # =========================================================
    ("Aptitude & Logical Reasoning", "What is 25% of 200?",
     ["25", "50", "75", "100"], 1),

    ("Aptitude & Logical Reasoning", "If 5 pens cost ₹100, what is the cost of 8 pens at the same rate?",
     ["₹120", "₹140", "₹160", "₹180"], 2),

    ("Aptitude & Logical Reasoning", "Find the next number: 2, 4, 8, 16, ?",
     ["18", "24", "30", "32"], 3),

    ("Aptitude & Logical Reasoning", "A student scores 72 marks out of 90. What percentage did the student score?",
     ["70%", "75%", "80%", "90%"], 2),

    ("Aptitude & Logical Reasoning", "Which number is different from the others?",
     ["2", "4", "8", "15"], 3),

    ("Aptitude & Logical Reasoning", "If TODAY is Monday, what day will it be after 10 days?",
     ["Wednesday", "Thursday", "Friday", "Saturday"], 1),

    ("Aptitude & Logical Reasoning", "What is the average of 10, 20 and 30?",
     ["15", "20", "25", "30"], 1),

    ("Aptitude & Logical Reasoning", "Complete the series: 5, 10, 15, 20, ?",
     ["22", "24", "25", "30"], 2),

    ("Aptitude & Logical Reasoning", "A course fee is ₹10,000 and a student receives a 20% discount. What amount remains payable?",
     ["₹2,000", "₹6,000", "₹8,000", "₹9,000"], 2),

    ("Aptitude & Logical Reasoning", "If all trainers are teachers and some teachers are developers, which statement is definitely true?",
     ["All developers are trainers", "All trainers are teachers", "All teachers are trainers", "No trainer is a developer"], 1),

    # =========================================================
    # COMPUTER & DIGITAL AWARENESS — 10
    # =========================================================
    ("Computer & Digital Awareness", "Which component is commonly called the brain of a computer?",
     ["Keyboard", "CPU", "Monitor", "Mouse"], 1),

    ("Computer & Digital Awareness", "Which application is primarily used for spreadsheets?",
     ["Microsoft Excel", "Microsoft Word", "Paint", "Notepad"], 0),

    ("Computer & Digital Awareness", "What does AI stand for?",
     ["Automatic Internet", "Artificial Intelligence", "Advanced Input", "Applied Information"], 1),

    ("Computer & Digital Awareness", "Which of these is a web browser?",
     ["Google Chrome", "Microsoft Excel", "Adobe Photoshop", "Tally"], 0),

    ("Computer & Digital Awareness", "Which is the strongest password?",
     ["12345678", "password", "Mcti@2026#Learn", "abcdefgh"], 2),

    ("Computer & Digital Awareness", "What is cloud computing commonly used for?",
     ["Only printing", "Accessing computing resources over the internet", "Cleaning computer hardware", "Only typing documents"], 1),

    ("Computer & Digital Awareness", "Which file extension is commonly associated with Microsoft Excel workbooks?",
     [".xlsx", ".mp3", ".jpg", ".exe"], 0),

    ("Computer & Digital Awareness", "Phishing usually attempts to:",
     ["Improve internet speed", "Steal sensitive information using deceptive messages", "Repair hardware", "Compress files"], 1),

    ("Computer & Digital Awareness", "Which technology is commonly used to create the structure of a web page?",
     ["HTML", "Tally", "PowerPoint", "BIOS"], 0),

    ("Computer & Digital Awareness", "What is the main purpose of a database?",
     ["Play music", "Store and organize data", "Draw pictures only", "Increase monitor brightness"], 1),

    # =========================================================
    # CAREER & WORKPLACE READINESS — 10
    # =========================================================
    ("Career & Workplace Readiness", "When you do not understand a task at work, what is the best first action?",
     ["Ignore it", "Ask for clarification", "Leave the workplace", "Guess without checking"], 1),

    ("Career & Workplace Readiness", "Which is most appropriate for a professional email?",
     ["Clear subject and respectful message", "No subject", "Only emojis", "Random abbreviations"], 0),

    ("Career & Workplace Readiness", "A deadline is approaching and your task may be delayed. What should you do?",
     ["Say nothing", "Inform the responsible person early and discuss a solution", "Delete the task", "Wait until after the deadline"], 1),

    ("Career & Workplace Readiness", "Which skill is important when working in a team?",
     ["Communication", "Avoiding everyone", "Ignoring feedback", "Never sharing information"], 0),

    ("Career & Workplace Readiness", "What is a good way to improve a professional skill?",
     ["Regular practice and feedback", "Avoid practice", "Only watch others", "Ignore mistakes"], 0),

    ("Career & Workplace Readiness", "If you make a mistake at work, what is the most professional response?",
     ["Hide it", "Blame someone else", "Acknowledge it and work on a correction", "Repeat it"], 2),

    ("Career & Workplace Readiness", "Which document generally summarizes education, skills and experience for a job application?",
     ["Resume", "Invoice", "Receipt", "Attendance sheet"], 0),

    ("Career & Workplace Readiness", "During an interview, if you do not know an answer, what is the best approach?",
     ["Give false information confidently", "Be honest and explain how you would find or learn the answer", "End the interview", "Change the subject"], 1),

    ("Career & Workplace Readiness", "Which habit best supports long-term career growth?",
     ["Continuous learning", "Avoiding new technology", "Never taking feedback", "Learning only once"], 0),

    ("Career & Workplace Readiness", "What should primarily guide your choice of a career skill to develop?",
     ["Your interests, aptitude and career opportunities", "Only what a friend chooses", "Random selection", "Only the course name"], 0),
]


def run():
    assessment, created = Assessment.objects.update_or_create(
        slug="mcti-scholarship-test-2026",
        defaults={
            "title": "MCTI Scholarship Test 2026",
            "assessment_type": "scholarship",
            "description": (
                "MCTI Scholarship Test to assess aptitude, digital awareness "
                "and career readiness for scholarship eligibility."
            ),
            "total_questions": 30,
            "passing_score": 0,
            "duration_minutes": 30,
            "is_active": True,
            "certificate_enabled": False,
            "lead_capture_enabled": True,
        },
    )

    for order, (category, question_text, options, correct_index) in enumerate(
        QUESTIONS, start=1
    ):
        question, _ = AssessmentQuestion.objects.update_or_create(
            assessment=assessment,
            order=order,
            defaults={
                "question_text": question_text,
                "category": category,
                "marks": 1,
                "is_active": True,
            },
        )

        for option_order, option_text in enumerate(options, start=1):
            AssessmentOption.objects.update_or_create(
                question=question,
                order=option_order,
                defaults={
                    "option_text": option_text,
                    "is_correct": option_order - 1 == correct_index,
                },
            )

    print("======================================")
    print("MCTI SCHOLARSHIP TEST READY")
    print("======================================")
    print("Assessment ID:", assessment.id)
    print("Created:", created)
    print("Slug:", assessment.slug)
    print("Questions:", assessment.questions.filter(is_active=True).count())
    print("Options:", AssessmentOption.objects.filter(
        question__assessment=assessment,
        question__is_active=True,
    ).count())
    print("Duration:", assessment.duration_minutes, "minutes")
    print("======================================")
