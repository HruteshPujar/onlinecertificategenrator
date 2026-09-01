from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q

from participants.models import Participant
from events.models import Event


@login_required
def certificate_list(request):
    search = request.GET.get("search", "").strip()
    event_id = request.GET.get("event", "").strip()

    certificates = Participant.objects.filter(
        certificate_generated=True
    ).select_related("event").order_by("-id")

    if event_id:
        certificates = certificates.filter(event_id=event_id)

    if search:
        certificates = certificates.filter(
            Q(full_name__icontains=search)
            | Q(email__icontains=search)
            | Q(usn__icontains=search)
            | Q(event__title__icontains=search)
        )

    paginator = Paginator(certificates, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    events = Event.objects.filter(is_active=True).order_by("-id")

    total_generated = Participant.objects.filter(certificate_generated=True).count()
    total_pending = Participant.objects.filter(certificate_generated=False).count()

    return render(
        request,
        "certificates/certificate_list.html",
        {
            "page_obj": page_obj,
            "search": search,
            "selected_event": event_id,
            "events": events,
            "total_generated": total_generated,
            "total_pending": total_pending,
        },
    )

