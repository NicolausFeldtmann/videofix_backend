from email.mime.image import MIMEImage
from pathlib import Path
from django.dispatch import Signal, receiver
from django.db import transaction
from django.db.models.signals import post_save
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.html import escape
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.urls import reverse
import django_rq

from .models import UserProfile
from .tasks import send_activation_email


LOGO_FILENAME = "logo_real.png"
LOGO_CID = "logo_cid"
HIGHLIGHT_COLOR = "#6500df"


from django.conf import settings

def get_logo_mime_image():
    """Loads logo directly from static-source."""
    logo_path = settings.BASE_DIR / "static" / "images" / LOGO_FILENAME

    if not logo_path.exists():
        return None

    with open(logo_path, "rb") as image_file:
        logo_data = image_file.read()

    image = MIMEImage(logo_data)
    image.add_header("Content-ID", f"<{LOGO_CID}>")
    image.add_header("Content-Disposition", "inline", filename=LOGO_FILENAME)
    return image

def get_logo_html():
    """Returns image-tag of imbeded logo."""

    return (
        f'<img src="cid:{LOGO_CID}" alt="Videoflix" '
        f'style="max-width: 200px; height: auto;">'
    )


def send_html_email(subject, text_message, html_message, recipient_email):
    """Builds and sends HTML email containing logo-image."""

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient_email],
    )
    email.attach_alternative(html_message, "text/html")

    logo_image = get_logo_mime_image()
    if logo_image:
        email.attach(logo_image)

    email.send(fail_silently=False)


password_reset_requested = Signal()


@receiver(post_save, sender=UserProfile)
def send_link_post_save(sender, instance, created, **kwargs):
    """Handles content and sending of activation mail."""

    if not created:
        return

    user_id = instance.user_id

    def enqueue_email():
        queue = django_rq.get_queue("default")
        queue.enqueue(send_activation_email, user_id)

    transaction.on_commit(enqueue_email)


@receiver(password_reset_requested)
def handle_password_reset(sender, user, **kwargs):
    """Sends password reset mail with auth-link to frontend.html."""

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    username_safe = escape(user.username)
    logo_html = get_logo_html()

    reset_url = f"{settings.FRONTEND_URL}/pages/auth/confirm_password.html?uid={uidb64}&token={token}"

    subject = "Videoflix - Password Reset"
    text_message = (
        f"Hello {user.username},\n\n"
        f"Please use the link below to change your password:\n"
        f"{reset_url}\n\n"
        f"This link is valid for 24 hours.\n\n"
        f"Best regards,\n"
        f"Your Videoflix Team"
    )

    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px">
        <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
            <div style="width: 100%;">
                {logo_html}
            </div>
            <div style="margin: 24px 0px;">
                <div style="margin: 24px 0px;">
                    Hello <span style="color:{HIGHLIGHT_COLOR};">{username_safe}</span>,<br><br>
                    We recently received a request to reset your password. If you made this request, please click on the following link
                    to reset your password:
                </div>
                <div style="margin: 48px 0px;">
                    <a href="{reset_url}" style="color: rgb(255, 255, 255); text-decoration: none; text-align: center; border-radius: 30px; background-color: #6500df; font-size: 24px; display: inline-block; padding: 12px 24px;">Reset Password</a>
                </div>
                <p style="margin: 14px 0px;">Please note that for security reasons, this link is only valid for 24 hours.</p>
                <p style="margin: 14px 0px;">If you did not request a password reset, please ignore this email.</p>
                <p style="margin: 14px 0px;">Best regards,</p>
                <p style="margin: 14px 0px;">Your Videoflix Team</p>
            </div>
        </div>
    </body>
    </html>
    """

    send_html_email(
        subject=subject,
        text_message=text_message,
        html_message=html_message,
        recipient_email=user.email,
    )