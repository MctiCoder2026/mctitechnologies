from django.urls import path
from . import views

app_name = "alumni"

urlpatterns = [
    path(
        "contact/<int:contact_id>/confirm-message/",
        views.confirm_message,
        name="confirm_message",
    ),

    path("import/", views.import_excel, name="import"),
    path("", views.dashboard, name="dashboard"),
    path("contact/<int:contact_id>/update/", views.update_contact, name="update_contact"),
]
