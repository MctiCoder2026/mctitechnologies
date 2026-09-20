from core.models import Course
from django.utils.text import slugify
from django.db import transaction


# ============================================================
# MCTI COURSE CATALOG - SAFE BULK IMPORT
# Existing courses are NEVER updated.
# ============================================================

COURSES = {

    "Programming Languages": [
        "C# Programming",
        "R Programming",
        "PHP Programming",
        "Kotlin Programming",
        "Swift Programming",
        "Go (Golang)",
        "Rust Programming",
        "Dart Programming",
        "TypeScript Programming",
        "Ruby Programming",
        "Scala Programming",
        "MATLAB Programming",
        "Visual Basic / VB.NET",
        "Perl Programming",
    ],

    "Web Development": [
        "Front-End Web Development",
        "Back-End Web Development",
        "React JS Development",
        "Angular Development",
        "Vue JS Development",
        "Node JS Development",
        "PHP Web Development",
        "Laravel Development",
        "ASP.NET Development",
        ".NET Development",

        # Django Development removed
        # Keep Django with Python

        # Flask Development removed
        # Keep Flask with Python

        # FastAPI Development removed
        # Keep FastAPI with Python

        # Spring Boot Development removed
        # Keep Spring Boot

        "REST API Development",
        "Web Application Development",
        "E-Commerce Website Development",
        "Responsive Web Design",
        "Bootstrap Development",
        "Tailwind CSS",
    ],

    "Mobile App Development": [
        "Android App Development",
        "iOS App Development",
        "Flutter App Development",
        "React Native Development",
        "Cross-Platform App Development",
        "Kotlin Android Development",
        "Swift iOS Development",
    ],

    "Advanced Java": [
        "Core Java",
        "Advanced Java",
        "Java EE / Jakarta EE",
        "Spring Framework",
        "Spring Boot",
        "Hibernate",
        "Java Microservices",
        "Java Backend Development",
    ],

    "Advanced Python": [
        "Core Python",
        "Advanced Python",
        "Django with Python",
        "Flask with Python",
        "FastAPI with Python",
        "Python Automation",
        "Python API Development",
        "Python Backend Development",
    ],

    "Database & Data Technologies": [
        "MySQL Database",
        "PostgreSQL",
        "Oracle Database",
        "Microsoft SQL Server",
        "MongoDB",
        "SQLite",
        "Redis",

        # PL/SQL removed
        # Keep Oracle PL/SQL

        "Oracle PL/SQL",
        "Database Administration",
        "Database Design & Management",
    ],

    "Software Testing": [
        "Selenium Automation Testing",
        "Automation Testing with Java",
        "Automation Testing with Python",
        "API Testing",
        "Performance Testing",
        "JMeter",
        "Postman API Testing",
        "Cypress Testing",
        "Playwright Testing",
        "TestNG",
        "Mobile App Testing",
        "Web Application Testing",
    ],

    "Software Development Tools": [
        "Git & GitHub",
        "GitLab",
        "Docker",
        "Kubernetes",
        "Jenkins",
        "Maven",
        "Gradle",
        "Jira for Software Development",
        "CI/CD Pipeline",
        "Microservices Architecture",
    ],

    "Cloud & Infrastructure": [
        "Google Cloud Platform (GCP)",
        "Microsoft 365 Administration",
        "Windows Server Administration",

        # Linux Server Administration removed
        # Existing Linux Administration already present

        "Active Directory",
        "Virtualization",
        "VMware",
        "Cloud Security",
        "Cloud Administration",
        "Infrastructure as Code",
        "Terraform",
        "Ansible",
    ],

    "Cyber Security": [
        "Cyber Security Fundamentals",
        "Network Security",
        "Web Application Security",
        "Penetration Testing",
        "Digital Forensics",
        "SOC Analyst",
        "Bug Bounty",
        "Kali Linux",
        "CompTIA Security+ Preparation",
        "Cyber Security Analyst",
        "Incident Response",
    ],

    "Advanced AI": [
        "Machine Learning with Python",
        "Deep Learning",
        "Natural Language Processing (NLP)",
        "Computer Vision",
        "AI Automation",
        "AI Agents",
        "Large Language Models (LLM)",
        "LLM Application Development",
        "AI API Integration",
        "LangChain",
        "AI Chatbot Development",
        "AI Application Development",
    ],

    "Advanced Data & BI": [
        "Tableau",
        "Qlik Sense",
        "Looker Studio",
        "Data Visualization",
        "Business Intelligence",
        "Data Engineering",
        "Big Data Analytics",
        "Hadoop",
        "Apache Spark",
        "Snowflake",
        "Databricks",
        "Statistics for Data Analysis",
        "dbt",
        "Data Warehousing",
    ],

    "Graphic & Creative": [
        "Adobe InDesign",
        "Adobe Premiere Pro",
        "Adobe After Effects",
        "Adobe Lightroom",
        "CorelDRAW",
        "Figma",
        "Motion Graphics",
        "2D Animation",
        "3D Animation",
        "Blender",
        "Logo & Brand Identity Design",
        "Digital Illustration",
        "Character Design",
    ],

    "Architecture / Civil / Engineering": [
        "AutoCAD Mechanical",
        "AutoCAD Electrical",
        "Civil 3D",
        "SketchUp",
        "Lumion",
        "V-Ray",
        "Navisworks",
        "BIM",
        "Revit MEP",
        "Revit Structure",
        "STAAD.Pro",
        "ETABS",
        "Primavera P6",
        "MS Project",
        "Quantity Surveying",
        "Architectural Visualization",
    ],

    "Business & Professional Skills": [
        "GST Practitioner",
        "Income Tax & ITR Filing",
        "Payroll Management",
        "Accounts & Finance Executive",
        "MIS Executive",
        "Business Communication",
        "Professional English",
        "Spoken English",
        "Interview Skills",
        "Resume Building",
        "Corporate Soft Skills",
        "Office Administration",
        "Data Entry Operator",
        "Computer Operator",
        "Back Office Executive",
    ],
}


# ============================================================
# CATEGORY DEFAULT DURATIONS
# These can be changed later from Admin.
# ============================================================

DURATIONS = {
    "Programming Languages": "2 Months",
    "Web Development": "2 Months",
    "Mobile App Development": "3 Months",
    "Advanced Java": "2 Months",
    "Advanced Python": "2 Months",
    "Database & Data Technologies": "2 Months",
    "Software Testing": "2 Months",
    "Software Development Tools": "1 Month",
    "Cloud & Infrastructure": "2 Months",
    "Cyber Security": "2 Months",
    "Advanced AI": "2 Months",
    "Advanced Data & BI": "2 Months",
    "Graphic & Creative": "2 Months",
    "Architecture / Civil / Engineering": "2 Months",
    "Business & Professional Skills": "1 Month",
}


# ============================================================
# SHORT DESCRIPTION GENERATOR
# Initial website/catalog description.
# Can be customized later from Admin.
# ============================================================

def make_description(title, category):

    descriptions = {

        "Programming Languages":
            f"Learn {title} from fundamentals to practical programming "
            f"with hands-on exercises and real-world applications.",

        "Web Development":
            f"Learn {title} with practical projects, modern development "
            f"techniques and industry-relevant web development skills.",

        "Mobile App Development":
            f"Build practical mobile application development skills with "
            f"{title}, hands-on exercises and project-based learning.",

        "Advanced Java":
            f"Develop professional Java development skills through "
            f"{title}, practical coding and application-based learning.",

        "Advanced Python":
            f"Build advanced Python development skills with {title}, "
            f"practical programming and real-world projects.",

        "Database & Data Technologies":
            f"Learn {title} with practical database concepts, data "
            f"management techniques and hands-on exercises.",

        "Software Testing":
            f"Learn {title} through practical software testing methods, "
            f"tools and industry-oriented exercises.",

        "Software Development Tools":
            f"Learn {title} with practical software development workflows, "
            f"tools and industry-relevant implementation.",

        "Cloud & Infrastructure":
            f"Develop practical cloud and infrastructure skills with "
            f"{title} through hands-on administration and implementation.",

        "Cyber Security":
            f"Learn {title} with practical cyber security concepts, "
            f"industry tools and hands-on security exercises.",

        "Advanced AI":
            f"Learn {title} through practical AI concepts, tools, "
            f"applications and project-based learning.",

        "Advanced Data & BI":
            f"Develop professional data and business intelligence skills "
            f"with {title}, practical exercises and projects.",

        "Graphic & Creative":
            f"Build creative and professional design skills with {title} "
            f"through practical exercises and portfolio-oriented projects.",

        "Architecture / Civil / Engineering":
            f"Learn {title} through practical engineering, design and "
            f"industry-oriented project exercises.",

        "Business & Professional Skills":
            f"Develop job-ready professional skills with {title} through "
            f"practical exercises and workplace-oriented learning.",
    }

    return descriptions.get(
        category,
        f"Learn {title} through practical and industry-oriented training."
    )


# ============================================================
# UNIQUE SLUG
# ============================================================

def generate_unique_slug(title):

    base_slug = slugify(title)
    slug = base_slug
    counter = 2

    while Course.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


# ============================================================
# PRE-IMPORT INFORMATION
# ============================================================

requested_count = sum(
    len(titles)
    for titles in COURSES.values()
)

before_count = Course.objects.count()

print()
print("=" * 75)
print("MCTI COURSE CATALOG - SAFE IMPORT")
print("=" * 75)

print("Courses currently in database :", before_count)
print("Courses requested for import  :", requested_count)
print()


# ============================================================
# IMPORT
# ============================================================

created_courses = []
skipped_courses = []


with transaction.atomic():

    for category, titles in COURSES.items():

        for title in titles:

            # ------------------------------------------------
            # Case-insensitive title protection.
            # Existing records are NEVER modified.
            # ------------------------------------------------

            existing = Course.objects.filter(
                title__iexact=title
            ).first()

            if existing:

                skipped_courses.append(
                    (
                        title,
                        existing.id,
                        existing.title,
                    )
                )

                print(
                    f"SKIPPED | {title}"
                    f" | Existing ID: {existing.id}"
                )

                continue

            # ------------------------------------------------
            # Generate slug before creation.
            # ------------------------------------------------

            unique_slug = generate_unique_slug(title)

            # ------------------------------------------------
            # CREATE NEW COURSE ONLY
            # ------------------------------------------------

            course, created = Course.objects.get_or_create(

                title=title,

                defaults={
                    "slug": unique_slug,
                    "short_description": make_description(
                        title,
                        category,
                    ),
                    "duration": DURATIONS.get(
                        category,
                        "2 Months",
                    ),
                    "fee": None,
                    "category": category,
                    "icon": "📚",
                    "is_active": True,
                    "is_package": False,
                }
            )

            if created:

                created_courses.append(
                    (
                        course.id,
                        course.title,
                        course.category,
                    )
                )

                print(
                    f"CREATED | ID {course.id}"
                    f" | {course.title}"
                    f" | {course.category}"
                )

            else:

                skipped_courses.append(
                    (
                        title,
                        course.id,
                        course.title,
                    )
                )

                print(
                    f"SKIPPED | {title}"
                    f" | Existing ID: {course.id}"
                )


# ============================================================
# FINAL REPORT
# ============================================================

after_count = Course.objects.count()

print()
print("=" * 75)
print("IMPORT SUMMARY")
print("=" * 75)

print(
    "Courses Before :",
    before_count
)

print(
    "Requested      :",
    requested_count
)

print(
    "Created        :",
    len(created_courses)
)

print(
    "Skipped        :",
    len(skipped_courses)
)

print(
    "Courses After  :",
    after_count
)

print("=" * 75)

if after_count == before_count + len(created_courses):

    print("COUNT CHECK     : PASS")

else:

    print("COUNT CHECK     : REVIEW REQUIRED")

print("=" * 75)
print("IMPORT COMPLETE")
print("=" * 75)