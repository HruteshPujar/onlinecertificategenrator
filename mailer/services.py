import logging
import os

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def send_certificate_email(participant, certificate_path):
    """
    Send certificate PDF attachment email to participant.
    """
    if not participant.email:
        raise ValueError(f"Participant '{participant.full_name}' does not have an email address.")

    subject = f"🎓 Certificate of Participation - {participant.event.title}"

    # Render HTML template for the email body
    html_message = render_to_string(
        "mailer/certificate_email.html",
        {
            "participant": participant,
            "event": participant.event,
        }
    )

    plain_message = strip_tags(html_message)
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or getattr(settings, "EMAIL_HOST_USER", None) or "noreply@ocms.com"

    email = EmailMessage(
        subject=subject,
        body=html_message,
        from_email=from_email,
        to=[participant.email.strip()],
    )
    email.content_subtype = "html"

    # Attach PDF certificate with explicit MIME type and clean filename
    if certificate_path and os.path.exists(certificate_path):
        safe_name = "".join(c for c in participant.full_name if c.isalnum() or c in (' ', '_', '-')).strip().replace(" ", "_")
        pdf_filename = f"{safe_name}_Certificate.pdf"
        
        with open(certificate_path, "rb") as f:
            pdf_bytes = f.read()
            email.attach(pdf_filename, pdf_bytes, "application/pdf")
        logger.info(f"Attached PDF certificate ({len(pdf_bytes)} bytes) to email for {participant.email}")
    else:
        logger.warning(f"Certificate PDF file not found at {certificate_path}, sending email without attachment.")

    try:
        email.send(fail_silently=False)
        logger.info(f"Certificate email successfully dispatched to {participant.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to dispatch email to {participant.email}: {e}")
        raise e
