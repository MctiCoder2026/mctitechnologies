from decimal import Decimal
from django.db import transaction
from typing_practice.models import TypingLesson, TypingExam

passages = [
("Professional Communication",
"""Clear communication helps people work together and complete tasks correctly. Before writing a message, decide what the reader needs to know. Begin with the purpose, explain the important details, and end with the next action. A polite tone makes the message easier to understand. Check the spelling of names and review every date before sending a document.

A customer has requested information about a training programme. The office assistant prepares a reply explaining the course schedule, admission process, and available support. The message uses complete sentences and avoids confusing abbreviations. After reviewing the details, the assistant sends the reply and records the enquiry for a follow-up."""),
("Business Letters",
"""A professional letter should explain its purpose clearly. Start with a suitable greeting and introduce the reason for writing. Arrange the information in a logical order so the reader can follow the message easily. Keep the language polite and direct. Before printing the letter, check the address, subject, punctuation, and closing statement.

The training centre is inviting a company to attend a student placement event. The letter explains the purpose of the event and describes the skills students have developed. It asks the company to share its hiring requirements and nominate a representative. The coordinator includes contact details so the company can request further information."""),
("Office Reports",
"""An office report presents information that helps a team make decisions. The writer should separate observations from personal opinions and explain the results accurately. A useful report describes what happened, identifies the main issue, and suggests a practical next step. Clear headings and complete sentences help readers understand the information.

At the end of the week, a coordinator reviews student attendance and completed assignments. Several students have improved their performance, while a few need additional support. The coordinator records these findings and prepares a plan for the next week. Trainers receive the report before the meeting so they can discuss the progress."""),
("Customer Service",
"""Good customer service begins with listening carefully. Allow the customer to explain the issue before suggesting a solution. Ask clear questions when important details are missing. Record the request accurately and explain what will happen next. If the issue needs more time, provide a realistic update instead of making a promise that cannot be kept.

A student contacts the office because a receipt has not arrived. The assistant checks the payment record and confirms the correct contact details. After finding the receipt, the assistant shares it through the approved process. The student receives a clear explanation, and the office records the request as completed."""),
("Technology and AI",
"""Digital tools can help people organise information and prepare documents quickly. Artificial intelligence can suggest ideas, improve wording, and create an initial draft. However, the person using the tool must review the result. Incorrect facts and unclear instructions can create problems when copied without checking. Human judgment remains important in every professional task.

A student uses an assistant to prepare a project introduction. The first draft contains a few statements that do not match the project. The student checks the original notes, corrects the details, and rewrites the conclusion. Strong typing skills make editing easier and allow the student to complete the work confidently."""),
("Time Management",
"""A productive day starts with a clear plan. Write down the tasks that need attention and choose the most important one first. Give each activity enough time and avoid switching between unrelated jobs repeatedly. When a task is complete, review the result before moving on. A practical routine makes work more predictable and reduces unnecessary pressure.

An office assistant needs to prepare a report, answer enquiries, and update records. The assistant completes the report during a quiet period and then handles the enquiries. Important information is recorded immediately so it is not forgotten. By following a simple schedule, the assistant finishes the work without rushing."""),
("Career and Learning",
"""Learning continues throughout a professional career. New tools and changing responsibilities create opportunities to improve existing skills. A person who asks useful questions and accepts feedback can develop steadily. Practice should include real tasks instead of only memorising instructions. Confidence grows when knowledge is applied successfully in everyday situations.

A student preparing for an office role practises writing emails and maintaining records. The trainer reviews the work and points out common mistakes. The student repeats difficult tasks until the process becomes familiar. Over time, the documents become clearer and the typing becomes more accurate. Regular effort creates lasting improvement."""),
("Teamwork and Leadership",
"""A reliable team depends on clear responsibilities and respectful communication. Each member should understand the goal and know when the work must be completed. When a problem appears, share it early so the team can respond. Listening to different ideas can improve the final result. Good leadership supports people while keeping attention on the shared task.

A group of students is preparing a presentation for a community event. One student organises the information, another prepares the slides, and a third reviews the wording. The group checks its progress together and corrects errors before the event. Their cooperation helps them deliver a clear and useful presentation."""),
("Education and Community",
"""Education can help people make informed decisions and develop practical skills. A useful learning programme connects explanations with everyday examples. Students should have opportunities to ask questions and practise what they have learned. Clear communication allows trainers to guide learners with different levels of experience. Patient support can make learning more accessible.

A local training centre organises a digital awareness session. Participants learn how to identify suspicious messages and protect personal information. The trainer explains each example slowly and invites questions. After the session, participants practise checking a message before responding. The activity helps the community use technology with greater confidence."""),
("Final Master Challenge",
"""Accurate English typing combines concentration, reading, and steady movement. The typist must follow the passage carefully while maintaining a comfortable rhythm. Capital letters, punctuation, and spaces are part of the task. Speed improves through regular practice, but accuracy should remain a priority. A complete five-minute test measures consistency over a longer period.

In a modern workplace, people prepare letters, update reports, and review digital documents every day. Even when software produces a draft, someone must check the meaning and correct the details. Strong keyboard skills make this work easier. Completing this challenge shows progress in sustained typing, careful reading, and professional document preparation."""),
]

def slug_for(order):
    return "master-in-english-typing" if order == 11 else f"master-english-typing-{order}"

def expand(text):
    text = " ".join(text.split())
    return " ".join([text] * (12000 // len(text) + 1))

with transaction.atomic():
    if not TypingLesson.objects.filter(order=10, is_active=True).exists():
        raise RuntimeError("Active Level 10 not found.")
    expected = [slug_for(order) for order in range(11, 21)]
    if TypingLesson.objects.filter(order__gte=11, order__lte=20).exclude(slug__in=expected).exists():
        raise RuntimeError("Another lesson occupies orders 11–20; no changes.")

    for order, (topic, passage) in enumerate(passages, start=11):
        title = (
            "Master in English Typing"
            if order == 11 else f"Master English Typing - {topic}"
        )
        lesson, created = TypingLesson.objects.update_or_create(
            slug=slug_for(order),
            defaults={
                "title": title,
                "order": order,
                "level": "advanced",
                "content": expand(passage),
                "target_wpm": 40,
                "target_accuracy": Decimal("95.00"),
                "is_active": True,
            },
        )
        # Reverse paragraph order for a different exam opening.
        exam_passage = " ".join(reversed(passage.split("\n\n")))
        exam, _ = TypingExam.objects.update_or_create(
            lesson=lesson,
            defaults={
                "title": f"{title} - 5 Minute Benchmark",
                "content": expand(exam_passage),
                "target_wpm": 40,
                "target_accuracy": Decimal("95.00"),
                "duration_seconds": 300,
                "is_active": True,
            },
        )
        print(f"Level {order}: {topic} | 40 WPM | 95% | 300 seconds")

print("DONE: Master series 11–20 ready. Existing progress preserved.")
