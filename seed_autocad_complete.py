from django.db import transaction
from core.models import Course
from lms.models import LMSModule, LMSTopic, QuizQuestion

COURSE_ID = 37
EXPECTED_SLUG = "autocad"

course = Course.objects.get(id=COURSE_ID)

if course.slug != EXPECTED_SLUG:
    raise RuntimeError(
        f"SAFETY STOP: Course {COURSE_ID} is {course.slug}, not autocad."
    )

# ------------------------------------------------------------
# SAFETY CHECK — Modules 1 & 2 must already be complete.
# Modules 3–10 must NOT exist.
# ------------------------------------------------------------

existing_modules = LMSModule.objects.filter(course=course)

for order in (1, 2):
    module = existing_modules.filter(order=order).first()

    if not module:
        raise RuntimeError(
            f"SAFETY STOP: AutoCAD Module {order} is missing."
        )

    topic_count = LMSTopic.objects.filter(module=module).count()
    mcq_count = QuizQuestion.objects.filter(topic__module=module).count()

    if topic_count != 5 or mcq_count != 25:
        raise RuntimeError(
            f"SAFETY STOP: Module {order} expected 5 topics/25 MCQs, "
            f"found {topic_count}/{mcq_count}."
        )

if existing_modules.filter(order__gte=3).exists():
    found = list(
        existing_modules.filter(order__gte=3)
        .values_list("order", "title")
    )
    raise RuntimeError(
        f"SAFETY STOP: Modules 3–10 already contain data: {found}"
    )

# ------------------------------------------------------------
# COURSE CONTENT
# Each topic:
# title, concept, command, practice, key_answer
# ------------------------------------------------------------

MODULES = [

    (
        2,
        "Basic Drawing Commands",
        "Create accurate 2D geometry using essential AutoCAD drawing commands.",
        [
            (
                "LINE Command",
                "Creates individual straight line segments between specified points.",
                "LINE",
                "Create a 100 x 60 rectangular outline using exact coordinates.",
                "straight line segments",
            ),
            (
                "POLYLINE Command",
                "Creates connected line or arc segments that behave as a single object.",
                "PLINE",
                "Create a closed irregular boundary using one polyline.",
                "connected segments as one object",
            ),
            (
                "CIRCLE Command",
                "Creates circles using center-radius, center-diameter and other construction methods.",
                "CIRCLE",
                "Create circles of radius 25 and diameter 100.",
                "circles",
            ),
            (
                "ARC Command",
                "Creates a portion of a circle using points, center, angle or other options.",
                "ARC",
                "Create three different arcs using the 3-point method.",
                "circular arcs",
            ),
            (
                "RECTANGLE and POLYGON",
                "Creates rectangular and regular multi-sided closed shapes.",
                "RECTANGLE / POLYGON",
                "Create a 100 x 60 rectangle and a regular hexagon.",
                "regular closed shapes",
            ),
        ],
    ),

    (
        3,
        "Modify Commands",
        "Edit existing AutoCAD geometry accurately using essential modify commands.",
        [
            (
                "MOVE and COPY",
                "MOVE changes an object's location while COPY creates one or more duplicates.",
                "MOVE / COPY",
                "Draw a chair symbol, move it to another location and create three copies.",
                "repositioning and duplicating objects",
            ),
            (
                "ROTATE",
                "Rotates selected objects around a specified base point by an angle.",
                "ROTATE",
                "Create a rectangle and rotate copies through 30, 45 and 90 degrees.",
                "rotating objects",
            ),
            (
                "SCALE",
                "Changes object size proportionally using a scale factor or reference.",
                "SCALE",
                "Create an object and produce half-size and double-size versions.",
                "changing object size proportionally",
            ),
            (
                "TRIM and EXTEND",
                "TRIM removes unwanted portions while EXTEND lengthens objects to a boundary.",
                "TRIM / EXTEND",
                "Create intersecting lines and practice trimming and extending them.",
                "shortening and extending geometry",
            ),
            (
                "OFFSET and MIRROR",
                "OFFSET creates parallel or concentric copies while MIRROR creates symmetrical copies.",
                "OFFSET / MIRROR",
                "Create wall lines using OFFSET and a symmetrical shape using MIRROR.",
                "parallel and symmetrical copies",
            ),
        ],
    ),

    (
        4,
        "Advanced Modify Tools",
        "Use advanced editing tools for repetitive geometry, corners and object cleanup.",
        [
            (
                "ARRAY",
                "Creates multiple copies of objects in rectangular, polar or path arrangements.",
                "ARRAY",
                "Create eight equally spaced circles using a polar array.",
                "multiple patterned copies",
            ),
            (
                "FILLET",
                "Joins two objects with a rounded corner of a specified radius.",
                "FILLET",
                "Create two perpendicular lines and apply different fillet radii.",
                "rounded corners",
            ),
            (
                "CHAMFER",
                "Joins two objects with an angled straight edge instead of a rounded corner.",
                "CHAMFER",
                "Create a rectangle and chamfer its corners using specified distances.",
                "angled corners",
            ),
            (
                "STRETCH",
                "Moves selected vertices or portions of objects while retaining connected geometry.",
                "STRETCH",
                "Stretch one side of a room plan while keeping the opposite side unchanged.",
                "changing part of an object",
            ),
            (
                "BREAK, JOIN and EXPLODE",
                "BREAK separates geometry, JOIN combines compatible objects and EXPLODE separates compound objects.",
                "BREAK / JOIN / EXPLODE",
                "Create sample geometry and test BREAK, JOIN and EXPLODE.",
                "separating and combining geometry",
            ),
        ],
    ),

    (
        5,
        "Layers and Object Properties",
        "Organize professional drawings using layers, colors, linetypes and object properties.",
        [
            (
                "Introduction to Layers",
                "Layers organize drawing objects into logical categories for easier control.",
                "LAYER",
                "Create WALL, DOOR, WINDOW, TEXT and DIMENSION layers.",
                "organizing drawing objects",
            ),
            (
                "Layer Properties",
                "Layer properties control color, linetype, lineweight and visibility.",
                "LAYER",
                "Assign different colors and linetypes to five drawing layers.",
                "layer appearance and visibility",
            ),
            (
                "Object Properties",
                "Object properties include layer, color, linetype, lineweight and geometry information.",
                "PROPERTIES",
                "Select several objects and inspect and modify their properties.",
                "editing object characteristics",
            ),
            (
                "Linetypes and Lineweights",
                "Linetypes communicate drawing meaning while lineweights control plotted line thickness.",
                "LINETYPE / LWEIGHT",
                "Create continuous, dashed and center lines with appropriate lineweights.",
                "technical line representation",
            ),
            (
                "Layer Management",
                "Layer states such as On, Off, Freeze, Thaw, Lock and Unlock control editing and display.",
                "LAYER",
                "Practice freezing, locking and hiding selected layers.",
                "controlling layer display and editing",
            ),
        ],
    ),

    (
        6,
        "Hatching, Text and Annotation",
        "Add material patterns, labels and professional annotations to technical drawings.",
        [
            (
                "HATCH Fundamentals",
                "HATCH fills enclosed areas with patterns, solid fills or gradients.",
                "HATCH",
                "Create enclosed shapes and apply different hatch patterns.",
                "filling enclosed areas",
            ),
            (
                "Hatch Patterns and Scale",
                "Hatch pattern, angle and scale determine the appearance of material representation.",
                "HATCH",
                "Apply one hatch pattern using three different scale values.",
                "controlling hatch appearance",
            ),
            (
                "Single Line Text",
                "TEXT creates individual single-line text objects suitable for short labels.",
                "TEXT",
                "Add room names and short labels to a simple floor plan.",
                "short drawing labels",
            ),
            (
                "Multiline Text",
                "MTEXT creates paragraph-style text within a defined text boundary.",
                "MTEXT",
                "Create a multi-line project note with several lines of information.",
                "paragraph-style annotation",
            ),
            (
                "Text Styles and Annotation",
                "Text styles provide consistent font, height and appearance across a drawing.",
                "STYLE",
                "Create a text style and apply consistent annotation to a drawing.",
                "consistent text formatting",
            ),
        ],
    ),

    (
        7,
        "Dimensions",
        "Create and manage accurate dimensions for professional technical drawings.",
        [
            (
                "Dimension Fundamentals",
                "Dimensions communicate measurements such as distance, size, angle and radius.",
                "DIM",
                "Add basic dimensions to a rectangular mechanical component.",
                "communicating measurements",
            ),
            (
                "Linear and Aligned Dimensions",
                "Linear dimensions measure horizontal or vertical distances while aligned dimensions follow object direction.",
                "DIMLINEAR / DIMALIGNED",
                "Dimension horizontal, vertical and inclined lines.",
                "linear and aligned measurements",
            ),
            (
                "Angular, Radius and Diameter Dimensions",
                "Special dimension types communicate angles, radii and diameters.",
                "DIMANGULAR / DIMRADIUS / DIMDIAMETER",
                "Dimension an angle, a circle radius and a circle diameter.",
                "angles and circular measurements",
            ),
            (
                "Dimension Styles",
                "Dimension styles control arrows, text, units, scale and overall dimension appearance.",
                "DIMSTYLE",
                "Create a custom dimension style and apply it to a drawing.",
                "consistent dimension formatting",
            ),
            (
                "Dimension Editing and Best Practices",
                "Professional dimensioning requires clear placement, correct scale and readable annotation.",
                "DIM / PROPERTIES",
                "Clean up overlapping dimensions in a sample technical drawing.",
                "clear professional dimensioning",
            ),
        ],
    ),

    (
        8,
        "Blocks, Attributes and Tables",
        "Create reusable drawing components and structured drawing information.",
        [
            (
                "Creating Blocks",
                "A block combines selected objects into one reusable named object.",
                "BLOCK",
                "Create a reusable door or furniture block.",
                "reusable grouped objects",
            ),
            (
                "Inserting Blocks",
                "INSERT places a saved block using insertion point, scale and rotation settings.",
                "INSERT",
                "Insert multiple copies of a previously created block.",
                "placing reusable blocks",
            ),
            (
                "Block Attributes",
                "Attributes store editable text information inside block references.",
                "ATTDEF",
                "Create an equipment block containing ID and description attributes.",
                "data attached to blocks",
            ),
            (
                "Editing Blocks",
                "Block editing tools allow reusable definitions and references to be updated efficiently.",
                "BEDIT",
                "Modify a sample block and inspect how its definition changes.",
                "modifying block definitions",
            ),
            (
                "Tables",
                "TABLE creates structured rows and columns for schedules, lists and drawing information.",
                "TABLE",
                "Create a small door or equipment schedule using a table.",
                "structured drawing data",
            ),
        ],
    ),

    (
        9,
        "Isometric Drawing",
        "Create 2D representations that visually simulate three-dimensional objects.",
        [
            (
                "Isometric Drawing Fundamentals",
                "Isometric drafting represents three-dimensional forms using three principal axes.",
                "ISODRAFT",
                "Enable isometric drafting and draw a simple box.",
                "2D representation of 3D form",
            ),
            (
                "Isometric Snap and Isoplanes",
                "Isometric snap and Left, Top and Right isoplanes help align geometry correctly.",
                "ISODRAFT / F5",
                "Switch between isoplanes and draw edges on each plane.",
                "isometric plane control",
            ),
            (
                "Isometric Lines and Shapes",
                "Lines aligned to isometric axes can construct boxes, steps and technical forms.",
                "LINE",
                "Create an isometric stepped block using exact dimensions.",
                "isometric geometry",
            ),
            (
                "Isocircle",
                "ELLIPSE with the Isocircle option represents circles correctly on isometric planes.",
                "ELLIPSE / ISOCIRCLE",
                "Create isocircles on top, left and right isoplanes.",
                "isometric circles",
            ),
            (
                "Isometric Practical Drawing",
                "A complete isometric drawing combines accurate axes, edges, circles and dimensions.",
                "ISODRAFT",
                "Create a complete isometric mechanical component from given dimensions.",
                "complete isometric drafting",
            ),
        ],
    ),

    (
        10,
        "Layouts, Plotting and Practical Projects",
        "Prepare professional sheets, plotting output and real-world architectural and mechanical drawings.",
        [
            (
                "Layouts and Paper Space",
                "Layouts provide paper-space sheets for arranging drawing views before plotting.",
                "LAYOUT",
                "Create an A4 or A3 layout and prepare it for a drawing sheet.",
                "preparing drawing sheets",
            ),
            (
                "Viewports and Scale",
                "Viewports display model-space geometry inside layouts at controlled scales.",
                "MVIEW",
                "Create two viewports and assign different drawing scales.",
                "scaled model views on layouts",
            ),
            (
                "Plotting and Printing",
                "Plot settings control printer, paper size, plot area, orientation, scale and output style.",
                "PLOT",
                "Configure a drawing for PDF output using an appropriate paper size and scale.",
                "producing drawing output",
            ),
            (
                "Architectural Drawing Project",
                "Architectural drafting combines walls, openings, layers, annotations and dimensions into a floor plan.",
                "LINE / OFFSET / TRIM / DIM",
                "Create a small room or residential floor plan with walls, doors, windows and dimensions.",
                "architectural floor planning",
            ),
            (
                "Mechanical Drawing Project",
                "Mechanical drafting uses accurate geometry, circles, dimensions and technical conventions to represent components.",
                "LINE / CIRCLE / OFFSET / DIM",
                "Create a dimensioned 2D mechanical component drawing suitable for printing.",
                "mechanical technical drawing",
            ),
        ],
    ),
]


def build_notes(title, concept, command, practice):
    return f"""Overview:
{concept}

Key Command(s):
{command}

Learning Objectives:
• Understand the purpose of {title}.
• Identify where this tool is used in technical drawings.
• Apply the command accurately using AutoCAD.
• Use exact dimensions and appropriate drawing aids.
• Follow clean and professional drafting practices.

Practical Task:
{practice}

Practice Guidance:
Run the command from the Command Line, read each AutoCAD prompt carefully, complete the exercise using exact values, and inspect the finished geometry before saving your drawing."""


def questions_for(title, concept, command, key_answer):
    # Five topic-specific questions. Correct option deliberately varies.
    return [
        (
            f"What is the main purpose of {title}?",
            key_answer,
            "Managing email accounts",
            "Editing video footage",
            "Creating spreadsheets",
            "A",
        ),
        (
            f"Which AutoCAD command or command group is associated with {title}?",
            "PLOT only",
            command,
            "SAVEAS only",
            "HELP only",
            "B",
        ),
        (
            f"Which statement best describes {title}?",
            "It is used only for internet settings.",
            "It is unrelated to technical drawing.",
            concept,
            "It is used only to rename files.",
            "C",
        ),
        (
            f"Why should a learner practice {title} using exact values?",
            "To change the computer password",
            "To increase internet speed",
            "To install a printer",
            "To improve drafting accuracy",
            "D",
        ),
        (
            f"Which activity is most appropriate while learning {title}?",
            "Create and inspect relevant geometry in AutoCAD",
            "Prepare an accounting ledger",
            "Edit an audio recording",
            "Configure an email server",
            "A",
        ),
    ]


created_modules = 0
created_topics = 0
created_mcqs = 0

with transaction.atomic():

    for module_order, module_title, module_description, topics in MODULES:
        if module_order < 3:
            continue

        module = LMSModule.objects.create(
            course=course,
            title=module_title,
            description=module_description,
            order=module_order,
            is_active=True,
        )

        created_modules += 1

        if len(topics) != 5:
            raise RuntimeError(
                f"Module {module_order} does not contain exactly 5 topics."
            )

        for topic_order, data in enumerate(topics, start=1):

            title, concept, command, practice, key_answer = data

            topic = LMSTopic.objects.create(
                module=module,
                title=title,
                description=build_notes(
                    title,
                    concept,
                    command,
                    practice,
                ),
                order=topic_order,
                is_active=True,
            )

            created_topics += 1

            questions = questions_for(
                title,
                concept,
                command,
                key_answer,
            )

            if len(questions) != 5:
                raise RuntimeError(
                    f"{title} does not contain exactly 5 questions."
                )

            for q_order, q in enumerate(questions, start=1):

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

                created_mcqs += 1

    # --------------------------------------------------------
    # FINAL VERIFICATION INSIDE TRANSACTION
    # Any mismatch rolls back Modules 2–10.
    # --------------------------------------------------------

    final_modules = LMSModule.objects.filter(
        course=course
    ).count()

    final_topics = LMSTopic.objects.filter(
        module__course=course
    ).count()

    final_mcqs = QuizQuestion.objects.filter(
        topic__module__course=course
    ).count()

    if (
        final_modules != 10
        or final_topics != 50
        or final_mcqs != 250
    ):
        raise RuntimeError(
            "FINAL COUNT FAILED — transaction rolled back. "
            f"Found Modules={final_modules}, "
            f"Topics={final_topics}, "
            f"MCQs={final_mcqs}"
        )

print("")
print("========================================")
print("AUTOCAD LMS COMPLETE ✅")
print("========================================")
print("Course ID:", course.id)
print("Course:", course.title)
print("Added now:")
print("  Modules:", created_modules)
print("  Topics:", created_topics)
print("  MCQs:", created_mcqs)
print("----------------------------------------")
print("FINAL TOTAL")
print("Modules:", final_modules)
print("Topics:", final_topics)
print("MCQs:", final_mcqs)
print("Status: COMPLETE")
print("========================================")
