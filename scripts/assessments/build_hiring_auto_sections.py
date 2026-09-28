from assessments.models import (
    Assessment,
    AssessmentQuestion,
    AssessmentOption,
)

PRACTICAL_CATEGORY = "AUTO_PRACTICAL"
COMMUNICATION_CATEGORY = "AUTO_COMMUNICATION"


def q(question, correct, wrong1, wrong2, wrong3):
    return (
        question,
        [correct, wrong1, wrong2, wrong3],
        0,
    )


AUTO_BANKS = {

    # ========================================================
    # DATA ANALYTICS TRAINER
    # ========================================================
    "hiring-data-analytics-trainer": {

        "practical": [
            q(
                "You receive an Excel file containing blank cells, duplicates and inconsistent date formats. What should you do first?",
                "Inspect and clean the dataset systematically before analysis",
                "Create the final dashboard immediately",
                "Replace every blank value with zero",
                "Delete all duplicate-looking rows without checking",
            ),
            q(
                "Sales totals become unusually high after joining two tables. What is the best first check?",
                "Check whether the join created duplicate matches",
                "Change the dashboard theme",
                "Round all numbers",
                "Remove the primary key",
            ),
            q(
                "A manager asks for monthly sales by branch from a large dataset. What is an appropriate approach?",
                "Clean the data, group by month and branch, then validate totals",
                "Manually type totals from memory",
                "Create one worksheet for every transaction",
                "Remove branch information",
            ),
            q(
                "A dashboard shows a different total from the source report. What should you do?",
                "Trace filters, calculations and source data until the difference is explained",
                "Choose whichever total looks better",
                "Publish both without checking",
                "Hide the KPI",
            ),
            q(
                "A numeric column contains values such as 'N/A' and text. What should happen before calculating averages?",
                "Identify invalid values and convert or handle them appropriately",
                "Treat all text as 100",
                "Ignore the entire column",
                "Convert every value to text",
            ),
            q(
                "You need to identify the top five products by revenue. What is the best approach?",
                "Aggregate revenue by product, validate it, sort descending and take the top five",
                "Select five products randomly",
                "Sort product names alphabetically",
                "Use only the first five rows",
            ),
            q(
                "A SQL query returns repeated customer records after a JOIN. What should you investigate?",
                "The relationship and join keys between the tables",
                "The font used by the SQL editor",
                "The monitor resolution",
                "The column heading colour",
            ),
            q(
                "Before presenting a business trend, what should an analyst verify?",
                "The calculation, time period, filters and underlying data quality",
                "Only the chart colour",
                "Only whether the graph is large",
                "Whether the result supports the manager's expectation",
            ),
            q(
                "An Excel formula gives correct results in the first row but wrong results after copying it down. What should be checked?",
                "Relative and absolute cell references",
                "Worksheet tab colour",
                "Computer username",
                "Printer settings",
            ),
            q(
                "You are asked to automate a recurring weekly report. What is the strongest approach?",
                "Create a repeatable data-cleaning and reporting process with validation",
                "Rebuild everything manually every week",
                "Copy last week's values",
                "Remove validation to save time",
            ),
        ],

        "communication": [
            q(
                "A beginner does not understand PivotTables after your first explanation. What should you do?",
                "Use a small familiar dataset and demonstrate the process step by step",
                "Repeat the same definition louder",
                "Skip the topic",
                "Tell the student to memorize the menu",
            ),
            q(
                "A student gives a wrong answer during class. What is the best trainer response?",
                "Understand their reasoning, correct the concept respectfully and let them retry",
                "Embarrass the student",
                "Ignore the mistake",
                "Immediately give the final answer without explanation",
            ),
            q(
                "Some students finish an Excel task quickly while others are struggling. What should the trainer do?",
                "Support struggling learners while giving extension work to faster learners",
                "Teach only the fastest students",
                "Stop the practical",
                "Give everyone the completed file",
            ),
            q(
                "What is the best way to explain a technical concept to a beginner?",
                "Use simple language, an example, demonstration and learner practice",
                "Use as much jargon as possible",
                "Read the definition only",
                "Avoid questions",
            ),
            q(
                "A student asks a question and you do not know the answer confidently. What should you do?",
                "Acknowledge it, verify the answer and follow up accurately",
                "Invent an answer",
                "Change the subject",
                "Tell the student never to ask it again",
            ),
            q(
                "How should a trainer verify that students understood a topic?",
                "Ask them to explain or perform a relevant task independently",
                "Ask only 'Did you understand?'",
                "Check attendance only",
                "Assume silence means understanding",
            ),
            q(
                "A student repeatedly makes the same Excel mistake. What is the best response?",
                "Identify the underlying misunderstanding and give focused guided practice",
                "Complete every task for the student",
                "Remove the student from the class",
                "Ignore repeated mistakes",
            ),
            q(
                "During a practical session, several students need help at once. What is the best approach?",
                "Prioritize common issues, guide the group and then support individual cases",
                "Help only the strongest student",
                "End the class",
                "Give answers without explanation",
            ),
            q(
                "What makes classroom communication effective?",
                "Clear explanations, listening, relevant examples and checking understanding",
                "Speaking continuously without questions",
                "Using difficult vocabulary",
                "Avoiding student interaction",
            ),
            q(
                "A student says data analysis is too difficult and wants to quit. What should a trainer do?",
                "Break the skill into achievable steps and use practical progress to build confidence",
                "Agree that they cannot learn it",
                "Give them advanced work immediately",
                "Ignore the concern",
            ),
        ],
    },

    # ========================================================
    # PYTHON TRAINER
    # ========================================================
    "hiring-python-trainer": {

        "practical": [
            q(
                "A Python program raises a TypeError after user input is used in arithmetic. What should be checked first?",
                "Whether the input needs conversion to the required numeric type",
                "The monitor brightness",
                "The Python logo",
                "The folder colour",
            ),
            q(
                "A loop is running forever. What is the best first debugging step?",
                "Inspect the loop condition and whether its controlling values change",
                "Reinstall Python",
                "Delete all functions",
                "Add more print colours",
            ),
            q(
                "A function returns None unexpectedly. What should you inspect?",
                "Its return paths and conditions",
                "The computer wallpaper",
                "The filename length only",
                "The keyboard language",
            ),
            q(
                "A list contains duplicate values but unique values are required. Which approach is commonly suitable?",
                "Use an appropriate uniqueness strategy such as a set while considering order requirements",
                "Duplicate the list again",
                "Convert every item to zero",
                "Store the values in separate files",
            ),
            q(
                "A program works for normal input but crashes when a file is missing. What should be improved?",
                "Error handling for the file operation",
                "Variable colours",
                "Screen resolution",
                "The Python installation name",
            ),
            q(
                "A student-written function contains repeated code in several places. What is a good improvement?",
                "Refactor repeated logic into reusable functions where appropriate",
                "Copy the code more times",
                "Remove function names",
                "Replace all variables with constants",
            ),
            q(
                "A Python dictionary lookup may reference a missing key. What should the developer consider?",
                "Handle the possibility of the key being absent appropriately",
                "Disable dictionaries",
                "Convert the dictionary to an image",
                "Always assume every key exists",
            ),
            q(
                "Before changing working production Python code, what is good practice?",
                "Test the change safely and preserve version history",
                "Edit production blindly",
                "Delete the previous version",
                "Disable logs",
            ),
            q(
                "A program produces the wrong total. What is the best debugging approach?",
                "Trace inputs, intermediate values and calculation logic systematically",
                "Guess a new total",
                "Change random lines",
                "Hide the output",
            ),
            q(
                "What best demonstrates practical Python ability?",
                "Building and explaining a small working solution to a defined problem",
                "Memorizing Python's logo",
                "Knowing only definitions",
                "Typing code without understanding it",
            ),
        ],

        "communication": [
            q(
                "How should a trainer introduce Python variables to a complete beginner?",
                "Use simple values and demonstrate how names reference changing data",
                "Start with metaclasses",
                "Give only a formal definition",
                "Skip examples",
            ),
            q(
                "A student copies code correctly but cannot explain it. What should the trainer do?",
                "Ask the student to predict, modify and explain small parts of the code",
                "Mark the topic complete",
                "Give more code to copy",
                "Ignore understanding",
            ),
            q(
                "A beginner is afraid of error messages. What should a Python trainer teach?",
                "How to read errors step by step and use them as debugging information",
                "That errors should always be hidden",
                "That every error requires reinstalling Python",
                "To avoid running code",
            ),
            q(
                "Students understand loops theoretically but cannot write one. What is the best next step?",
                "Give a small guided problem followed by independent practice",
                "Repeat the definition only",
                "Move immediately to advanced frameworks",
                "Remove practical work",
            ),
            q(
                "A student asks why functions are useful. What is the clearest approach?",
                "Show repeated code and then refactor it into a reusable function",
                "Ask them to memorize the word function",
                "Say functions are compulsory without explanation",
                "Skip the question",
            ),
            q(
                "What is the best way to check whether a student understands Python conditions?",
                "Give a new decision-making problem for the student to solve",
                "Ask if they attended class",
                "Ask them to copy an if statement",
                "Check typing speed",
            ),
            q(
                "A mixed-level class has both beginners and experienced learners. What should the trainer do?",
                "Use core guided tasks plus extension challenges for faster learners",
                "Teach only advanced learners",
                "Teach only beginners forever",
                "Remove exercises",
            ),
            q(
                "A student's solution works but is difficult to understand. What should the trainer encourage?",
                "Clear naming, simpler structure and explanation of the logic",
                "More unnecessary complexity",
                "Removing all comments and names",
                "Copying another solution without review",
            ),
            q(
                "When demonstrating code live, what is a useful teaching practice?",
                "Explain the reasoning, predict outcomes and test the code with students",
                "Paste the entire solution silently",
                "Avoid running the code",
                "Hide errors when they occur",
            ),
            q(
                "A student becomes frustrated after several failed attempts. What is the best trainer response?",
                "Break the problem into smaller steps and guide them without simply giving the answer",
                "Tell them programming is not for them",
                "Complete all future exercises for them",
                "Ignore the student",
            ),
        ],
    },
}


def seed_section(assessment, category, start_order, questions):
    if len(questions) != 10:
        raise ValueError(
            f"{assessment.slug} {category}: expected 10 questions, "
            f"got {len(questions)}"
        )

    for offset, item in enumerate(questions):
        order = start_order + offset
        text, options, correct_index = item

        if len(options) != 4:
            raise ValueError(
                f"{assessment.slug} Q{order}: expected 4 options"
            )

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
                    "is_correct": (
                        option_order - 1 == correct_index
                    ),
                },
            )


def audit(assessment):
    technical = assessment.questions.filter(
        is_active=True,
        order__lte=25,
    )

    practical = assessment.questions.filter(
        is_active=True,
        category=PRACTICAL_CATEGORY,
        order__gte=26,
        order__lte=35,
    )

    communication = assessment.questions.filter(
        is_active=True,
        category=COMMUNICATION_CATEGORY,
        order__gte=36,
        order__lte=45,
    )

    all_questions = assessment.questions.filter(
        is_active=True,
        order__lte=45,
    )

    invalid = []

    for question in all_questions:
        options = question.options.all()

        if (
            options.count() != 4
            or options.filter(is_correct=True).count() != 1
        ):
            invalid.append(question.order)

    return {
        "technical": technical.count(),
        "practical": practical.count(),
        "communication": communication.count(),
        "total": all_questions.count(),
        "invalid": invalid,
    }


for slug, sections in AUTO_BANKS.items():
    assessment = Assessment.objects.get(
        slug=slug,
        assessment_type="hiring",
    )

    seed_section(
        assessment,
        PRACTICAL_CATEGORY,
        26,
        sections["practical"],
    )

    seed_section(
        assessment,
        COMMUNICATION_CATEGORY,
        36,
        sections["communication"],
    )

    result = audit(assessment)

    if (
        result["technical"] != 25
        or result["practical"] != 10
        or result["communication"] != 10
        or result["total"] != 45
        or result["invalid"]
    ):
        raise RuntimeError(
            f"{slug} FAILED AUTO SECTION AUDIT: {result}"
        )

    print(
        f"OK | {slug} | "
        f"Technical={result['technical']} | "
        f"Practical={result['practical']} | "
        f"Communication={result['communication']} | "
        f"Total={result['total']}"
    )

print("=" * 65)
print("HIRING AUTO-SECTIONS PILOT PASSED")
