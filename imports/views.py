import pandas as pd
import io

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse

from .forms import ExcelUploadForm
from participants.models import Participant
from events.models import Event


def normalize_col(col):
    return str(col).strip().lower().replace(" ", "_").replace("-", "_")


def find_column(df_columns, candidates):
    norm_map = {normalize_col(c): c for c in df_columns}
    for cand in candidates:
        if cand in norm_map:
            return norm_map[cand]
    return None


@login_required
def import_participants(request):
    if request.method == "POST":
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.cleaned_data["event"]
            uploaded_file = request.FILES["file"]
            filename = uploaded_file.name.lower()

            try:
                if filename.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                elif filename.endswith((".xlsx", ".xls")):
                    df = pd.read_excel(uploaded_file)
                else:
                    messages.error(request, "Unsupported file format. Please upload an Excel (.xlsx, .xls) or CSV (.csv) file.")
                    return render(request, "imports/import_participants.html", {"form": form})
            except Exception as e:
                messages.error(request, f"Unable to read uploaded file: {e}")
                return render(request, "imports/import_participants.html", {"form": form})

            # Clean NaN values
            df = df.fillna("")

            # Resolve column mappings flexibly
            col_name = find_column(df.columns, ["full_name", "name", "participant_name", "student_name", "candidate_name"])
            col_email = find_column(df.columns, ["email", "email_address", "mail", "e_mail"])
            col_phone = find_column(df.columns, ["phone", "mobile", "contact", "phone_number", "mobile_number"])
            col_college = find_column(df.columns, ["college", "institution", "university", "institute", "school", "organization"])
            col_dept = find_column(df.columns, ["department", "dept", "branch", "stream"])
            col_usn = find_column(df.columns, ["usn", "roll_no", "roll_number", "registration_no", "reg_no", "id"])

            if not col_name or not col_email:
                messages.error(
                    request,
                    "File must contain at least 'Full Name' (or Name) and 'Email' columns. Found columns: "
                    + ", ".join(list(df.columns))
                )
                return render(request, "imports/import_participants.html", {"form": form})

            # Check existing records for this event
            existing_emails = set(
                Participant.objects.filter(event=event).values_list("email", flat=True)
            )
            existing_usns = set(
                Participant.objects.filter(event=event).exclude(usn__isnull=True).exclude(usn="").values_list("usn", flat=True)
            )

            participants_to_create = []
            added = 0
            skipped = 0
            failed = 0

            for _, row in df.iterrows():
                try:
                    full_name = str(row[col_name]).strip()
                    email = str(row[col_email]).strip().lower()
                    phone = str(row[col_phone]).strip() if col_phone else ""
                    college = str(row[col_college]).strip() if col_college else ""
                    department = str(row[col_dept]).strip() if col_dept else ""
                    usn = str(row[col_usn]).strip() if col_usn else ""

                    # Clean float strings like "12345.0" for phone or usn if present
                    if phone.endswith(".0") and phone[:-2].isdigit():
                        phone = phone[:-2]
                    if usn.endswith(".0") and usn[:-2].isdigit():
                        usn = usn[:-2]

                    if not full_name or not email or "@" not in email:
                        failed += 1
                        continue

                    if email in existing_emails:
                        skipped += 1
                        continue

                    if usn and usn in existing_usns:
                        skipped += 1
                        continue

                    participant = Participant(
                        event=event,
                        full_name=full_name,
                        email=email,
                        phone=phone,
                        college=college,
                        department=department,
                        usn=usn or None,
                    )
                    participants_to_create.append(participant)
                    existing_emails.add(email)
                    if usn:
                        existing_usns.add(usn)
                    added += 1

                except Exception:
                    failed += 1

            if participants_to_create:
                with transaction.atomic():
                    Participant.objects.bulk_create(participants_to_create)

            messages.success(
                request,
                f"Import summary for '{event.title}': {added} added successfully, {skipped} duplicates skipped, {failed} invalid rows ignored."
            )
            return redirect(f"/participants/?event={event.id}")
    else:
        initial_event = Event.objects.filter(is_active=True).order_by("-id").first()
        form = ExcelUploadForm(initial={"event": initial_event})

    return render(
        request,
        "imports/import_participants.html",
        {
            "form": form,
        },
    )


@login_required
def download_sample_template(request):
    """
    Generate and download a sample CSV template for participant import.
    """
    csv_content = "full_name,email,phone,college,department,usn\nJohn Doe,john@example.com,9876543210,Oxford College,Computer Science,1OX20CS001\nJane Smith,jane@example.com,9876543211,Stanford University,Information Science,1ST20IS002\n"
    response = HttpResponse(csv_content, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="participants_sample_template.csv"'
    return response