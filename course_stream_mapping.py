from core.models import Course, Stream
from collections import defaultdict


# ============================================================
# MCTI COURSE -> STREAM MAPPING
# DRY RUN ONLY
# ============================================================

DRY_RUN = False

STREAM_NAMES = [
    "Arts",
    "Commerce",
    "Science",
    "Engineering",
    "IT/CS",
    "Other",
]


# ============================================================
# KEYWORD RULES
# A course can belong to multiple streams.
# ============================================================

RULES = {

    # ========================================================
    # ARTS
    # Creative, marketing, communication and general office
    # ========================================================

    "Arts": [
        "graphic design",
        "photoshop",
        "illustrator",
        "indesign",
        "premiere",
        "after effects",
        "lightroom",
        "coreldraw",
        "figma",
        "canva",
        "video editing",
        "motion graphics",
        "2d animation",
        "3d animation",
        "blender",
        "illustration",
        "character design",
        "brand identity",
        "ui/ux",
        "digital marketing",
        "seo",
        "google ads",
        "social media",
        "meta ads",
        "wordpress",
        "business communication",
        "professional english",
        "spoken english",
        "interview skills",
        "resume building",
        "soft skills",
        "office administration",
        "data entry",
        "computer operator",
        "back office",
        "typing",
    ],

    # ========================================================
    # COMMERCE
    # Accounts, finance, taxation, office, MIS and BI
    # ========================================================

    "Commerce": [
        "accounting",
        "account",
        "tally",
        "gst",
        "tax",
        "itr",
        "finance",
        "financial",
        "payroll",
        "sap fico",
        "advanced excel",
        "power query",
        "power pivot",
        "mis executive",
        "business analytics",
        "business intelligence",
        "power bi",
        "tableau",
        "qlik sense",
        "looker studio",
        "data visualization",
        "data analysis",
        "statistics for data analysis",
        "office administration",
        "data entry",
        "back office",
    ],

    # ========================================================
    # SCIENCE
    # Programming, data, AI and analytical technologies
    # Not every development/cloud course automatically matches.
    # ========================================================

    "Science": [
        "python",
        "c programming",
        "c++ programming",
        "c# programming",
        "r programming",
        "java development",
        "core java",
        "advanced java",
        "matlab",
        "data analysis",
        "data analytics",
        "data science",
        "business analytics",
        "statistics",
        "machine learning",
        "deep learning",
        "artificial intelligence",
        "generative ai",
        "natural language processing",
        "computer vision",
        "large language models",
        "llm",
        "ai automation",
        "ai agents",
        "ai api",
        "ai chatbot",
        "ai application",
        "power bi",
        "tableau",
        "data visualization",
        "big data",
        "hadoop",
        "apache spark",
        "snowflake",
        "databricks",
        "data engineering",
        "data warehousing",
    ],

    # ========================================================
    # ENGINEERING
    # Engineering design + selected technical/software skills
    # ========================================================

    "Engineering": [
        "autocad",
        "3ds max",
        "revit",
        "civil 3d",
        "civil",
        "mechanical",
        "electrical",
        "architecture",
        "architectural",
        "sketchup",
        "lumion",
        "v-ray",
        "navisworks",
        "bim",
        "staad",
        "etabs",
        "primavera",
        "ms project",
        "quantity surveying",
        "matlab",
        "python development",
        "java development",
        "c programming",
        "c++ programming",
        "data analysis",
        "data science",
        "machine learning",
        "artificial intelligence",
        "cloud computing",
        "cyber security",
        "devops",
        "computer hardware",
        "networking",
    ],

    # ========================================================
    # IT / COMPUTER SCIENCE
    # Programming, web/app, database, testing, cloud,
    # cyber security, DevOps, AI and data technologies.
    # ========================================================

    "IT/CS": [
        "programming",
        "development",
        "python",
        "java",
        "c++",
        "c#",
        "php",
        "kotlin",
        "swift",
        "golang",
        "rust",
        "dart",
        "typescript",
        "ruby",
        "scala",
        "perl",
        "html",
        "css",
        "javascript",
        "react",
        "angular",
        "vue",
        "node",
        "laravel",
        "asp.net",
        ".net",
        "django",
        "flask",
        "fastapi",
        "spring",
        "hibernate",
        "rest api",
        "android",
        "ios",
        "flutter",
        "mysql",
        "postgresql",
        "oracle database",
        "sql server",
        "mongodb",
        "sqlite",
        "redis",
        "pl/sql",
        "database",
        "software testing",
        "automation testing",
        "selenium",
        "api testing",
        "performance testing",
        "jmeter",
        "postman",
        "cypress",
        "playwright",
        "testng",
        "mobile app testing",
        "web application testing",
        "git",
        "github",
        "gitlab",
        "docker",
        "kubernetes",
        "jenkins",
        "maven",
        "gradle",
        "jira",
        "ci/cd",
        "microservices",
        "cloud",
        "linux",
        "windows server",
        "active directory",
        "virtualization",
        "vmware",
        "terraform",
        "ansible",
        "cyber",
        "security",
        "network",
        "ethical hacking",
        "penetration testing",
        "digital forensics",
        "soc analyst",
        "bug bounty",
        "kali linux",
        "incident response",
        "machine learning",
        "deep learning",
        "natural language processing",
        "computer vision",
        "artificial intelligence",
        "generative ai",
        "ai automation",
        "ai agents",
        "llm",
        "langchain",
        "chatbot",
        "data science",
        "data engineering",
        "big data",
        "hadoop",
        "apache spark",
        "snowflake",
        "databricks",
        "dbt",
        "data warehousing",
        "power bi",
    ],

    # ========================================================
    # OTHER
    # General employability / office / communication
    # ========================================================

    "Other": [
        "spoken english",
        "professional english",
        "business communication",
        "interview skills",
        "resume building",
        "corporate soft skills",
        "office administration",
        "data entry",
        "computer operator",
        "back office",
        "english typing",
    ],
}

    


# ============================================================
# SPECIAL / BROAD COURSES
#
# These courses are useful across multiple educational
# backgrounds and should not depend only on keyword matching.
# ============================================================

BROAD_RULES = {

    "Advanced Excel": [
        "Arts",
        "Commerce",
        "Science",
        "Engineering",
        "IT/CS",
        "Other",
    ],

    "Advanced MS Office": [
        "Arts",
        "Commerce",
        "Science",
        "Engineering",
        "IT/CS",
        "Other",
    ],

    "ONLINE MS OFFICE": [
        "Arts",
        "Commerce",
        "Science",
        "Engineering",
        "IT/CS",
        "Other",
    ],

    "AI Tools & ChatGPT for Office Productivity": [
        "Arts",
        "Commerce",
        "Science",
        "Engineering",
        "IT/CS",
        "Other",
    ],

    "Digital Marketing with AI": [
        "Arts",
        "Commerce",
        "Science",
        "Engineering",
        "IT/CS",
        "Other",
    ],

    "Digital Marketing": [
        "Arts",
        "Commerce",
        "Science",
        "Other",
    ],

    "Data Analysis with AI": [
        "Commerce",
        "Science",
        "Engineering",
        "IT/CS",
    ],

    "Business Analytics with AI": [
        "Commerce",
        "Science",
        "Engineering",
        "IT/CS",
    ],

    "Power BI": [
        "Commerce",
        "Science",
        "Engineering",
        "IT/CS",
    ],

    "Tally Prime with GST": [
        "Commerce",
        "Other",
    ],

    "MIA – Master in Accounting": [
        "Commerce",
        "Other",
    ],

    "DFA – Diploma in Financial Accounting": [
        "Commerce",
        "Other",
    ],

    "Graphic Design": [
        "Arts",
        "Commerce",
        "Science",
        "Other",
    ],

    "Video Editing": [
        "Arts",
        "Commerce",
        "Science",
        "Other",
    ],

    "UI/UX Design": [
        "Arts",
        "Science",
        "Engineering",
        "IT/CS",
        "Other",
    ],

    "Cyber Security & Ethical Hacking": [
        "Science",
        "Engineering",
        "IT/CS",
    ],

    "Cloud Computing": [
        "Science",
        "Engineering",
        "IT/CS",
    ],
}


# ============================================================
# LOAD STREAMS
# ============================================================

streams = {
    stream.name: stream
    for stream in Stream.objects.filter(
        name__in=STREAM_NAMES
    )
}

missing_streams = [
    name
    for name in STREAM_NAMES
    if name not in streams
]

if missing_streams:

    print(
        "ERROR - Missing Streams:",
        ", ".join(missing_streams)
    )

    raise SystemExit


# ============================================================
# DETERMINE STREAMS
# ============================================================

def determine_streams(course):

    title = course.title.lower()
    category = (course.category or "").lower()

    searchable = f" {title} {category} "

    matched = set()

    # ----------------------------------------
    # Explicit broad/special mappings first
    # ----------------------------------------

    for special_title, special_streams in BROAD_RULES.items():

        if course.title.casefold() == special_title.casefold():

            matched.update(
                special_streams
            )

    # ----------------------------------------
    # Keyword matching
    # ----------------------------------------

    for stream_name, keywords in RULES.items():

        for keyword in keywords:

            if keyword.lower() in searchable:

                matched.add(
                    stream_name
                )

                break

    # ----------------------------------------
    # If nothing matches, keep visible in Other
    # ----------------------------------------

    if not matched:

        matched.add("Other")

    return sorted(
        matched,
        key=lambda x: STREAM_NAMES.index(x)
    )


# ============================================================
# DRY RUN
# ============================================================

courses = Course.objects.filter(
    is_active=True
).order_by(
    "id"
)

report = defaultdict(list)
course_results = []

print()
print("=" * 90)
print("MCTI COURSE STREAM MAPPING - DRY RUN")
print("=" * 90)
print()

for course in courses:

    matched_streams = determine_streams(
        course
    )

    course_results.append(
        (
            course,
            matched_streams,
        )
    )

    for stream_name in matched_streams:

        report[stream_name].append(
            course.title
        )

    # --------------------------------------------------------
    # SAVE STREAM ASSIGNMENTS
    # --------------------------------------------------------

    if not DRY_RUN:

        course.streams.set(
            [
                streams[stream_name]
                for stream_name in matched_streams
            ]
        )

    print(
        f"{course.id:>3} | "
        f"{course.title:<45} | "
        f"{', '.join(matched_streams)}"
    )

# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 90)
print("STREAM SUMMARY")
print("=" * 90)

for stream_name in STREAM_NAMES:

    print(
        f"{stream_name:<15}: "
        f"{len(report[stream_name])}"
    )


unmapped = [
    course.title
    for course, matched in course_results
    if not matched
]

print()
print("TOTAL ACTIVE COURSES :", courses.count())
print("UNMAPPED COURSES     :", len(unmapped))
if DRY_RUN:
    print("DATABASE CHANGES     : 0")
else:
    print(
        "COURSES MAPPED       :",
        len(course_results)
    )

print("=" * 90)

if DRY_RUN:

    print(
        "DRY RUN COMPLETE - NO STREAM ASSIGNMENTS WERE SAVED"
    )

else:

    print(
        "STREAM MAPPING SAVED SUCCESSFULLY"
    )

print("=" * 90)