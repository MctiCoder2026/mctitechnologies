from django.urls import path

from . import views

app_name = "assessments"

urlpatterns = [
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
