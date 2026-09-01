from django.contrib import admin
from .models import Participant


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):

    list_display = (
        "full_name",
        "event",
        "email",
        "phone",
        "certificate_generated",
        "email_sent",
    )

    search_fields = (
        "full_name",
        "email",
        "college",
    )

    list_filter = (
        "event",
        "certificate_generated",
        "email_sent",
    )