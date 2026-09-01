from django.urls import path
from . import views

urlpatterns = [
    path("participants/", views.import_participants, name="import_participants"),
    path("sample-template/", views.download_sample_template, name="download_sample_template"),
]