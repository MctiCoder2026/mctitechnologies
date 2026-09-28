from django.urls import path

from . import views

app_name = "assessments"

urlpatterns = [
    # --------------------------------------------------------
    # MCTI HR HIRING ASSESSMENT
    # One common flow for all job roles
    # --------------------------------------------------------
    path(
        "hiring/",
        views.hiring_start,
        name="hiring_start",
    ),
    path(
        "hiring/hr/",
        views.hiring_hr_dashboard,
        name="hiring_hr_dashboard",
    ),
    path(
        "hiring/hr/evaluate/<int:application_id>/",
        views.hiring_hr_evaluate,
        name="hiring_hr_evaluate",
    ),
    path(
        "hiring/interview/<int:application_id>/",
        views.hiring_interview,
        name="hiring_interview",
    ),
    path(
        "hiring/quiz/<int:attempt_id>/",
        views.hiring_quiz,
        name="hiring_quiz",
    ),
    path(
        "hiring/practical/<int:attempt_id>/",
        views.hiring_practical,
        name="hiring_practical",
    ),
    path(
        "hiring/communication/<int:attempt_id>/",
        views.hiring_communication,
        name="hiring_communication",
    ),
    path(
        "hiring/result/<int:attempt_id>/",
        views.hiring_result,
        name="hiring_result",
    ),
    # --------------------------------------------------------
    # MCTI SCHOLARSHIP TEST
    # --------------------------------------------------------
    path(
        "scholarship/",
        views.scholarship_start,
        name="scholarship_start",
    ),
    path(
        "scholarship/quiz/<int:attempt_id>/",
        views.scholarship_quiz,
        name="scholarship_quiz",
    ),
    path(
        "scholarship/result/<int:attempt_id>/",
        views.scholarship_result,
        name="scholarship_result",
    ),
    path(
        "scholarship/dashboard/",
        views.scholarship_dashboard,
        name="scholarship_dashboard",
    ),
    path(
        "scholarship/dashboard/<int:scholarship_id>/status/",
        views.scholarship_update_status,
        name="scholarship_update_status",
    ),
    path(
        "scholarship/dashboard/<int:scholarship_id>/send-to-enquiry/",
        views.scholarship_send_to_enquiry,
        name="scholarship_send_to_enquiry",
    ),

    path(
        "ai-ready/",
        views.ai_ready_start,
        name="ai_ready_start",
    ),
    path(
        "ai-ready/quiz/<int:attempt_id>/",
        views.ai_ready_quiz,
        name="ai_ready_quiz",
    ),
    path(
        "ai-ready/result/<int:attempt_id>/",
        views.ai_ready_result,
        name="ai_ready_result",
    ),
    path(
        "ai-ready/certificate/<int:attempt_id>/",
        views.ai_ready_certificate,
        name="ai_ready_certificate",
    ),
    path(
        "certificate/verify/<str:verification_token>/",
        views.verify_assessment_certificate,
        name="verify_assessment_certificate",
    ),
]
