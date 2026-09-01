import csv
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Count, Q

from events.models import Event
from participants.models import Participant


@login_required
def reports_dashboard(request):
    events = Event.objects.filter(is_active=True).annotate(
        total_participants=Count("participants"),
        certs_generated=Count("participants", filter=Q(participants__certificate_generated=True)),
        emails_sent=Count("participants", filter=Q(participants__email_sent=True)),
    ).order_by("-id")

    total_events = Event.objects.filter(is_active=True).count()
    total_participants = Participant.objects.count()
    total_certificates = Participant.objects.filter(certificate_generated=True).count()
    total_emails = Participant.objects.filter(email_sent=True).count()

    # College Distribution
    colleges = Participant.objects.exclude(college="").values("college").annotate(
        count=Count("id")
    ).order_by("-count")[:10]

    context = {
        "events": events,
        "total_events": total_events,
        "total_participants": total_participants,
        "total_certificates": total_certificates,
        "total_emails": total_emails,
        "colleges": colleges,
    }
    return render(request, "reports/reports.html", context)


@login_required
def export_participants_csv(request):
    event_id = request.GET.get("event")
    participants = Participant.objects.select_related("event").order_by("-id")

    filename = "all_participants.csv"
    if event_id:
        participants = participants.filter(event_id=event_id)
        if participants.exists():
            safe_title = participants.first().event.title.replace(" ", "_")
            filename = f"{safe_title}_participants.csv"

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(["ID", "Event", "Full Name", "Email", "Phone", "College", "Department", "USN", "Certificate Generated", "Email Sent", "Created At"])

    for p in participants:
        writer.writerow([
            p.id,
            p.event.title,
            p.full_name,
            p.email,
            p.phone,
            p.college,
            p.department,
            p.usn or "",
            "Yes" if p.certificate_generated else "No",
            "Yes" if p.email_sent else "No",
            p.created_at.strftime("%Y-%m-%d %H:%M"),
        ])

    return response

