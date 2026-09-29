from django.urls import path
from . import views

app_name = "exam_preparation"

urlpatterns = [
    path("logout/", views.ssc_student_logout, name="ssc_student_logout"),
    path("login/", views.ssc_student_login, name="ssc_student_login"),
    path("mock/start/", views.ssc_mock_start, name="ssc_mock_start"),
    path("mock/quiz/<int:attempt_id>/", views.ssc_mock_quiz, name="ssc_mock_quiz"),
    path("mock/result/<int:attempt_id>/", views.ssc_mock_result, name="ssc_mock_result"),
    path(
        "management/student/<int:student_id>/send-to-enquiry/",
        views.ssc_send_to_enquiry,
        name="ssc_send_to_enquiry",
    ),

    path(
        "management/",
        views.ssc_management_dashboard,
        name="ssc_management_dashboard",
    ),

    path(
        "resource/<int:resource_id>/open/",
        views.ssc_resource_open,
        name="ssc_resource_open",
    ),

    path(
        "",
        views.ssc_exam_preparation,
        name="ssc_exam_preparation",
    ),
]
