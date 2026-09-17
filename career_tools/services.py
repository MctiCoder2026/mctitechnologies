from core.models import Course


COURSE_RULES = [
    {
        "keywords": [
            "commerce", "account", "finance", "banking",
            "gst", "tax", "tally",
        ],
        "titles": [
            "MIA – Master in Accounting",
            "Tally Prime with GST",
            "Advanced Excel",
            "SAP FICO",
            "DFA – Diploma in Financial Accounting",
        ],
        "reason": (
            "Suitable for accounting, finance, taxation "
            "and office-based career opportunities."
        ),
    },
    {
        "keywords": [
            "coding", "programming", "software", "developer",
            "it_cs", "computer science", "web",
        ],
        "titles": [
            "Full Stack Development",
            "Python Development",
            "Java Development",
            "C & C++ Programming",
            "MERN Stack Development",
        ],
        "reason": (
            "Suitable for software development, programming "
            "and technology careers."
        ),
    },
    {
        "keywords": [
            "data", "analytics", "analyst", "power bi",
            "excel", "science",
        ],
        "titles": [
            "Data Analysis with AI",
            "Power BI",
            "Advanced Excel",
            "Python for Data Analysis",
            "Data Science with AI",
        ],
        "reason": (
            "Suitable for data analysis, reporting "
            "and business intelligence roles."
        ),
    },
    {
        "keywords": [
            "marketing", "social media", "seo",
            "advertising", "business promotion",
        ],
        "titles": [
            "Digital Marketing with AI",
            "Social Media Marketing & Meta Ads",
            "SEO & Google Ads",
            "Canva & Social Media Designing",
        ],
        "reason": (
            "Suitable for digital marketing, advertising "
            "and online business growth roles."
        ),
    },
    {
        "keywords": [
            "design", "creative", "graphics", "video",
            "ui", "ux", "arts",
        ],
        "titles": [
            "Graphic Design",
            "UI/UX Design",
            "Video Editing",
            "Canva & Social Media Designing",
        ],
        "reason": (
            "Suitable for creative, visual communication "
            "and digital design careers."
        ),
    },
    {
        "keywords": [
            "civil", "architecture", "interior",
            "mechanical", "autocad", "engineering",
        ],
        "titles": [
            "AutoCAD",
            "Revit Architecture",
            "3ds Max",
            "Interior Design with AutoCAD & 3ds Max",
        ],
        "reason": (
            "Suitable for technical drawing, architecture "
            "and design-related careers."
        ),
    },
    {
        "keywords": [
            "hardware", "network", "networking",
            "cloud", "linux", "cyber",
        ],
        "titles": [
            "Computer Hardware & Networking",
            "CCNA – Networking",
            "Linux Administration",
            "Cyber Security & Ethical Hacking",
            "AWS Cloud Computing",
        ],
        "reason": (
            "Suitable for IT infrastructure, networking "
            "and system-support careers."
        ),
    },
    {
        "keywords": [
            "office", "admin", "back office",
            "computer basics", "ms office",
        ],
        "titles": [
            "Advanced MS Office",
            "Advanced Excel",
            "AI Tools & ChatGPT for Office Productivity",
        ],
        "reason": (
            "Suitable for office administration, computer "
            "operations and productivity-based job roles."
        ),
    },
]


DEFAULT_COURSES = [
    "Advanced MS Office",
    "Advanced Excel",
    "AI Tools & ChatGPT for Office Productivity",
]


def get_course_suggestions(profile, limit=3):
    search_text = " ".join(
        [
            profile.stream or "",
            profile.highest_qualification or "",
            profile.career_interest or "",
            profile.preferred_job_role or "",
            profile.skills or "",
            profile.current_status or "",
        ]
    ).casefold()

    ranked = []

    for rule in COURSE_RULES:
        if any(
            keyword.casefold() in search_text
            for keyword in rule["keywords"]
        ):
            for title in rule["titles"]:
                ranked.append(
                    {
                        "title": title,
                        "reason": rule["reason"],
                    }
                )

    for title in DEFAULT_COURSES:
        ranked.append(
            {
                "title": title,
                "reason": (
                    "Builds essential digital and workplace skills "
                    "required across multiple industries."
                ),
            }
        )

    active_courses = {
        course.title.casefold(): course
        for course in Course.objects.filter(is_active=True)
    }

    suggestions = []
    used_ids = set()

    for item in ranked:
        course = active_courses.get(
            item["title"].casefold()
        )

        if not course or course.id in used_ids:
            continue

        suggestions.append(
            {
                "course": course,
                "reason": item["reason"],
            }
        )
        used_ids.add(course.id)

        if len(suggestions) >= limit:
            break

    return suggestions
