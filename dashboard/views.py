from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from events.models import Event
from participants.models import Participant
from django.db.models import Count

@login_required
def dashboard(request):

    total_events = Event.objects.count()

    total_participants = Participant.objects.count()

    total_certificates = Participant.objects.filter(
        certificate_generated=True
    ).count()

    total_emails = Participant.objects.filter(
        email_sent=True
    ).count()

    recent_events = Event.objects.order_by(
        "-id"
    )[:5]

    recent_participants = Participant.objects.select_related(
            "event"
        ).order_by(
            "-id"
        )[:5]
        # Participants per Event

    event_data = Event.objects.annotate(
        total=Count("participants")
    )

    event_labels = [
        event.title
        for event in event_data
    ]

    event_counts = [
        event.total
        for event in event_data
    ]

    # Certificate Statistics

    generated = Participant.objects.filter(
        certificate_generated=True
    ).count()

    pending = Participant.objects.filter(
        certificate_generated=False
    ).count()

    context = {

    "total_events": total_events,

    "total_participants": total_participants,

    "total_certificates": total_certificates,

    "total_emails": total_emails,

    "recent_events": recent_events,

    "recent_participants": recent_participants,

    "event_labels": event_labels,

    "event_counts": event_counts,

    "generated": generated,

    "pending": pending,

}

    return render(
        request,
        "dashboard/dashboard.html",
        context
    )