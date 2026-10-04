from decimal import Decimal
from django.db import transaction
from typing_practice.models import TypingLesson, TypingExam

paragraphs = [
    "Clear communication is an essential skill in every workplace. A well-written message helps people understand instructions, complete their tasks, and avoid unnecessary confusion. Before sending an email, read it carefully and check the names, dates, and important details. Simple language and accurate typing make professional communication more effective.",
    "Learning a new skill requires patience and regular practice. Progress may seem slow at first, but small improvements become visible over time. Set a realistic goal, practise every day, and review your mistakes without losing confidence. A student who follows a steady routine can develop both speed and accuracy through consistent effort.",
    "Technology can help us prepare documents, organise information, and solve problems. However, we still need to understand the work we produce. Even when an artificial intelligence tool creates a draft, a person must review the facts, correct mistakes, and improve the wording. Good keyboard skills make this process faster and easier.",
    "A successful office depends on teamwork and responsibility. Each employee should understand the task, respect the deadline, and communicate any difficulty early. Keeping records in order allows the team to find important information when it is needed. Careful work builds trust between colleagues and improves the quality of customer service.",
    "Time management begins with choosing the most important task. Prepare a short list before starting your day and complete one activity at a time. Avoid checking your phone repeatedly while working on a document. Taking a brief break between focused sessions can help you return with better concentration and a clear mind.",
    "Typing speed is useful only when the text is accurate. Keep your hands relaxed, use the correct fingers, and look at the passage instead of the keyboard. Read a few words ahead while maintaining a comfortable rhythm. When you make an error, correct it calmly and continue without rushing through the next sentence.",
    "Education gives people the opportunity to improve their knowledge and confidence. Practical training connects classroom lessons with real tasks. Students can prepare letters, write reports, maintain records, and communicate with customers. These everyday activities show why strong English typing skills remain valuable in modern careers.",
    "Professional growth does not stop after completing a course. Continue practising, ask useful questions, and apply your knowledge in real situations. A person who learns from feedback can improve the quality of their work. Consistency, honesty, and attention to detail are habits that support long-term success.",
]

practice = " ".join(paragraphs)
exam_passage = " ".join(paragraphs[3:] + paragraphs[:3])

def long_passage(text):
    return " ".join([text] * (12000 // len(text) + 1))

slug = "master-in-english-typing"
with transaction.atomic():
    if not TypingLesson.objects.filter(order=10, is_active=True).exists():
        raise RuntimeError("Active Level 10 not found.")
    if TypingLesson.objects.filter(order__gte=11, is_active=True).exclude(slug=slug).exists():
        raise RuntimeError("Another active level exists at order 11 or above; no changes.")

    lesson, created = TypingLesson.objects.update_or_create(
        slug=slug,
        defaults={
            "title": "Master in English Typing",
            "level": "advanced",
            "order": 11,
            "content": long_passage(practice),
            "target_wpm": 40,
            "target_accuracy": Decimal("95.00"),
            "is_active": True,
        },
    )
    exam, exam_created = TypingExam.objects.update_or_create(
        lesson=lesson,
        defaults={
            "title": "Master in English Typing - 5 Minute Benchmark",
            "content": long_passage(exam_passage),
            "target_wpm": 40,
            "target_accuracy": Decimal("95.00"),
            "duration_seconds": 300,
            "is_active": True,
        },
    )

print("DONE: Level 11", "created" if created else "updated")
print("Target: 40 WPM | 95% accuracy")
print("Practice: 300 seconds | Exam:", exam.duration_seconds, "seconds")
print("Content characters:", len(lesson.content), "|", len(exam.content))
print("Existing student progress and certificates preserved.")
