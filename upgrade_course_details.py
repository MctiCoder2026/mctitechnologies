import os
import re
from pathlib import Path

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

import django
django.setup()

from core.models import Course


# ============================================================
# COURSE CONTENT PROFILES
# ============================================================

PROFILES = {

    "programming": {
        "keywords": [
            "python", "java", "javascript", "typescript",
            "c programming", "c++", "php", "ruby",
            "kotlin", "swift", "golang", "rust"
        ],
        "eligibility":
            "Students, graduates, job seekers, working professionals "
            "and beginners interested in programming and software development.",

        "benefits":
            "Programming Fundamentals, Practical Coding Skills, "
            "Problem Solving, Logic Building, Hands-on Exercises, "
            "Mini Projects, Interview Preparation and Certificate.",

        "syllabus":
            "Programming Fundamentals, Variables & Data Types, "
            "Operators, Conditions, Loops, Functions, Arrays & Collections, "
            "Object-Oriented Concepts, Error Handling, File Handling, "
            "Practical Coding Exercises, Mini Projects and Final Project."
    },


    "web": {
        "keywords": [
            "html", "css", "react", "angular", "vue",
            "node", "express", "django", "flask",
            "fastapi", "web development", "full stack",
            "mern", "wordpress", "spring boot"
        ],
        "eligibility":
            "Students, graduates, job seekers, freelancers and beginners "
            "interested in website and web application development.",

        "benefits":
            "Website Development Skills, Responsive Design, "
            "Frontend & Backend Concepts, Database Integration, "
            "Practical Projects, Portfolio Development, "
            "Deployment Knowledge and Certificate.",

        "syllabus":
            "Web Development Fundamentals, User Interface Basics, "
            "Responsive Design, Programming Concepts, Forms & Validation, "
            "Database Integration, APIs, Authentication, "
            "Version Control, Deployment, Practical Projects "
            "and Portfolio Development."
    },


    "data": {
        "keywords": [
            "data", "power bi", "tableau", "sql",
            "database", "analytics", "excel",
            "business intelligence", "power query"
        ],
        "eligibility":
            "Students, graduates, working professionals, analysts, "
            "accounting professionals and job seekers interested in "
            "data analysis and reporting.",

        "benefits":
            "Data Analysis Skills, Data Cleaning, Reporting, "
            "Dashboard Development, Business Insights, "
            "Practical Projects, MIS Skills and Certificate.",

        "syllabus":
            "Data Fundamentals, Data Collection, Data Cleaning, "
            "Data Transformation, Formulas & Analysis, "
            "Database Concepts, Visualization, Dashboard Development, "
            "Business Reporting, Practical Case Studies "
            "and Final Project."
    },


    "ai": {
        "keywords": [
            "artificial intelligence", "machine learning",
            "generative ai", "prompt engineering",
            "chatgpt", "deep learning", "nlp",
            "computer vision", " ai "
        ],
        "eligibility":
            "Students, graduates, developers, professionals, entrepreneurs "
            "and beginners interested in Artificial Intelligence "
            "and modern AI tools.",

        "benefits":
            "AI Fundamentals, Practical AI Tools, Automation Skills, "
            "Prompt Engineering, Real-world Applications, "
            "AI Projects, Productivity Improvement and Certificate.",

        "syllabus":
            "Artificial Intelligence Fundamentals, AI Tools, "
            "Prompt Engineering, Data & AI Concepts, "
            "Machine Learning Basics, Generative AI, "
            "Automation Use Cases, Responsible AI, "
            "Practical Projects and Real-world Applications."
    },


    "design": {
        "keywords": [
            "photoshop", "illustrator", "graphic",
            "canva", "ui/ux", "figma",
            "video editing", "premiere", "after effects"
        ],
        "eligibility":
            "Students, designers, job seekers, digital marketers, "
            "freelancers, content creators and beginners interested "
            "in creative design.",

        "benefits":
            "Professional Designing Skills, Creative Tools, "
            "Digital & Social Media Creatives, Practical Projects, "
            "Portfolio Development, Freelancing Skills and Certificate.",

        "syllabus":
            "Design Fundamentals, Interface & Tools, "
            "Typography, Colors, Layout & Composition, "
            "Digital Creatives, Social Media Design, "
            "Branding Concepts, Practical Design Projects, "
            "Portfolio Development and Export Techniques."
    },


    "accounting": {
        "keywords": [
            "tally", "account", "gst", "tax",
            "finance", "financial", "sap fico",
            "payroll"
        ],
        "eligibility":
            "Commerce students, graduates, accountants, business owners, "
            "job seekers and professionals interested in accounting, "
            "taxation and finance.",

        "benefits":
            "Practical Accounting Skills, GST & Taxation Knowledge, "
            "Business Transactions, Financial Reporting, "
            "Job-oriented Practice, Real-world Exercises and Certificate.",

        "syllabus":
            "Accounting Fundamentals, Company & Ledger Management, "
            "Business Transactions, Purchase & Sales, Banking, "
            "GST & Taxation Concepts, Inventory, Payroll Basics, "
            "Financial Reports, Practical Assignments and Final Project."
    },


    "cloud": {
        "keywords": [
            "aws", "azure", "cloud", "devops",
            "linux", "docker", "kubernetes",
            "server", "network", "ccna"
        ],
        "eligibility":
            "IT students, graduates, system administrators, developers, "
            "job seekers and professionals interested in cloud, "
            "networking and infrastructure.",

        "benefits":
            "Infrastructure Skills, Cloud Concepts, Server Management, "
            "Networking Knowledge, Deployment Skills, "
            "Practical Labs, Industry-oriented Practice and Certificate.",

        "syllabus":
            "IT Infrastructure Fundamentals, Networking Basics, "
            "Operating Systems, Server Administration, "
            "Cloud Concepts, Security Basics, Deployment, "
            "Monitoring, Practical Labs, Troubleshooting "
            "and Real-world Projects."
    },


    "cyber": {
        "keywords": [
            "cyber", "ethical hacking", "security",
            "penetration", "forensic"
        ],
        "eligibility":
            "IT students, graduates, networking professionals, "
            "system administrators and job seekers interested "
            "in cyber security.",

        "benefits":
            "Cyber Security Fundamentals, Security Awareness, "
            "Network Security, Ethical Security Testing Concepts, "
            "Practical Labs, Risk Assessment and Certificate.",

        "syllabus":
            "Cyber Security Fundamentals, Networking & Security, "
            "Operating System Security, Web Security Concepts, "
            "Threats & Vulnerabilities, Ethical Security Testing, "
            "Security Tools, Risk Management, Practical Labs "
            "and Security Projects."
    },


    "cad": {
        "keywords": [
            "autocad", "revit", "3ds max",
            "civil", "architecture", "interior",
            "solidworks", "catia", "mechanical"
        ],
        "eligibility":
            "Engineering students, diploma students, architects, "
            "interior designers, professionals and job seekers "
            "interested in CAD and technical design.",

        "benefits":
            "Technical Drawing Skills, CAD Tools, "
            "2D/3D Design Concepts, Practical Drafting, "
            "Industry-oriented Projects, Portfolio Development "
            "and Certificate.",

        "syllabus":
            "Design & Drafting Fundamentals, Interface & Tools, "
            "Drawing Commands, Editing Tools, Layers, "
            "Dimensions & Annotation, 2D Design, 3D Concepts, "
            "Layouts & Printing, Practical Drawings "
            "and Industry Projects."
    },


    "business": {
        "keywords": [
            "business", "communication", "spoken english",
            "interview", "resume", "office administration",
            "data entry", "computer operator",
            "soft skills", "professional english"
        ],
        "eligibility":
            "Students, graduates, job seekers, working professionals "
            "and beginners who want to improve workplace "
            "and professional skills.",

        "benefits":
            "Professional Skills, Workplace Communication, "
            "Practical Office Skills, Interview Preparation, "
            "Career Readiness, Confidence Building and Certificate.",

        "syllabus":
            "Professional Fundamentals, Workplace Communication, "
            "Office Skills, Practical Exercises, "
            "Resume & Interview Preparation, Productivity Skills, "
            "Professional Etiquette, Career Readiness "
            "and Practical Assignments."
    }
}


# ============================================================
# DEFAULT PROFILE
# ============================================================

DEFAULT_PROFILE = {

    "eligibility":
        "Students, graduates, job seekers, working professionals "
        "and beginners interested in developing practical "
        "career-oriented skills.",

    "benefits":
        "Practical Skills, Industry-oriented Learning, "
        "Hands-on Exercises, Career-focused Training, "
        "Practical Projects, Skill Development "
        "and Course Certificate.",

    "syllabus":
        "Course Fundamentals, Core Concepts, Essential Tools, "
        "Practical Exercises, Industry Applications, "
        "Best Practices, Hands-on Assignments, "
        "Practical Projects and Career Preparation."
}


# ============================================================
# SELECT PROFILE
# ============================================================

def get_profile(course):

    searchable = (
        f" {course.title} {course.category} "
    ).lower()

    for profile in PROFILES.values():

        if any(
            keyword in searchable
            for keyword in profile["keywords"]
        ):
            return profile

    return DEFAULT_PROFILE


# ============================================================
# UPDATE ONLY MISSING COURSE DETAILS
# ============================================================

updated = 0
unchanged = 0

for course in Course.objects.filter(is_active=True):

    profile = get_profile(course)

    changed = False


    if not (course.eligibility or "").strip():

        course.eligibility = profile["eligibility"]
        changed = True


    if not (course.benefits or "").strip():

        course.benefits = profile["benefits"]
        changed = True


    if not (course.syllabus or "").strip():

        course.syllabus = (
            f"{course.title} Overview, "
            + profile["syllabus"]
        )

        changed = True


    if changed:

        course.save(
            update_fields=[
                "eligibility",
                "benefits",
                "syllabus",
            ]
        )

        updated += 1

    else:
        unchanged += 1


# ============================================================
# PATCH COURSE DETAIL CTA -> WHATSAPP
# ============================================================

template_path = Path(
    "templates/course-detail.html"
)

template = template_path.read_text(
    encoding="utf-8"
)


whatsapp_href = (
    'href="https://wa.me/918655556219'
    '?text=Hello%20MCTI%20Technologies%2C'
    '%20I%20am%20interested%20in%20'
    '{{ course.title|urlencode }}'
    '%20course.%20Please%20share%20fees%2C'
    '%20batch%20timings%20and%20admission%20details."'
    ' target="_blank" rel="noopener"'
)


# Replace anchors whose visible text contains
# Enquire Now or Talk to MCTI.
pattern = re.compile(
    r'<a\b([^>]*)href="[^"]*"([^>]*)>'
    r'(\s*(?:Enquire Now|Talk to MCTI).*?)'
    r'</a>',
    re.IGNORECASE | re.DOTALL
)


def replace_cta(match):

    before = match.group(1)
    after = match.group(2)
    label = match.group(3)

    attrs = (before + after)

    # Remove any duplicate target/rel
    attrs = re.sub(
        r'\s+target="[^"]*"',
        '',
        attrs,
        flags=re.IGNORECASE
    )

    attrs = re.sub(
        r'\s+rel="[^"]*"',
        '',
        attrs,
        flags=re.IGNORECASE
    )

    return (
        "<a "
        + attrs.strip()
        + " "
        + whatsapp_href
        + ">"
        + label
        + "</a>"
    )


patched_template, cta_count = pattern.subn(
    replace_cta,
    template
)


template_path.write_text(
    patched_template,
    encoding="utf-8"
)


# ============================================================
# RESULT
# ============================================================

print()
print("============================================")
print("MCTI COURSE DETAIL UPGRADE COMPLETE")
print("============================================")
print()
print("Total Active Courses :", Course.objects.filter(is_active=True).count())
print("Courses Updated      :", updated)
print("Already Complete     :", unchanged)
print("WhatsApp CTAs Patched:", cta_count)
print()
print("Existing detailed course content was NOT overwritten.")
print("WhatsApp Number: 8655556219")
print()