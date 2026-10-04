from django.urls import path
from . import views

app_name = "career_tools"

from django.urls import path
from . import views

app_name = "career_tools"

from . import quick_views
from . import report_views
from django.views.generic import RedirectView

urlpatterns = [
    # Legacy Career Compass link - keep old shared links working
    path(
        "compass/",
        RedirectView.as_view(
            pattern_name="career_tools:career_compass_start",
            permanent=True
        ),
        name="legacy_career_compass"
    ),

    # MCTI Career Compass - After 10th
    path(
        "career-compass/",
        views.career_compass_start,
        name="career_compass_start"
    ),
    path(
        "career-compass/test/",
        views.career_compass_test,
        name="career_compass_test"
    ),
    path(
        "career-compass/result/<int:attempt_id>/",
        views.career_compass_result,
        name="career_compass_result"
    ),

    path(
        "aptitude/start/",
        quick_views.public_aptitude_start,
        name="public_aptitude_start_legacy"
    ),

    path("", views.career_home, name="home"),

    path(
        "free-aptitude/",
        quick_views.public_aptitude_start,
        name="public_aptitude_start"
    ),

    path(
        "free-aptitude/qr/",
        quick_views.public_aptitude_qr,
        name="public_aptitude_qr"
    ),

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
        "quick-enquiry/report/<int:profile_id>/",
        report_views.career_report_pdf,
        name="career_report_pdf"
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
        "career-account/created/",
        views.career_account_created,
        name="career_account_created"
    ),

    path(
        "career-account/login/",
        views.career_login,
        name="career_login"
    ),

    path(
        "career-account/",
        views.career_dashboard,
        name="career_dashboard"
    ),

    path(
        "career-account/logout/",
        views.career_logout,
        name="career_logout"
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
        "counsellor/profile/<int:profile_id>/reset-pin/",
        views.counsellor_reset_career_pin,
        name="counsellor_reset_career_pin"
    ),

    path(
        "counsellor/profile/<int:profile_id>/",
        views.counsellor_profile_detail,
        name="counsellor_profile_detail"
    ),

    path(
        "career-compass/dashboard/",
        views.career_compass_dashboard,
        name="career_compass_dashboard"
    ),
    path(
        "career-compass/dashboard/<int:attempt_id>/status/",
        views.career_compass_update_status,
        name="career_compass_update_status"
    ),
]
from . import assessment_report_views
urlpatterns += [
    path("reports/", assessment_report_views.assessment_reports,
         name="assessment_reports"),
]
