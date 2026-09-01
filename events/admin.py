from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "venue",
        "event_date",
        "is_active",
    )

    search_fields = (
        "title",
        "venue",
    )

    list_filter = (
        "event_date",
        "is_active",
    )