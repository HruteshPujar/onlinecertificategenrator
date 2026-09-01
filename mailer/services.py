import logging
import os

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def send_certificate_email(participant, certificate_path):
    """
    Send certificate attachment email to participant.
    """
    subject = f"Certificate of Participation - {participant.event.title}"

    html_message = render_to_string(
        "mailer/certificate_email.html",
        {
            "participant": participant,
        }
    )

    plain_message = strip_tags(html_message)

    email = EmailMessage(
        subject=subject,
        body=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[participant.email],
    )

    email.content_subtype = "html"
    email.body = html_message

    if certificate_path and os.path.exists(certificate_path):
        email.attach_file(certificate_path)
    else:
        logger.warning(f"Certificate file not found at {certificate_path}, sending email without attachment.")

    try:
        email.send(fail_silently=False)
        logger.info(f"Email sent successfully to {participant.email}")
        return True
    except Exception as e:
        logger.error(f"Email failed for {participant.email}: {e}")
        raise e