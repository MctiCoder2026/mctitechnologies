import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

django.setup()

from career_tools.models import AptitudeQuestion


questions = [

    # =====================================================
    # NUMERICAL - 4
    # =====================================================

    {
        "category": "numerical",
        "order": 1,
        "question": "What is 25% of 200?",
        "option_a": "25",
        "option_b": "50",
        "option_c": "75",
        "option_d": "100",
        "correct_option": "B",
        "difficulty": "easy",
        "explanation": "25% of 200 is 50.",
    },

    {
        "category": "numerical",
        "order": 2,
        "question": "If a product costs Rs. 800 and gets a 10% discount, what is the final price?",
        "option_a": "Rs. 700",
        "option_b": "Rs. 720",
        "option_c": "Rs. 740",
        "option_d": "Rs. 780",
        "correct_option": "B",
        "difficulty": "easy",
        "explanation": "10% of 800 is 80, so final price is Rs. 720.",
    },

    {
        "category": "numerical",
        "order": 3,
        "question": "A student scores 360 marks out of 450. What is the percentage?",
        "option_a": "70%",
        "option_b": "75%",
        "option_c": "80%",
        "option_d": "85%",
        "correct_option": "C",
        "difficulty": "medium",
        "explanation": "360 divided by 450 multiplied by 100 equals 80%.",
    },

    {
        "category": "numerical",
        "order": 4,
        "question": "What is the average of 10, 20, 30, 40 and 50?",
        "option_a": "25",
        "option_b": "30",
        "option_c": "35",
        "option_d": "40",
        "correct_option": "B",
        "difficulty": "easy",
        "explanation": "Total is 150 and 150 divided by 5 equals 30.",
    },

    # =====================================================
    # LOGICAL - 4
    # =====================================================

    {
        "category": "logical",
        "order": 1,
        "question": "Find the next number: 2, 4, 8, 16, ?",
        "option_a": "20",
        "option_b": "24",
        "option_c": "30",
        "option_d": "32",
        "correct_option": "D",
        "difficulty": "easy",
        "explanation": "Each number is multiplied by 2.",
    },

    {
        "category": "logical",
        "order": 2,
        "question": "If all laptops are machines and some machines are expensive, which statement is definitely true?",
        "option_a": "All laptops are expensive",
        "option_b": "All expensive things are laptops",
        "option_c": "All laptops are machines",
        "option_d": "No machine is expensive",
        "correct_option": "C",
        "difficulty": "medium",
        "explanation": "The only guaranteed statement is that all laptops are machines.",
    },

    {
        "category": "logical",
        "order": 3,
        "question": "Find the odd one out.",
        "option_a": "Apple",
        "option_b": "Mango",
        "option_c": "Banana",
        "option_d": "Carrot",
        "correct_option": "D",
        "difficulty": "easy",
        "explanation": "Carrot is a vegetable, while the others are fruits.",
    },

    {
        "category": "logical",
        "order": 4,
        "question": "If CAT is coded as DBU, how is DOG coded using the same rule?",
        "option_a": "EPH",
        "option_b": "EOG",
        "option_c": "DPH",
        "option_d": "FPH",
        "correct_option": "A",
        "difficulty": "medium",
        "explanation": "Each letter is shifted forward by one.",
    },

    # =====================================================
    # VERBAL - 4
    # =====================================================

    {
        "category": "verbal",
        "order": 1,
        "question": "Choose the synonym of 'Rapid'.",
        "option_a": "Slow",
        "option_b": "Fast",
        "option_c": "Weak",
        "option_d": "Late",
        "correct_option": "B",
        "difficulty": "easy",
        "explanation": "Rapid means fast.",
    },

    {
        "category": "verbal",
        "order": 2,
        "question": "Choose the opposite of 'Increase'.",
        "option_a": "Improve",
        "option_b": "Expand",
        "option_c": "Decrease",
        "option_d": "Develop",
        "correct_option": "C",
        "difficulty": "easy",
        "explanation": "Decrease is the opposite of increase.",
    },

    {
        "category": "verbal",
        "order": 3,
        "question": "Choose the correctly spelled word.",
        "option_a": "Recieve",
        "option_b": "Receive",
        "option_c": "Receeve",
        "option_d": "Receve",
        "correct_option": "B",
        "difficulty": "easy",
        "explanation": "The correct spelling is Receive.",
    },

    {
        "category": "verbal",
        "order": 4,
        "question": "Complete the sentence: She _____ to the office every day.",
        "option_a": "go",
        "option_b": "going",
        "option_c": "goes",
        "option_d": "gone",
        "correct_option": "C",
        "difficulty": "easy",
        "explanation": "With 'She', the correct present tense form is 'goes'.",
    },

    # =====================================================
    # COMPUTER / DIGITAL - 4
    # =====================================================

    {
        "category": "computer",
        "order": 1,
        "question": "Which application is mainly used for spreadsheets?",
        "option_a": "Microsoft Word",
        "option_b": "Microsoft Excel",
        "option_c": "Microsoft PowerPoint",
        "option_d": "Paint",
        "correct_option": "B",
        "difficulty": "easy",
        "explanation": "Microsoft Excel is used for spreadsheets.",
    },

    {
        "category": "computer",
        "order": 2,
        "question": "What does CPU stand for?",
        "option_a": "Central Processing Unit",
        "option_b": "Computer Personal Unit",
        "option_c": "Central Program Utility",
        "option_d": "Control Processing User",
        "correct_option": "A",
        "difficulty": "easy",
        "explanation": "CPU stands for Central Processing Unit.",
    },

    {
        "category": "computer",
        "order": 3,
        "question": "Which of these is a web browser?",
        "option_a": "Google Chrome",
        "option_b": "Microsoft Excel",
        "option_c": "Adobe Photoshop",
        "option_d": "Tally Prime",
        "correct_option": "A",
        "difficulty": "easy",
        "explanation": "Google Chrome is a web browser.",
    },

    {
        "category": "computer",
        "order": 4,
        "question": "Which file extension is commonly used for a Microsoft Excel workbook?",
        "option_a": ".docx",
        "option_b": ".pptx",
        "option_c": ".xlsx",
        "option_d": ".jpg",
        "correct_option": "C",
        "difficulty": "easy",
        "explanation": ".xlsx is a common Excel workbook format.",
    },

    # =====================================================
    # CAREER / WORK APTITUDE - 4
    # =====================================================

    {
        "category": "career",
        "order": 1,
        "question": "You receive a task you do not fully understand. What should you do first?",
        "option_a": "Ignore the task",
        "option_b": "Ask for clarification",
        "option_c": "Guess and submit immediately",
        "option_d": "Give the task to someone else",
        "correct_option": "B",
        "difficulty": "easy",
        "explanation": "Clarifying requirements helps avoid mistakes.",
    },

    {
        "category": "career",
        "order": 2,
        "question": "Two important tasks have the same deadline. What is the best approach?",
        "option_a": "Do nothing until the deadline",
        "option_b": "Choose randomly",
        "option_c": "Prioritize based on importance and discuss if needed",
        "option_d": "Ignore one task",
        "correct_option": "C",
        "difficulty": "medium",
        "explanation": "Good prioritization and communication are important workplace skills.",
    },

    {
        "category": "career",
        "order": 3,
        "question": "A teammate makes a small mistake. What is the most professional response?",
        "option_a": "Publicly criticize them",
        "option_b": "Ignore every mistake",
        "option_c": "Discuss it respectfully and help correct it",
        "option_d": "Complain to everyone",
        "correct_option": "C",
        "difficulty": "easy",
        "explanation": "Professional teamwork requires respectful communication.",
    },

    {
        "category": "career",
        "order": 4,
        "question": "Which habit is most useful for career growth?",
        "option_a": "Avoid learning new skills",
        "option_b": "Continuous learning and practice",
        "option_c": "Only wait for instructions",
        "option_d": "Never ask for feedback",
        "correct_option": "B",
        "difficulty": "easy",
        "explanation": "Continuous learning supports long-term career growth.",
    },
]


created = 0
updated = 0

for data in questions:

    question, was_created = AptitudeQuestion.objects.update_or_create(
        category=data["category"],
        order=data["order"],
        defaults={
            "question": data["question"],
            "option_a": data["option_a"],
            "option_b": data["option_b"],
            "option_c": data["option_c"],
            "option_d": data["option_d"],
            "correct_option": data["correct_option"],
            "difficulty": data["difficulty"],
            "explanation": data["explanation"],
            "is_active": True,
        }
    )

    if was_created:
        created += 1
    else:
        updated += 1


print("-----------------------------------")
print("MCTI APTITUDE QUESTION SEED COMPLETE")
print("-----------------------------------")
print("Created =", created)
print("Updated =", updated)
print("Total Active =", AptitudeQuestion.objects.filter(
    is_active=True
).count())