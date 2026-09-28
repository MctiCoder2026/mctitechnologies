from assessments.models import Assessment, AssessmentQuestion, AssessmentOption

SLUG = "hiring-python-trainer"

QUESTIONS = [
    ("Python Fundamentals", "Which Python data type is mutable?", ["Tuple", "String", "List", "Integer"], 2),
    ("Python Fundamentals", "What does len([10, 20, 30]) return?", ["2", "3", "30", "Error"], 1),
    ("Python Fundamentals", "Which keyword is used to define a function in Python?", ["func", "define", "def", "function"], 2),
    ("Python Fundamentals", "What is the result of 10 // 3 in Python?", ["3", "3.33", "1", "4"], 0),
    ("Python Fundamentals", "Which collection stores unique values?", ["List", "Tuple", "Set", "String"], 2),

    ("Functions & OOP", "What is the purpose of the return statement in a function?", ["Stop Python permanently", "Send a value back to the caller", "Print only", "Create a class"], 1),
    ("Functions & OOP", "In a Python instance method, what does self normally refer to?", ["The current object instance", "The parent class only", "A global variable", "The Python interpreter"], 0),
    ("Functions & OOP", "Which concept allows a child class to acquire behavior from a parent class?", ["Iteration", "Inheritance", "Indexing", "Slicing"], 1),
    ("Functions & OOP", "Which special method is commonly used to initialize a new object?", ["__start__", "__init__", "__create__", "__main__"], 1),
    ("Functions & OOP", "What is polymorphism intended to support?", ["One interface with different implementations", "Only one class in a program", "Removing all methods", "Preventing object creation"], 0),

    ("Practical & Debugging", "Which exception is raised by int('abc')?", ["TypeError", "ValueError", "KeyError", "IndexError"], 1),
    ("Practical & Debugging", "Which block is used to handle an exception?", ["if/else", "for/while", "try/except", "class/def"], 2),
    ("Practical & Debugging", "A program must process every item in a list. Which construct is normally most suitable?", ["for loop", "class declaration", "import statement", "exception only"], 0),
    ("Practical & Debugging", "Which mode opens a text file for appending without replacing existing content?", ["r", "w", "a", "x"], 2),
    ("Practical & Debugging", "What is the safest first step when a student's program gives an unexpected result?", ["Rewrite the entire program", "Inspect the error/output and reproduce the issue", "Change random lines", "Reinstall Python immediately"], 1),

    ("Training Ability", "A beginner does not understand loops. What is the most effective first teaching approach?", ["Start with a simple repeated real-life task and trace iterations", "Give only the formal definition", "Skip loops", "Ask the student to memorize syntax"], 0),
    ("Training Ability", "A student copies code correctly but cannot explain it. What should a trainer do next?", ["Move immediately to the next chapter", "Ask the student to trace and explain the code step by step", "Give more code to copy", "Mark the topic complete"], 1),
    ("Training Ability", "During a coding demo, a student gets an error. What should the trainer encourage first?", ["Read the error message and identify the failing line", "Delete the project", "Ignore the error", "Copy another student's output"], 0),
    ("Training Ability", "Which method best checks whether students understood a Python concept?", ["Ask only 'understood?'", "Give a small task requiring them to apply the concept", "Show another slide", "End the class early"], 1),
    ("Training Ability", "Students in one batch learn at different speeds. What is the best trainer response?", ["Teach only the fastest students", "Use guided practice and additional support while maintaining learning goals", "Remove difficult topics", "Give everyone answers"], 1),

    ("Development Understanding", "Which Python structure is most appropriate for mapping student IDs to student names?", ["Dictionary", "Set only", "Integer", "Boolean"], 0),
    ("Development Understanding", "Why are virtual environments commonly used in Python projects?", ["To isolate project dependencies", "To increase monitor resolution", "To replace databases", "To create HTML automatically"], 0),
    ("Development Understanding", "What is the primary purpose of Git in a development project?", ["Version control", "Database hosting", "Image editing", "Operating system installation"], 0),
    ("Development Understanding", "In a web application, why should user input be validated?", ["To reduce invalid or unsafe data entering the system", "To make every field optional", "To avoid writing functions", "To disable the database"], 0),
    ("Development Understanding", "Before deploying a code change to a live system, what is the best practice?", ["Test the change and verify it does not break existing functionality", "Deploy without testing", "Delete the previous project", "Change production data manually"], 0),
]

assessment = Assessment.objects.get(slug=SLUG)

for order, (category, text, options, correct_index) in enumerate(QUESTIONS, start=1):
    question, created = AssessmentQuestion.objects.update_or_create(
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
                "is_correct": (option_order - 1 == correct_index),
            },
        )

    print(order, category, "CREATED" if created else "UPDATED")

print("TOTAL QUESTIONS:", assessment.questions.count())
print("TOTAL OPTIONS:", AssessmentOption.objects.filter(question__assessment=assessment).count())
print("CORRECT OPTIONS:", AssessmentOption.objects.filter(question__assessment=assessment, is_correct=True).count())
