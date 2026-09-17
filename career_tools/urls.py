from django.urls import path
from . import views

app_name = "career_tools"

from django.urls import path
from . import views

app_name = "career_tools"

from . import quick_views

urlpatterns = [
    path("", views.career_home, name="home"),

    path(
        "quick-enquiry/",
        quick_views.quick_career_enquiry,
        name="quick_career_enquiry"
    ),

    path(
        "quick-enquiry/result/<int:profile_id>/",
        quick_views.quick_enquiry_result,
        name="quick_enquiry_result"
    ),

    path(
        "aptitude-access/<str:token>/",
        quick_views.aptitude_access,
        name="aptitude_access"
    ),

    path(
        "quick-enquiry/aptitude-qr/<int:profile_id>/",
        quick_views.aptitude_qr,
        name="aptitude_qr"
    ),

    path(
        "resume-builder/",
        views.resume_builder,
        name="resume_builder"
    ),

    path(
        "guest/",
        views.guest_start,
        name="guest_start"
    ),

    path(
        "guest/resume-builder/",
        views.guest_resume_builder,
        name="guest_resume_builder"
    ),

    path(
        "resume/download/",
        views.download_resume_pdf,
        name="download_resume_pdf"
    ),

    # Aptitude Test
    path(
        "aptitude/",
        views.aptitude_test,
        name="aptitude_test"
    ),

    path(
        "aptitude/result/<int:attempt_id>/",
        views.aptitude_result,
        name="aptitude_result"
    ),
    path(
    "career-recommendation/<int:attempt_id>/",
    views.career_recommendation,
    name="career_recommendation"
    ),
    
    path(
    "counsellor/",
    views.counsellor_dashboard,
    name="counsellor_dashboard"
    ),

    path(
        "counsellor/profile/<int:profile_id>/",
        views.counsellor_profile_detail,
        name="counsellor_profile_detail"
    ),
]