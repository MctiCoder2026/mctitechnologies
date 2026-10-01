from django.db import transaction
from core.models import Course
from lms.models import LMSModule, LMSTopic, QuizQuestion

COURSE_ID = 37
EXPECTED_SLUG = "autocad"

course = Course.objects.get(id=COURSE_ID)

if course.slug != EXPECTED_SLUG:
    raise RuntimeError("Safety stop: Course ID 37 is not AutoCAD.")

if LMSModule.objects.filter(course=course, order=1).exists():
    raise RuntimeError(
        "Safety stop: AutoCAD Module 1 already exists. Nothing changed."
    )

DATA = [
    {
        "title": "Introduction to AutoCAD",
        "notes": """AutoCAD is Computer-Aided Design software used to create accurate technical drawings.

Key concepts:
• CAD means Computer-Aided Design.
• AutoCAD is widely used in architecture, civil engineering, mechanical engineering and interior design.
• Drawings can be created and modified accurately using commands.
• Common drawing elements include lines, circles, arcs, dimensions and text.
• AutoCAD drawing files normally use the DWG format.

Practical Task:
Open AutoCAD and identify the drawing area, command line, ribbon and status bar. Create a new blank drawing and save it as AutoCAD_Practice_01.dwg.""",
        "questions": [
            ("What does CAD stand for?", "Computer-Aided Design", "Computer Automatic Drawing", "Creative Architectural Design", "Computer Application Development", "A"),
            ("Which file format is commonly used for AutoCAD drawings?", "DOCX", "DWG", "XLSX", "PPTX", "B"),
            ("AutoCAD is mainly used for which purpose?", "Technical drawing and design", "Video editing", "Accounting", "Email management", "A"),
            ("Which profession commonly uses AutoCAD?", "Civil engineering", "Music production only", "Banking only", "Medical billing only", "A"),
            ("What is an important advantage of CAD?", "Accurate technical drawing", "Automatic internet access", "Video streaming", "Email hosting", "A"),
        ],
    },
    {
        "title": "AutoCAD Interface and Workspace",
        "notes": """The AutoCAD interface provides tools required to create and edit drawings.

Important interface areas:
• Ribbon – contains commands organized into tabs and panels.
• Drawing Area – main area where objects are created.
• Command Line – displays commands, prompts and options.
• Status Bar – provides drawing aids such as Grid, Snap and Ortho.
• ViewCube – helps control drawing orientation in supported workspaces.

Practical Task:
Locate the Ribbon, Command Line, Drawing Area and Status Bar. Run the LINE command from the Ribbon and then type LINE in the Command Line to compare both methods.""",
        "questions": [
            ("Where are AutoCAD commands commonly organized into tabs and panels?", "Ribbon", "Status Bar", "Title Block", "Drawing Border", "A"),
            ("What does the Command Line display?", "Commands and prompts", "Only file names", "Only dimensions", "Only printer settings", "A"),
            ("Where are drawing objects mainly created?", "Drawing Area", "Status Bar", "File menu only", "Title bar", "A"),
            ("Which area contains drawing aids such as Ortho and Grid?", "Status Bar", "Ribbon title", "File Explorer", "View window title", "A"),
            ("What is the ViewCube mainly used for?", "Controlling drawing orientation", "Saving drawings", "Creating passwords", "Printing invoices", "A"),
        ],
    },
    {
        "title": "Creating, Opening and Saving Drawings",
        "notes": """Drawing file management is an essential AutoCAD skill.

Common operations:
• NEW creates a new drawing.
• OPEN opens an existing drawing.
• SAVE stores changes to the current drawing.
• SAVEAS saves the drawing with a different name or location.
• DWG is the standard AutoCAD drawing format.

Good Practice:
Use meaningful filenames and save your work regularly. Keep separate versions of important project drawings.

Practical Task:
Create a new drawing, draw three simple lines, save the file, close it, reopen it and save another copy using SAVEAS.""",
        "questions": [
            ("Which command starts a new drawing?", "NEW", "MOVE", "TRIM", "OFFSET", "A"),
            ("Which command opens an existing drawing?", "OPEN", "ARRAY", "ROTATE", "HATCH", "A"),
            ("Which command saves the current drawing?", "SAVE", "LINE", "ZOOM", "PAN", "A"),
            ("What does SAVEAS allow you to do?", "Save with another name or location", "Delete every object", "Create a circle", "Change drawing units only", "A"),
            ("Why should drawings be saved regularly?", "To reduce the risk of losing work", "To increase line thickness", "To create dimensions", "To activate Ortho", "A"),
        ],
    },
    {
        "title": "Drawing Units and Limits",
        "notes": """Correct drawing setup helps maintain accurate dimensions.

UNITS controls how measurements are represented in a drawing.

Common unit types include:
• Decimal
• Architectural
• Engineering
• Fractional

Drawing units may represent millimetres, centimetres, metres, inches or other project units depending on the drawing standard.

LIMITS can define a working boundary, although modern AutoCAD drawings are not physically restricted to that area.

Practical Task:
Run UNITS and inspect the available unit types and precision settings. Configure a practice drawing for decimal measurements and create objects using exact numeric lengths.""",
        "questions": [
            ("Which command is used to configure drawing units?", "UNITS", "TRIM", "MIRROR", "HATCH", "A"),
            ("Which is a valid AutoCAD unit type?", "Decimal", "Video", "Audio", "Database", "A"),
            ("Why are correct drawing units important?", "For accurate measurements", "For internet speed", "For file passwords", "For email settings", "A"),
            ("What can the precision setting control?", "Displayed measurement precision", "Monitor brightness", "Printer power", "Internet bandwidth", "A"),
            ("Which command can define a drawing working boundary?", "LIMITS", "COPY", "FILLET", "EXPLODE", "A"),
        ],
    },
    {
        "title": "Coordinate Systems",
        "notes": """Coordinates allow objects to be positioned accurately.

Important coordinate methods:
• Absolute coordinates – measured from the drawing origin.
• Relative coordinates – measured from the previous point.
• Polar coordinates – use distance and angle.
• The default User Coordinate System is commonly aligned with the World Coordinate System in a new 2D drawing.

Examples:
Absolute: 100,50
Relative Cartesian: @100,50
Relative Polar: @100<45

Practical Task:
Use the LINE command to create shapes using absolute coordinates, relative Cartesian coordinates and relative polar coordinates. Compare the three methods.""",
        "questions": [
            ("Absolute coordinates are normally measured from what reference?", "Drawing origin", "Previous point only", "Printer origin", "Screen corner only", "A"),
            ("Which symbol commonly indicates a relative coordinate?", "@", "#", "%", "&", "A"),
            ("Which coordinate method uses distance and angle?", "Polar coordinates", "Text coordinates", "Layer coordinates", "Print coordinates", "A"),
            ("What does @100,50 represent?", "A relative Cartesian coordinate", "An absolute coordinate", "A layer name", "A dimension style", "A"),
            ("What does @100<45 represent?", "A relative polar coordinate", "A file path", "A text style", "A plot scale", "A"),
        ],
    },
]

with transaction.atomic():
    module = LMSModule.objects.create(
        course=course,
        title="AutoCAD Fundamentals and Drawing Setup",
        description=(
            "Learn the AutoCAD interface, drawing setup, file management, "
            "units and coordinate systems through practical exercises."
        ),
        order=1,
        is_active=True,
    )

    for topic_order, item in enumerate(DATA, start=1):
        topic = LMSTopic.objects.create(
            module=module,
            title=item["title"],
            description=item["notes"],
            order=topic_order,
            is_active=True,
        )

        for q_order, q in enumerate(item["questions"], start=1):
            QuizQuestion.objects.create(
                topic=topic,
                language="en",
                question=q[0],
                option_a=q[1],
                option_b=q[2],
                option_c=q[3],
                option_d=q[4],
                correct_answer=q[5],
                order=q_order,
                is_active=True,
            )

print("AUTOCAD MODULE 1 CREATED ✅")
print(
    "Modules:",
    LMSModule.objects.filter(course=course).count()
)
print(
    "Topics:",
    LMSTopic.objects.filter(module__course=course).count()
)
print(
    "MCQs:",
    QuizQuestion.objects.filter(topic__module__course=course).count()
)
