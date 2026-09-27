from core.models import Course
from lms.models import LMSModule, LMSTopic, QuizQuestion
from django.db import transaction


COURSE_ID = 47


@transaction.atomic
def build():
    course = Course.objects.get(id=COURSE_ID)

    print("=" * 60)
    print("BUILDING LMS:", course.title)
    print("=" * 60)

    from scripts.lms.aws_cloud_curriculum import AWS_CURRICULUM
    curriculum = AWS_CURRICULUM

    for module_order, module_data in enumerate(curriculum, start=1):

        module, _ = LMSModule.objects.update_or_create(
            course=course,
            order=module_order,
            defaults={
                "title": module_data["title"],
                "description": module_data.get("description", ""),
                "is_active": True,
            },
        )

        for topic_order, topic_data in enumerate(
            module_data["topics"],
            start=1
        ):

            topic, _ = LMSTopic.objects.update_or_create(
                module=module,
                order=topic_order,
                defaults={
                    "title": topic_data["title"],
                    "description": topic_data.get("description", ""),
                    "is_active": True,
                },
            )

            questions = topic_data["questions"]

            if len(questions) != 5:
                raise ValueError(
                    f"{module.title} / {topic.title} "
                    f"must contain exactly 5 questions."
                )

            for question_order, q in enumerate(
                questions,
                start=1
            ):

                QuizQuestion.objects.update_or_create(
                    topic=topic,
                    language="en",
                    order=question_order,
                    defaults={
                        "question": q["q"],
                        "option_a": q["a"],
                        "option_b": q["b"],
                        "option_c": q["c"],
                        "option_d": q["d"],
                        "correct_answer": q["answer"],
                        "is_active": True,
                    },
                )

    modules = LMSModule.objects.filter(course=course)
    topics = LMSTopic.objects.filter(module__course=course)
    questions = QuizQuestion.objects.filter(
        topic__module__course=course,
        language="en"
    )

    print()
    print("BUILD COMPLETE")
    print("Modules:", modules.count())
    print("Topics:", topics.count())
    print("English Questions:", questions.count())


build()
