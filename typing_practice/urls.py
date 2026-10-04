from django.urls import path
from . import views

app_name = "typing_practice"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    path(
        "lesson/<slug:slug>/",
        views.lesson,
        name="lesson"
    ),

    path(
        "lesson/<slug:slug>/save/",
        views.save_attempt,
        name="save_attempt"
    ),

    path(
        "exam/<slug:slug>/",
        views.exam,
        name="exam"
    ),

    path(
        "exam/<slug:slug>/save/",
        views.save_exam_attempt,
        name="save_exam_attempt"
    ),

    path(
        "game/letter-rush/",
        views.letter_rush,
        name="letter_rush"
    ),

    path(
        "game/letter-rush/save/",
        views.save_game_attempt,
        name="save_game_attempt"
    ),

    path(
        "progress/",
        views.progress,
        name="progress"
    ),
]

# Public Typing Marketing Funnel
urlpatterns += [
    path("free/", views.public_typing, name="public_typing"),
    path("free/practice/<slug:slug>/", views.public_practice, name="public_practice"),
    path("free/game/", views.public_game, name="public_game"),
    path("free/register/", views.public_register, name="public_register"),
]

# Staff / Management Typing Accountability
urlpatterns += [
    path(
        "staff/report/",
        views.staff_typing_report,
        name="staff_report"
    ),
    path(
        "management/report/",
        views.management_typing_report,
        name="management_report"
    ),
]


urlpatterns += [
    path("certificate/download/", views.download_typing_certificate,
         name="download_certificate"),
    path("certificate/verify/<uuid:verification_token>/",
         views.verify_typing_certificate, name="verify_certificate"),
]
