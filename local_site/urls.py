from django.urls import path
from . import views

app_name = "local_site"

urlpatterns = [
    path("<slug:slug>/", views.branch_landing, name="branch_landing"),
]
