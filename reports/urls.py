from django.urls import path
from . import views

urlpatterns = [
    path("", views.reports_dashboard, name="reports_dashboard"),
    path("export/participants/", views.export_participants_csv, name="export_participants_csv"),
]
