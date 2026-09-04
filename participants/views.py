import os
import zipfile

from django.http import FileResponse, Http404
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from events.models import Event
from .models import Participant
from .forms import ParticipantForm
from .services import generate_single_certificate, send_participant_email_service
from .pdf_utils import generate_pdf_certificate


@login_required
def participant_list(request):
    search = request.GET.get("search", "").strip()
    event_id = request.GET.get("event", "").strip()

    participants = Participant.objects.select_related("event").order_by("-id")

    if event_id:
        participants = participants.filter(event_id=event_id)

    if search:
        participants = participants.filter(
            Q(full_name__icontains=search)
            | Q(email__icontains=search)
            | Q(usn__icontains=search)
            | Q(college__icontains=search)
            | Q(department__icontains=search)
        )

    paginator = Paginator(participants, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    events = Event.objects.filter(is_active=True).order_by("-id")

    return render(
        request,
        "participants/participant_list.html",
        {
            "page_obj": page_obj,
            "search": search,
            "selected_event": event_id,
            "events": events,
        },
    )


@login_required
def add_participant(request):
    if request.method == "POST":
        form = ParticipantForm(request.POST)
        if form.is_valid():
            participant = form.save()
            messages.success(request, f"Participant '{participant.full_name}' added successfully!")
            return redirect("participant_list")
    else:
        form = ParticipantForm()

    return render(
        request,
        "participants/add_participant.html",
        {
            "form": form,
            "title": "Add New Participant",
            "button": "Save Participant",
        },
    )


@login_required
def edit_participant(request, id):
    participant = get_object_or_404(Participant, id=id)

    if request.method == "POST":
        form = ParticipantForm(request.POST, instance=participant)
        if form.is_valid():
            participant = form.save()
            messages.success(request, f"Participant '{participant.full_name}' updated successfully!")
            return redirect("participant_list")
    else:
        form = ParticipantForm(instance=participant)

    return render(
        request,
        "participants/add_participant.html",
        {
            "form": form,
            "title": f"Edit Participant: {participant.full_name}",
            "button": "Update Participant",
        },
    )


@login_required
def delete_participant(request, id):
    participant = get_object_or_404(Participant, id=id)
    name = participant.full_name
    participant.delete()
    messages.success(request, f"Participant '{name}' deleted successfully.")
    return redirect("participant_list")


@login_required
def generate_certificate_view(request, pk):
    participant = get_object_or_404(Participant, pk=pk)

    try:
        base_url = request.build_absolute_uri('/')
        generate_single_certificate(participant, base_url=base_url)
        messages.success(request, f"Certificate generated for {participant.full_name}.")
    except Exception as e:
        messages.error(request, f"Error generating certificate: {e}")

    # Return to previous page or participant list
    next_url = request.GET.get("next") or request.META.get("HTTP_REFERER")
    if next_url and next_url.startswith("/"):
        return redirect(next_url)
    return redirect("participant_list")


@login_required
def preview_certificate(request, pk):
    participant = get_object_or_404(Participant, pk=pk)

    # Ensure certificate exists for preview
    if not participant.generated_certificate:
        try:
            base_url = request.build_absolute_uri('/')
            generate_single_certificate(participant, base_url=base_url)
            participant.refresh_from_db()
        except Exception as e:
            messages.warning(request, f"Could not pre-render certificate: {e}")

    return render(
        request,
        "participants/preview_certificate.html",
        {
            "participant": participant,
        }
    )


@login_required
def send_single_email_view(request, pk):
    participant = get_object_or_404(Participant, pk=pk)

    try:
        send_participant_email_service(participant)
        if "console" in getattr(settings, "EMAIL_BACKEND", ""):
            messages.info(
                request,
                f"Email for {participant.email} generated & logged to server console. (To deliver to actual inboxes, add your Gmail App Password to .env)"
            )
        else:
            messages.success(request, f"Certificate PDF dispatched to {participant.email} successfully!")
    except Exception as e:
        error_msg = str(e)
        if any(term in error_msg for term in ["Authentication Required", "Username and Password not accepted", "530", "535", "BadCredentials"]):
            messages.error(
                request,
                "Email dispatch failed: Gmail SMTP Authentication rejected. Google requires a 16-character Google App Password (not your regular Gmail password). Please generate one at https://myaccount.google.com/apppasswords and update EMAIL_HOST_PASSWORD in your .env file."
            )
        else:
            messages.error(request, f"Failed to dispatch email to {participant.email}: {e}")

    next_url = request.GET.get("next") or request.META.get("HTTP_REFERER")
    if next_url and next_url.startswith("/"):
        return redirect(next_url)
    return redirect("participant_list")




@login_required
def generate_all_certificates(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    participants = Participant.objects.filter(event=event)

    if not participants.exists():
        messages.warning(request, f"No participants found for '{event.title}'.")
        return redirect("participant_list")

    base_url = request.build_absolute_uri('/')
    generated = 0
    failed = 0

    for participant in participants:
        try:
            generate_single_certificate(participant, base_url=base_url)
            generated += 1
        except Exception as e:
            failed += 1

    messages.success(request, f"Generated {generated} certificates ({failed} failed).")

    # Prepare ZIP
    zip_dir = os.path.join(settings.MEDIA_ROOT, "zip")
    os.makedirs(zip_dir, exist_ok=True)

    safe_title = "".join(c for c in event.title if c.isalnum() or c in (' ', '_', '-')).rstrip()
    zip_filename = f"{safe_title}_Certificates.zip".replace(" ", "_")
    zip_path = os.path.join(zip_dir, zip_filename)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for participant in participants:
            if participant.generated_certificate and os.path.exists(participant.generated_certificate.path):
                safe_name = participant.full_name.replace(" ", "_").replace("/", "_")
                zipf.write(
                    participant.generated_certificate.path,
                    arcname=f"{participant.id}_{safe_name}.png"
                )

    if os.path.exists(zip_path) and os.path.getsize(zip_path) > 0:
        return FileResponse(
            open(zip_path, "rb"),
            as_attachment=True,
            filename=zip_filename
        )
    return redirect("participant_list")


@login_required
def send_all_emails(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    participants = Participant.objects.filter(event=event)

    sent = 0
    failed = 0
    skipped = 0

    base_url = request.build_absolute_uri('/')

    for participant in participants:
        if not participant.generated_certificate:
            try:
                generate_single_certificate(participant, base_url=base_url)
                participant.refresh_from_db()
            except Exception:
                skipped += 1
                continue

        if participant.email_sent:
            skipped += 1
            continue

        try:
            send_participant_email_service(participant)
            sent += 1
        except Exception:
            failed += 1

    messages.info(
        request,
        f"Email Dispatch Finished — Sent: {sent} | Failed: {failed} | Skipped: {skipped}"
    )

    return redirect("participant_list")


@login_required
def download_pdf(request, pk):
    participant = get_object_or_404(Participant, pk=pk)

    try:
        pdf_path = generate_pdf_certificate(participant)
        if not os.path.exists(pdf_path):
            raise Http404("PDF certificate file not found.")

        safe_name = participant.full_name.replace(" ", "_").replace("/", "_")
        return FileResponse(
            open(pdf_path, "rb"),
            as_attachment=True,
            filename=f"{participant.id}_{safe_name}_certificate.pdf"
        )
    except Exception as e:
        messages.error(request, f"Could not generate PDF: {e}")
        return redirect("participant_list")