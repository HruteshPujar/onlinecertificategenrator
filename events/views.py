from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count

from .models import Event
from .forms import EventForm


@login_required
def event_list(request):
    search = request.GET.get("search", "").strip()

    events = Event.objects.filter(is_active=True).annotate(
        participant_count=Count("participants")
    ).order_by("-id")

    if search:
        events = events.filter(title__icontains=search)

    paginator = Paginator(events, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "events/event_list.html",
        {
            "page_obj": page_obj,
            "events": page_obj,
            "search": search,
        },
    )


@login_required
def add_event(request):
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save()
            messages.success(request, f"Event '{event.title}' created successfully!")
            return redirect("event_list")
    else:
        form = EventForm()

    return render(
        request,
        "events/add_event.html",
        {
            "form": form,
            "title": "Add New Event",
            "button_text": "Create Event",
        }
    )


@login_required
def edit_event(request, id):
    event = get_object_or_404(Event, id=id)

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, f"Event '{event.title}' updated successfully!")
            return redirect("event_list")
    else:
        form = EventForm(instance=event)

    return render(
        request,
        "events/edit_event.html",
        {
            "form": form,
            "event": event,
            "title": f"Edit Event: {event.title}",
            "button_text": "Update Event",
        }
    )


@login_required
def delete_event(request, id):
    event = get_object_or_404(Event, id=id)
    title = event.title
    event.is_active = False
    event.save(update_fields=["is_active"])

    messages.success(request, f"Event '{title}' deleted successfully.")
    return redirect("event_list")