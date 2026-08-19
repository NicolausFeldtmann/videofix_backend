from email.mime.image import MIMEImage
from django.conf import settings

LOGO_FILENAME = "logo_real.png"
LOGO_CID = "logo_cid"

def get_logo_mime_image():
    """Loads logo and attaches it to email"""

    logo_path = settings.BASE_DIR / "static" / "images" / LOGO_FILENAME

    if not logo_path.exists():
        return None

    with open(logo_path, "rb") as image_file:
        logo_data = image_file.read()

    image = MIMEImage(logo_data)
    image.add_header("Content-ID", f"<{LOGO_CID}>")
    image.add_header(
        "Content-Disposition",
        "inline",
        filename=LOGO_FILENAME
    )

    return image

def get_logo_html():
    """Creates HTML-image for inline-logo."""

    return(
        f'<img src="cid:{LOGO_CID}" alt="Videoflix" '
        f'style="max-width: 200px; height: auto;">'
    )