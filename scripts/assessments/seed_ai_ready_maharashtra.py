from assessments.models import Assessment, AssessmentQuestion, AssessmentOption

SLUG = "ai-ready-maharashtra-2026"

QUESTIONS = [
    # AI FUNDAMENTALS
    ("AI Fundamentals", "What does AI stand for?",
     ["Automated Internet", "Artificial Intelligence", "Advanced Interface", "Artificial Internet"], 2),

    ("AI Fundamentals", "Which statement best describes Artificial Intelligence?",
     ["Technology that enables computers to perform tasks that normally require human intelligence",
      "A faster type of internet connection",
      "A computer storage device",
      "A social media platform"], 1),

    ("AI Fundamentals", "Which of these is a common example of AI?",
     ["Voice assistant", "USB cable", "Keyboard", "Printer paper"], 1),

    ("AI Fundamentals", "Machine Learning is best described as:",
     ["A method that allows systems to learn patterns from data",
      "A method for repairing computer hardware",
      "A type of computer monitor",
      "A file compression technique"], 1),

    ("AI Fundamentals", "Why is data important for many AI systems?",
     ["It helps AI systems learn patterns and make predictions",
      "It increases monitor size",
      "It replaces electricity",
      "It automatically repairs hardware"], 1),

    # AI IN DAILY LIFE
    ("AI in Daily Life", "Which feature commonly uses AI on a smartphone?",
     ["Face recognition", "Charging cable", "SIM tray", "Volume button"], 1),

    ("AI in Daily Life", "How can an online shopping platform use AI?",
     ["To recommend products based on user activity",
      "To physically manufacture every product",
      "To replace the internet",
      "To increase the phone battery size"], 1),

    ("AI in Daily Life", "Which is a common AI use in navigation apps?",
     ["Estimating routes and travel time",
      "Increasing vehicle fuel capacity",
      "Changing the road surface",
      "Printing a driving licence"], 1),

    ("AI in Daily Life", "An email service may use AI to:",
     ["Detect spam messages",
      "Increase screen brightness",
      "Repair a keyboard",
      "Charge a laptop"], 1),

    # GENERATIVE AI
    ("Generative AI", "What can Generative AI commonly create?",
     ["Text, images, audio or other new content",
      "Only computer cables",
      "Only printed books",
      "Only hardware components"], 1),

    ("Generative AI", "ChatGPT is primarily an example of:",
     ["A generative AI assistant",
      "A computer processor",
      "A web browser cable",
      "A storage drive"], 1),

    ("Generative AI", "Which task is suitable for a generative AI assistant?",
     ["Drafting an email from instructions",
      "Physically replacing laptop RAM",
      "Charging a mobile phone",
      "Connecting an electrical socket"], 1),

    ("Generative AI", "When using AI-generated information, what is a good practice?",
     ["Verify important facts before using them",
      "Assume every response is always correct",
      "Share every password with the AI",
      "Ignore the source of important information"], 1),

    # PROMPTING & PRODUCTIVITY
    ("Prompting & Productivity", "In Generative AI, what is a prompt?",
     ["An instruction or question given to the AI",
      "A computer motherboard",
      "A type of printer",
      "An internet cable"], 1),

    ("Prompting & Productivity", "Which prompt is likely to produce a more useful response?",
     ["Create a 5-point interview preparation plan for a fresher applying for a data analyst role",
      "Tell me something",
      "Do work",
      "Give stuff"], 1),

    ("Prompting & Productivity", "Why is context useful in an AI prompt?",
     ["It helps the AI understand the goal and produce a more relevant response",
      "It increases computer RAM",
      "It changes the keyboard layout",
      "It automatically upgrades the internet plan"], 1),

    ("Prompting & Productivity", "Which activity can AI assist with in office productivity?",
     ["Summarizing a long document",
      "Physically replacing a damaged monitor",
      "Installing an electrical switch",
      "Increasing desk size"], 1),

    # AI & CAREERS
    ("AI & Careers", "Which skill becomes especially useful when working with AI tools?",
     ["Critical thinking", "Ignoring accuracy", "Avoiding learning", "Sharing passwords"], 1),

    ("AI & Careers", "How can AI help a job seeker?",
     ["Practice interview questions and improve a resume draft",
      "Guarantee a job without skills",
      "Automatically issue a university degree",
      "Replace every hiring decision"], 1),

    ("AI & Careers", "What is a useful approach as AI changes job roles?",
     ["Continuously learn and combine domain skills with AI tools",
      "Stop learning new skills",
      "Avoid all technology",
      "Depend on AI without checking its work"], 1),

    ("AI & Careers", "Which statement about AI and careers is most appropriate?",
     ["People can improve productivity by learning how to use AI responsibly",
      "AI makes every human skill unnecessary",
      "AI guarantees the same career outcome for everyone",
      "Learning fundamentals is no longer useful"], 1),

    # RESPONSIBLE AI
    ("Responsible AI", "Which information should you avoid entering into a public AI tool?",
     ["Passwords and sensitive personal information",
      "A general study topic",
      "A public course name",
      "A general writing request"], 1),

    ("Responsible AI", "What should you do if an AI answer affects an important decision?",
     ["Verify it using reliable sources or qualified expertise",
      "Trust it automatically",
      "Forward it without reading",
      "Assume AI cannot make mistakes"], 1),

    ("Responsible AI", "What is an AI hallucination?",
     ["When an AI generates incorrect or unsupported information as if it were factual",
      "When a computer enters sleep mode",
      "When a phone battery is empty",
      "When a printer runs out of paper"], 1),

    ("Responsible AI", "What is responsible use of AI for student assignments?",
     ["Use AI as a learning aid while understanding, checking and following academic rules",
      "Submit unchecked AI output as your own work in every situation",
      "Use AI to obtain another person's passwords",
      "Ignore accuracy and academic guidelines"], 1),
]


def run():
    assessment = Assessment.objects.get(slug=SLUG)

    if len(QUESTIONS) != 25:
        raise ValueError(f"Expected 25 questions, found {len(QUESTIONS)}")

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

        for option_order, option_text in enumerate(options, start=1):
            AssessmentOption.objects.update_or_create(
                question=question,
                order=option_order,
                defaults={
                    "option_text": option_text,
                    "is_correct": option_order == correct,
                },
            )

    print("ASSESSMENT:", assessment.title)
    print("QUESTIONS:", assessment.questions.count())
    print(
        "OPTIONS:",
        AssessmentOption.objects.filter(question__assessment=assessment).count()
    )
    print(
        "CORRECT OPTIONS:",
        AssessmentOption.objects.filter(
            question__assessment=assessment,
            is_correct=True
        ).count()
    )


if __name__ == "__main__":
    run()
