import os
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from django.conf import settings
from .utils import generate_certificate


def generate_pdf_certificate(participant):
    """
    Generate PDF version of the participant's certificate.
    """
    # Ensure PNG certificate exists
    if not participant.generated_certificate:
        generate_certificate(participant)
        participant.refresh_from_db()

    png_path = participant.generated_certificate.path
    if not os.path.exists(png_path):
        generate_certificate(participant)
        participant.refresh_from_db()
        png_path = participant.generated_certificate.path

    # PDF folder
    pdf_folder = os.path.join(
        settings.MEDIA_ROOT,
        "certificates",
        "pdf"
    )
    os.makedirs(pdf_folder, exist_ok=True)

    # PDF filename
    filename = os.path.basename(png_path).replace(".png", ".pdf")
    pdf_path = os.path.join(pdf_folder, filename)

    # Read PNG and create PDF with identical dimensions
    image = ImageReader(png_path)
    width, height = image.getSize()

    pdf = canvas.Canvas(pdf_path, pagesize=(width, height))
    pdf.drawImage(image, 0, 0, width=width, height=height)
    pdf.save()

    return pdf_path