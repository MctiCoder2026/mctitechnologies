from django.urls import path

from .views import (
    mobile_login,
    student_dashboard,
    my_courses,
    course_content,
    topic_detail,
    topic_quiz,
    submit_topic_quiz,
    mark_mobile_attendance,
)


urlpatterns = [

    path(
        "login/",
        mobile_login,
        name="mobile-login"
    ),

    path(
        "dashboard/",
        student_dashboard,
        name="student-dashboard"
    ),

    path(
        "courses/",
        my_courses,
        name="my-courses"
    ),

    path(
        "courses/<int:course_id>/",
        course_content,
        name="course-content"
    ),

    path(
        "topics/<int:topic_id>/",
        topic_detail,
        name="mobile-topic-detail"
    ),

    path(
        "topics/<int:topic_id>/quiz/",
        topic_quiz,
        name="mobile-topic-quiz"
    ),

    path(
        "topics/<int:topic_id>/quiz/submit/",
        submit_topic_quiz,
        name="mobile-submit-topic-quiz"
    ),

    path(
        "attendance/mark/",
        mark_mobile_attendance,
        name="mobile-mark-attendance"
    ),
]