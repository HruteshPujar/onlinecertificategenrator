from .utils import generate_certificate
from .pdf_utils import generate_pdf_certificate
from mailer.services import send_certificate_email


def generate_single_certificate(participant, base_url="http://127.0.0.1:8000"):
    """
    Generate PNG and PDF certificate for a participant.
    """
    # 1. Generate PNG
    png_path = generate_certificate(participant, base_url=base_url)

    # 2. Generate PDF
    pdf_path = generate_pdf_certificate(participant)

    return {
        "png_path": png_path,
        "pdf_path": pdf_path,
    }


def send_participant_email_service(participant):
    """
    Send the generated certificate via email to the participant.
    """
    if not participant.generated_certificate:
        generate_single_certificate(participant)
        participant.refresh_from_db()

    pdf_path = generate_pdf_certificate(participant)
    send_certificate_email(participant, pdf_path)

    participant.email_sent = True
    participant.save(update_fields=["email_sent"])
    return True