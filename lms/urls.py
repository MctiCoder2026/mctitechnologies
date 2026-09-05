from django.urls import path

from . import views


app_name = "lms"


urlpatterns = [

    # =====================================================
    # STUDENT LMS
    # =====================================================

    path(
        "my-courses/",
        views.my_courses,
        name="my_courses"
    ),

    path(
        "module/<int:module_id>/",
        views.module_topics,
        name="module_topics"
    ),

    path(
        "topic/<int:topic_id>/",
        views.topic_detail,
        name="topic_detail"
    ),

    path(
        "topic/<int:topic_id>/quiz/",
        views.topic_quiz,
        name="topic_quiz"
    ),

    path(
        "quiz-history/",
        views.quiz_history,
        name="quiz_history"
    ),

    path(
        "my-progress/",
        views.my_progress,
        name="my_progress"
    ),

    path(
        "certificates/",
        views.certificates,
        name="certificates"
    ),

    path(
        "certificates/download/",
        views.download_certificate,
        name="download_certificate"
    ),

    # =====================================================
    # LMS ADMIN REPORTS
    # =====================================================

    path(
        "admin/student-performance/",
        views.student_performance_report,
        name="student_performance_report"
    ),

]