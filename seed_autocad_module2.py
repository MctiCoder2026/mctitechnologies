from django.db import transaction
from core.models import Course
from lms.models import LMSModule, LMSTopic, QuizQuestion

COURSE_ID = 37
EXPECTED_SLUG = "autocad"

course = Course.objects.get(id=COURSE_ID)

if course.slug != EXPECTED_SLUG:
    raise RuntimeError("Safety stop: Course ID 37 is not AutoCAD.")

if LMSModule.objects.filter(course=course, order=2).exists():
    raise RuntimeError(
        "Safety stop: AutoCAD Module 2 already exists. Nothing changed."
    )

DATA = [
    {
        "title": "LINE Command",
        "notes": """The LINE command creates individual straight line segments.

Key concepts:
• Start LINE by typing LINE or L.
• Specify the first point and then the next point.
• Each segment created with LINE is an independent object.
• Exact coordinates, Ortho Mode and Object Snap can improve accuracy.
• Press Enter or Esc to finish the command.

Practical Task:
Create a simple rectangular room outline using LINE. Enter exact dimensions and use Ortho Mode to keep horizontal and vertical lines straight.""",
        "questions": [
            ("Which command creates straight line segments?", "LINE", "CIRCLE", "ARC", "HATCH", "A"),
            ("What is a common shortcut for the LINE command?", "L", "LN", "LI", "LE", "A"),
            ("How are segments created by LINE normally treated?", "As individual objects", "As one automatic block", "As dimensions", "As layers", "A"),
            ("Which mode helps draw horizontal and vertical lines accurately?", "Ortho Mode", "Plot Mode", "Layout Mode", "Print Preview", "A"),
            ("Which key can finish the LINE command after drawing?", "Enter", "Caps Lock", "Num Lock", "Tab only", "A"),
        ],
    },
    {
        "title": "POLYLINE Command",
        "notes": """A polyline is a connected sequence of line or arc segments treated as one object.

Key concepts:
• Start with PLINE or PL.
• Multiple connected segments form a single polyline object.
• Polyline width can be controlled.
• Line and arc segments can exist within the same polyline.
• Polylines are useful for boundaries, paths and complex outlines.

Practical Task:
Create a closed irregular boundary using PLINE. Select the completed polyline and observe that the connected segments behave as one object.""",
        "questions": [
            ("Which command creates a polyline?", "PLINE", "POINT", "PAN", "PLOT", "A"),
            ("What is a common shortcut for PLINE?", "PL", "PN", "PE", "PI", "A"),
            ("How does a polyline differ from separate LINE segments?", "Connected segments can act as one object", "It cannot contain straight segments", "It is only used for text", "It cannot be edited", "A"),
            ("A polyline can contain which types of segments?", "Lines and arcs", "Images only", "Dimensions only", "Tables only", "A"),
            ("Which is a common use of a polyline?", "Creating connected boundaries", "Sending email", "Changing printer ink", "Creating spreadsheets", "A"),
        ],
    },
    {
        "title": "CIRCLE Command",
        "notes": """The CIRCLE command creates accurate circular objects.

Common methods include:
• Center and Radius
• Center and Diameter
• Two Point
• Three Point
• Tangent-Tangent-Radius in supported command options

The most common method is to specify the centre point followed by the radius.

Practical Task:
Create circles using Center-Radius and Center-Diameter methods. Make one circle with radius 25 units and another with diameter 100 units.""",
        "questions": [
            ("Which command creates a circle?", "CIRCLE", "RECTANGLE", "LINE", "TEXT", "A"),
            ("What information is used in the Center-Radius method?", "Center point and radius", "Two layers", "Text and height", "Width and color only", "A"),
            ("A circle with a diameter of 100 has what radius?", "50", "100", "200", "25", "A"),
            ("Which is a valid method for creating a circle?", "Three Point", "Four Layer", "Two Text", "Five Dimension", "A"),
            ("What is the diameter of a circle with radius 25?", "50", "25", "12.5", "100", "A"),
        ],
    },
    {
        "title": "ARC Command",
        "notes": """The ARC command creates a portion of a circle.

AutoCAD provides several methods for defining an arc. Depending on the method, you may specify:
• Start point
• Second point
• End point
• Center
• Radius
• Angle

Arcs are commonly used for curved boundaries, openings and mechanical profiles.

Practical Task:
Create several arcs using the 3-Point method. Then create an arc using a start point, center and end point and compare the results.""",
        "questions": [
            ("What does the ARC command create?", "A portion of a circle", "A complete spreadsheet", "A text paragraph", "A layer table", "A"),
            ("Which is a valid way to define an arc?", "Three points", "Three passwords", "Three layers only", "Three printers", "A"),
            ("Which value may be used when constructing an arc?", "Angle", "Email address", "Font file only", "Password", "A"),
            ("Where might an arc be useful?", "Curved technical geometry", "Database backup only", "Email formatting", "Audio editing", "A"),
            ("An arc is geometrically related to which object?", "Circle", "Table", "Text", "Layer", "A"),
        ],
    },
    {
        "title": "RECTANGLE and POLYGON Commands",
        "notes": """RECTANGLE and POLYGON are useful commands for creating regular shapes.

RECTANGLE:
• Creates a closed rectangular polyline.
• Normally defined using two opposite corners.
• Exact dimensions can be entered using command options or coordinates.

POLYGON:
• Creates a regular closed polygon.
• You specify the number of sides.
• It can be constructed using inscribed or circumscribed options.
• It is useful for triangles, pentagons, hexagons and other regular shapes.

Practical Task:
Create a rectangle 100 × 60 units. Then create a regular hexagon and experiment with both Inscribed in Circle and Circumscribed about Circle options.""",
        "questions": [
            ("What does the RECTANGLE command normally create?", "A closed rectangular polyline", "A circle", "A text style", "A dimension only", "A"),
            ("How many sides does a hexagon have?", "6", "5", "7", "8", "A"),
            ("Which command creates a regular multi-sided shape?", "POLYGON", "PAN", "ZOOM", "TEXT", "A"),
            ("Which is an available polygon construction concept?", "Inscribed in a circle", "Saved in a table", "Printed in a layer", "Stored in a dimension", "A"),
            ("A rectangle is commonly specified using what?", "Two opposite corners", "Two passwords", "Two printers", "Two text styles", "A"),
        ],
    },
]

with transaction.atomic():

    module = LMSModule.objects.create(
        course=course,
        title="Basic Drawing Commands",
        description=(
            "Create accurate AutoCAD geometry using Line, Polyline, "
            "Circle, Arc, Rectangle and Polygon commands."
        ),
        order=2,
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

print("AUTOCAD MODULE 2 CREATED ✅")

print(
    "Modules:",
    LMSModule.objects.filter(course=course).count()
)

print(
    "Topics:",
    LMSTopic.objects.filter(
        module__course=course
    ).count()
)

print(
    "MCQs:",
    QuizQuestion.objects.filter(
        topic__module__course=course
    ).count()
)
