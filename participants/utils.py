import os
import uuid

try:
    import qrcode
except ImportError:
    qrcode = None

from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from verification.models import CertificateVerification



def get_font(size=40, bold=False):
    """
    Safely load a TrueType font with fallback.
    """
    font_candidates = [
        os.path.join(settings.MEDIA_ROOT, "fonts", "arial.ttf"),
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]

    for candidate in font_candidates:
        if os.path.exists(candidate):
            try:
                return ImageFont.truetype(candidate, size)
            except Exception:
                continue

    try:
        return ImageFont.load_default()
    except Exception:
        return None


def create_default_template(width=1920, height=1080):
    """
    Generate an elegant, professional certificate template background if none uploaded.
    """
    img = Image.new("RGB", (width, height), color="#FDFDFE")
    draw = ImageDraw.Draw(img)

    # Outer decorative borders
    border_color_gold = "#C5A059"
    border_color_navy = "#1B2A4A"

    # Outer dark navy frame
    draw.rectangle([(20, 20), (width - 20, height - 20)], outline=border_color_navy, width=6)
    # Inner gold border
    draw.rectangle([(36, 36), (width - 36, height - 36)], outline=border_color_gold, width=3)
    # Thin inner border
    draw.rectangle([(48, 48), (width - 48, height - 48)], outline=border_color_navy, width=1)

    # Corner ornaments
    corner_size = 40
    for cx, cy in [(48, 48), (width - 48 - corner_size, 48), 
                   (48, height - 48 - corner_size), (width - 48 - corner_size, height - 48 - corner_size)]:
        draw.rectangle([(cx, cy), (cx + corner_size, cy + corner_size)], outline=border_color_gold, width=2)

    # Top header badge / title
    header_font = get_font(52, bold=True)
    sub_font = get_font(24)

    title_text = "CERTIFICATE OF PARTICIPATION"
    sub_title = "PROUDLY PRESENTED TO"

    # Draw header text centered
    if header_font:
        bbox = draw.textbbox((0, 0), title_text, font=header_font)
        tw = bbox[2] - bbox[0]
        draw.text(((width - tw) / 2, 130), title_text, fill=border_color_navy, font=header_font)

    if sub_font:
        bbox = draw.textbbox((0, 0), sub_title, font=sub_font)
        tw = bbox[2] - bbox[0]
        draw.text(((width - tw) / 2, 220), sub_title, fill=border_color_gold, font=sub_font)

    # Decorative dividing line below header
    draw.line([(width * 0.25, 200), (width * 0.75, 200)], fill=border_color_gold, width=2)

    return img


def generate_certificate(participant, base_url="http://127.0.0.1:8000"):
    """
    Generate certificate PNG with participant details, event details, and verification QR code.
    """
    event = participant.event

    # 1. Open or generate base template
    template_exists = False
    if event.certificate_template:
        try:
            template_path = event.certificate_template.path
            if os.path.exists(template_path):
                image = Image.open(template_path).convert("RGB")
                template_exists = True
        except Exception:
            template_exists = False

    if not template_exists:
        image = create_default_template(1920, 1080)

    draw = ImageDraw.Draw(image)
    width, height = image.size

    # 2. Setup verification record
    verification, _ = CertificateVerification.objects.get_or_create(
        participant=participant,
        defaults={
            "verification_code": str(uuid.uuid4())
        }
    )

    verification_code = verification.verification_code

    # 3. Load Fonts
    name_font_size = getattr(event, "name_font_size", 60) or 60
    event_font_size = getattr(event, "event_font_size", 38) or 38
    date_font_size = getattr(event, "date_font_size", 26) or 26

    name_font = get_font(name_font_size, bold=True)
    event_font = get_font(event_font_size, bold=True)
    desc_font = get_font(date_font_size)
    small_font = get_font(18)

    # 4. Render Participant Name
    participant_name = participant.full_name.strip()
    name_x = getattr(event, "name_x", 0)
    name_y = getattr(event, "name_y", 0)

    if name_font:
        n_bbox = draw.textbbox((0, 0), participant_name, font=name_font)
        n_width = n_bbox[2] - n_bbox[0]

        if name_x > 0 and name_y > 0:
            final_name_x = name_x
            final_name_y = name_y
        else:
            final_name_x = (width - n_width) / 2
            final_name_y = height * 0.35 if not template_exists else height * 0.50

        # Draw participant name
        draw.text((final_name_x, final_name_y), participant_name, fill="#1B2A4A", font=name_font)

        # Draw decorative underline if default template
        if not template_exists:
            line_y = final_name_y + (n_bbox[3] - n_bbox[1]) + 15
            draw.line([(width * 0.20, line_y), (width * 0.80, line_y)], fill="#C5A059", width=2)

    # 5. Render Event & Description (for default template or if coordinates provided)
    event_x = getattr(event, "event_x", 0)
    event_y = getattr(event, "event_y", 0)

    if not template_exists:
        # Default layout description
        desc_text = "for active and successful participation in"
        if desc_font:
            d_bbox = draw.textbbox((0, 0), desc_text, font=desc_font)
            draw.text(((width - (d_bbox[2] - d_bbox[0])) / 2, height * 0.50), desc_text, fill="#555555", font=desc_font)

        event_title = event.title
        if event_font:
            e_bbox = draw.textbbox((0, 0), event_title, font=event_font)
            draw.text(((width - (e_bbox[2] - e_bbox[0])) / 2, height * 0.58), event_title, fill="#1B2A4A", font=event_font)

        # Event date and venue
        date_str = f"Date: {event.event_date.strftime('%B %d, %Y')} | Venue: {event.venue}"
        if desc_font:
            date_bbox = draw.textbbox((0, 0), date_str, font=desc_font)
            draw.text(((width - (date_bbox[2] - date_bbox[0])) / 2, height * 0.68), date_str, fill="#4A6FA5", font=desc_font)

        # College / Department info if available
        if participant.college or participant.department:
            info_str = f"{participant.department} - {participant.college}" if participant.department else participant.college
            if small_font:
                i_bbox = draw.textbbox((0, 0), info_str, font=small_font)
                draw.text(((width - (i_bbox[2] - i_bbox[0])) / 2, height * 0.44), info_str, fill="#777777", font=small_font)

    elif event_x > 0 and event_y > 0 and event_font:
        draw.text((event_x, event_y), event.title, fill="#1B2A4A", font=event_font)

    # 6. Render Certificate ID / Verification code text
    cert_id_x = getattr(event, "certificate_id_x", 0)
    cert_id_y = getattr(event, "certificate_id_y", 0)
    cert_id_text = f"Certificate ID: {verification_code[:13]}"

    if cert_id_x > 0 and cert_id_y > 0 and small_font:
        draw.text((cert_id_x, cert_id_y), cert_id_text, fill="#333333", font=small_font)
    elif small_font:
        draw.text((80, height - 100), cert_id_text, fill="#666666", font=small_font)

    # 7. Generate and Paste QR Code
    verification_url = f"{base_url.rstrip('/')}/verify/{verification_code}/"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=5,
        border=2,
    )
    qr.add_data(verification_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#1B2A4A", back_color="white").convert("RGB")
    qr_img = qr_img.resize((150, 150))

    # Paste QR at bottom-right corner with margin
    qr_x = width - 230
    qr_y = height - 230
    image.paste(qr_img, (qr_x, qr_y))

    if small_font:
        qr_label = "Scan to Verify"
        ql_bbox = draw.textbbox((0, 0), qr_label, font=small_font)
        ql_w = ql_bbox[2] - ql_bbox[0]
        draw.text((qr_x + (150 - ql_w) / 2, qr_y + 155), qr_label, fill="#666666", font=small_font)

    # 8. Save PNG Output
    output_folder = os.path.join(settings.MEDIA_ROOT, "certificates")
    os.makedirs(output_folder, exist_ok=True)

    safe_name = participant.full_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    filename = f"{participant.id}_{safe_name}.png"
    output_path = os.path.join(output_folder, filename)

    image.save(output_path, "PNG", quality=95)

    # 9. Update participant record
    participant.generated_certificate = f"certificates/{filename}"
    participant.certificate_generated = True
    participant.save(update_fields=["generated_certificate", "certificate_generated"])

    return output_path