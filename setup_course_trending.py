import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

django.setup()

from core.models import Course


TRENDING_COURSES = [
    "Data Analysis with AI",
    "Digital Marketing with AI",
    "Advanced Excel",
    "Tally Prime with GST",
    "Full Stack Development",
    "Python Development",
    "Cyber Security & Ethical Hacking",
    "Cloud Computing",
    "SAP FICO",
    "Artificial Intelligence & Machine Learning",
    "Power BI",
    "Graphic Design",
]


print()
print("======================================")
print("MCTI TRENDING COURSE SETUP")
print("======================================")

found = 0
missing = []

# Only reset existing trending flag.
# No course is deleted or modified otherwise.
Course.objects.filter(
    is_trending=True
).update(
    is_trending=False,
    display_order=0
)


for order, title in enumerate(
    TRENDING_COURSES,
    start=1
):

    course = Course.objects.filter(
        title__iexact=title,
        is_active=True
    ).first()

    if not course:

        missing.append(title)
        continue

    course.is_trending = True
    course.display_order = order

    course.save(
        update_fields=[
            "is_trending",
            "display_order",
        ]
    )

    found += 1

    print(
        f"{order:02d}. {course.title}"
    )


print()
print("--------------------------------------")
print(f"Trending Set : {found}")
print(f"Missing      : {len(missing)}")

if missing:

    print()
    print("MISSING COURSES:")

    for title in missing:
        print(" -", title)

print("======================================")

if missing:
    raise SystemExit(
        "ERROR: Some trending courses were not found."
    )

print("TRENDING SETUP COMPLETE")