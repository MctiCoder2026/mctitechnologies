from django.urls import path

from . import views, delivery_views, classroom_workflow


app_name = "lms"


urlpatterns = [

    path("classroom/trainer-login/", classroom_workflow.trainer_login, name="trainer_login"),
    path("classroom/trainer-logout/", classroom_workflow.trainer_logout, name="trainer_logout"),
    path("classroom/workspace/", classroom_workflow.trainer_workspace, name="trainer_workspace"),
    path("classroom/workspace/assignment/<int:assignment_id>/submit/", classroom_workflow.submit_class, name="submit_class"),
    path("classroom/workspace/report/<int:report_id>/approve-completion/", classroom_workflow.trainer_approve_completion, name="trainer_approve_completion"),
    path("classroom/staff/", classroom_workflow.staff_workspace, name="staff_classroom"),
    path("classroom/staff/create-trainer/", classroom_workflow.create_trainer, name="create_classroom_trainer"),
    path("classroom/staff/trainer/<int:trainer_id>/deactivate/", classroom_workflow.deactivate_trainer, name="deactivate_classroom_trainer"),
    path("classroom/staff/assign/", classroom_workflow.assign_weekly_topic, name="assign_weekly_topic"),
    path("classroom/staff/report/<int:report_id>/review/", classroom_workflow.review_class, name="review_class"),
    path("classroom/staff/report/<int:report_id>/close/", classroom_workflow.close_topic, name="close_topic"),
    path("classroom/student/report/<int:report_id>/feedback/", classroom_workflow.student_feedback, name="student_feedback"),


    path("classroom/trainer/", delivery_views.trainer_delivery, name="trainer_delivery"),
    path("classroom/trainer/record/", delivery_views.record_delivery, name="record_delivery"),
    path("classroom/trainer/lab/<int:record_id>/verify/", delivery_views.verify_lab_practice, name="verify_lab_practice"),
    path("classroom/student/", classroom_workflow.student_classroom, name="student_delivery"),
    path("classroom/report/", delivery_views.delivery_report, name="delivery_report"),
    path("classroom/report/student/<int:enrollment_id>/course/<int:course_id>/", delivery_views.delivery_student_history, name="delivery_student_history"),
    path("classroom/student/doubt/", delivery_views.raise_delivery_doubt, name="raise_delivery_doubt"),


    # =====================================================
    # STAFF TRAINING LMS
    # =====================================================

    path(
        "staff/training/",
        views.staff_training,
        name="staff_training"
    ),

    path(
        "staff/training/module/<int:module_id>/",
        views.staff_training_module,
        name="staff_training_module"
    ),

    path(
        "staff/training/topic/<int:topic_id>/",
        views.staff_training_topic,
        name="staff_training_topic"
    ),

    path(
        "staff/training/topic/<int:topic_id>/quiz/",
        views.staff_training_quiz,
        name="staff_training_quiz"
    ),

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

    # =====================================================
    # CERTIFICATES
    # =====================================================

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

    path(
        "certificate/verify/<uuid:verification_token>/",
        views.verify_certificate,
        name="verify_certificate"
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