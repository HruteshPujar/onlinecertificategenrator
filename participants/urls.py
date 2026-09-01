from django.urls import path
from . import views

urlpatterns = [

    path("", views.participant_list, name="participant_list"),

    path("add/", views.add_participant, name="add_participant"),

    path("edit/<int:id>/",
         views.edit_participant,
         name="edit_participant"),

    path("delete/<int:id>/",
         views.delete_participant,
         name="delete_participant"),
    path(
        "generate/<int:pk>/",
        views.generate_certificate_view,
        name="generate_certificate"),
    path(
        "preview/<int:pk>/",
        views.preview_certificate,
        name="preview_certificate"),
    path(
        "generate-all/<int:event_id>/",
        views.generate_all_certificates,
        name="generate_all_certificates"),
    path(
        "send-all-emails/<int:event_id>/",
        views.send_all_emails,
        name="send_all_emails"),
    path(
        "download-pdf/<int:pk>/",
        views.download_pdf,
        name="download_pdf"),
    path(
        "send-email/<int:pk>/",
        views.send_single_email_view,
        name="send_single_email"),
]