from django.urls import path

from . import views


urlpatterns = [

    # ============================================================
    # PUBLIC WEBSITE
    # ============================================================

    path(
        "",
        views.home,
        name="home"
    ),

    path(
        "about/",
        views.about,
        name="about"
    ),

    path(
        "academy/",
        views.academy,
        name="academy"
    ),

    path(
        "courses/",
        views.courses,
        name="courses"
    ),

    path(
        "courses/<slug:slug>/",
        views.course_detail,
        name="course_detail"
    ),

    path(
        "business-solutions/",
        views.business_solutions,
        name="business_solutions"
    ),

    path(
        "ai/",
        views.ai,
        name="ai"
    ),

    path(
        "saas/",
        views.saas,
        name="saas"
    ),

    path(
        "contact/",
        views.contact,
        name="contact"
    ),

    path(
        "contact/success/",
        views.contact_success,
        name="contact_success"
    ),
    # Enquiry Dashboard
    path("enquiries/", views.enquiry_dashboard, name="enquiry_dashboard"),

    # ============================================================
    # STUDENT LOGIN
    # ============================================================

    path(
        "student/login/",
        views.student_login,
        name="student_login"
    ),

    path(
        "student/logout/",
        views.student_logout,
        name="student_logout"
    ),

    path(
        "student/dashboard/",
        views.student_dashboard,
        name="student_dashboard"
    ),
    

    # ============================================================
    # ENQUIRY / CRM
    # ============================================================

    path(
        "dashboard/",
        views.enquiry_dashboard,
        name="enquiry_dashboard"
    ),

    path(
        "enquiry/<int:enquiry_id>/",
        views.enquiry_detail,
        name="enquiry_detail"
    ),

    path(
        "enquiry/<int:enquiry_id>/status/",
        views.update_enquiry_status,
        name="update_enquiry_status"
    ),

    path(
        "enquiry/<int:enquiry_id>/call/",
        views.log_enquiry_call,
        name="log_enquiry_call"
    ),

    path(
        "enquiry/<int:enquiry_id>/whatsapp/",
        views.log_enquiry_whatsapp,
        name="log_enquiry_whatsapp"
    ),


    # ============================================================
    # ADMISSION
    # ============================================================

    path(
        "enquiry/<int:enquiry_id>/admission/",
        views.create_admission,
        name="create_admission"
    ),

    path(
        "admission/<int:admission_id>/",
        views.admission_detail,
        name="admission_detail"
    ),
    path(
    "admissions/",
    views.admission_list,
    name="admission_list"
    ),


    # ============================================================
    # FEE PAYMENT
    # ============================================================

    path(
        "fee-payment/<int:student_id>/add/",
        views.add_fee_payment,
        name="add_fee_payment"
    ),

    path(
        "fee-payments/",
        views.fee_payment_list,
        name="fee_payment_list"
    ),

    path(
        "fee-receipt/<str:receipt_number>/",
        views.fee_receipt,
        name="fee_receipt"
    ),
    path(
    "management-dashboard/",
    views.management_dashboard,
    name="management_dashboard"
    ),


    path(
    "branch-dashboard/",
    views.branch_dashboard,
    name="branch_dashboard"
),
    path(
        "reports/",
        views.reports_dashboard,
        name="reports_dashboard"
    ),
    path(
    "reports/export-excel/",
    views.export_reports_excel,
    name="export_reports_excel"
    ),

    path(
        "staff-login/",
        views.staff_login,
        name="staff_login"
    ),
    path(
        "staff-logout/",
        views.staff_logout,
        name="staff_logout",
),
    path(
        "students/",
        views.student_list,
        name="student_list"
    ),
    path(
    "staff/",
    views.staff_list,
    name="staff_list"
),

path(
    "admissions/<int:admission_id>/edit/",
    views.edit_admission,
    name="edit_admission"
),
path(
    "student-quick-view/",
    views.student_quick_view,
    name="student_quick_view"
),
]