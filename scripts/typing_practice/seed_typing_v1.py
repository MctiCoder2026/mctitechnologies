from typing_practice.models import TypingLesson


LESSONS = [
    {
        "title": "Home Row Keys",
        "slug": "home-row-keys",
        "level": "beginner",
        "order": 1,
        "target_wpm": 10,
        "target_accuracy": 90,
        "content": (
            "asdf jkl; asdf jkl; fdsa ;lkj "
            "asdf jkl; sad lad fall ask flask "
            "dad salad flask fall ask sad"
        ),
    },
    {
        "title": "Home Row Words",
        "slug": "home-row-words",
        "level": "beginner",
        "order": 2,
        "target_wpm": 12,
        "target_accuracy": 90,
        "content": (
            "ask dad fall flask salad lad sad "
            "all fall ask flask dad salad "
            "sad lad all ask fall"
        ),
    },
    {
        "title": "E and I Keys",
        "slug": "e-and-i-keys",
        "level": "beginner",
        "order": 3,
        "target_wpm": 14,
        "target_accuracy": 90,
        "content": (
            "see like life side file idea "
            "safe desk field slide alike "
            "she likes the file beside the desk"
        ),
    },
    {
        "title": "R and U Keys",
        "slug": "r-and-u-keys",
        "level": "beginner",
        "order": 4,
        "target_wpm": 16,
        "target_accuracy": 91,
        "content": (
            "read user sure rule rise fire "
            "use real result raise rural "
            "users read useful files regularly"
        ),
    },
    {
        "title": "T and O Keys",
        "slug": "t-and-o-keys",
        "level": "beginner",
        "order": 5,
        "target_wpm": 18,
        "target_accuracy": 92,
        "content": (
            "to tool sort store test road "
            "today start total office data "
            "students use tools to improve speed"
        ),
    },
    {
        "title": "G and H Keys",
        "slug": "g-and-h-keys",
        "level": "intermediate",
        "order": 6,
        "target_wpm": 20,
        "target_accuracy": 92,
        "content": (
            "good high right light growth "
            "hard higher digital skill "
            "good habits help students grow"
        ),
    },
    {
        "title": "C and N Keys",
        "slug": "c-and-n-keys",
        "level": "intermediate",
        "order": 7,
        "target_wpm": 22,
        "target_accuracy": 93,
        "content": (
            "can nice learn clean chance "
            "computer training centre "
            "practice can increase typing accuracy"
        ),
    },
    {
        "title": "V M and B Keys",
        "slug": "v-m-and-b-keys",
        "level": "intermediate",
        "order": 8,
        "target_wpm": 24,
        "target_accuracy": 93,
        "content": (
            "move value mobile become improve "
            "member number available "
            "practice improves movement and balance"
        ),
    },
    {
        "title": "Full Keyboard Practice",
        "slug": "full-keyboard-practice",
        "level": "intermediate",
        "order": 9,
        "target_wpm": 26,
        "target_accuracy": 94,
        "content": (
            "quick people work every day to build "
            "better skills and improve their typing. "
            "Focus on accuracy before increasing speed."
        ),
    },
    {
        "title": "English Speed Practice",
        "slug": "english-speed-practice",
        "level": "advanced",
        "order": 10,
        "target_wpm": 30,
        "target_accuracy": 95,
        "content": (
            "Technology skills become stronger through regular practice. "
            "A good typist focuses on accuracy, rhythm, posture, and speed. "
            "Practice every day and measure your improvement."
        ),
    },
]


created = 0
skipped = 0

for data in LESSONS:

    if TypingLesson.objects.filter(
        slug=data["slug"]
    ).exists():

        print(
            "SKIP:",
            data["title"],
            "(already exists)"
        )
        skipped += 1
        continue

    TypingLesson.objects.create(**data)

    print(
        "CREATED:",
        data["order"],
        data["title"]
    )

    created += 1


print()
print("TYPING V1 LESSON SEED COMPLETE ✅")
print("Created:", created)
print("Skipped:", skipped)
print(
    "Total active:",
    TypingLesson.objects.filter(
        is_active=True
    ).count()
)
