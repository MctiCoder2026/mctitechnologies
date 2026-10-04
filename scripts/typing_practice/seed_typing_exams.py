from typing_practice.models import TypingLesson, TypingExam

exam_texts = {
    1: "asdf jkl; asdf jkl; sad lad fall ask dad flask salad",
    2: "ask dad fall salad flask all sad lad ask fall salad",
    3: "ease idea side file jade like safe deal ideal field",
    4: "read rude rule ride fire fair dear real user raise",
    5: "total tool root rate tour outer later tailor rotate",
    6: "good high light right thing night going height gather",
    7: "nice can clean dance center learn chance line nation",
    8: "move brave member value mobile number above become",
    9: "quick brown fox jumps over the lazy dog while students build accurate keyboard skills every day",
    10: "Consistent typing practice improves speed accuracy confidence and productivity. Focus on rhythm, correct finger movement and clean typing before chasing higher speed.",
}

created = 0
updated = 0

for order, content in exam_texts.items():
    lesson = TypingLesson.objects.filter(order=order, is_active=True).first()
    if not lesson:
        print(f"SKIP lesson order {order}: not found")
        continue

    exam, was_created = TypingExam.objects.update_or_create(
        lesson=lesson,
        defaults={
            "title": f"{lesson.title} - Benchmark Exam",
            "content": content,
            "target_wpm": lesson.target_wpm,
            "target_accuracy": lesson.target_accuracy,
            "duration_seconds": 120,
            "is_active": True,
        }
    )

    if was_created:
        created += 1
        print("CREATED:", exam.title)
    else:
        updated += 1
        print("UPDATED:", exam.title)

print()
print("TYPING EXAMS READY")
print("Created:", created)
print("Updated:", updated)
print("Total:", TypingExam.objects.filter(is_active=True).count())
