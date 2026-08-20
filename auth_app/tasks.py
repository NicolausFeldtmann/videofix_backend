from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.html import escape
from django.utils.http import urlsafe_base64_encode

from .email_utils import get_logo_html, get_logo_mime_image

User = get_user_model()


def send_activation_email(user_id):
    """Sends activation email via queue."""
    """Uses HTML-template to create and define email layout"""

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    activation_token = default_token_generator.make_token(user)
    frontend_link = f"{settings.FRONTEND_URL}/pages/auth/activate.html?uid={uidb64}&token={activation_token}"
    logo_html = get_logo_html()
    username_safe = escape(user.username)
    highlight_color = "#6500df"

    subject = "Activate Your Videoflix Account"
    text_message = (
        f"Hello {user.username},\n\n"
        f"Thank you for registering with Videoflix.\n\n"
        f"To complete your registration and verify your email address, please click the link below:\n"
        f"{frontend_link}\n\n"
        f"If you did not create an account with us, please disregard this email.\n\n"
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
    <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
            <div style="width: 100%;">
                {logo_html}
            </div>
            <div style="margin: 24px 0px;">
                <div style="margin: 24px 0px;">
                    Dear <span style="color:{highlight_color};">{username_safe}</span>,<br><br>
                    Thank you for registering with <span style="color:{highlight_color};">Videoflix</span>.
                    To complete your registration and verify your email address, please click the link below:
                </div>
                <div style="margin: 48px 0px;">
                    <a href="{frontend_link}" style="color: rgb(255, 255, 255); text-decoration: none; text-align: center; border-radius: 30px; background-color: #6500df; font-size: 24px; display: inline-block; padding: 12px 24px;">Activate account</a>
                </div>
                <p style="margin: 14px 0px;">If you did not create an account with us, please disregard this email.</p>
                <p style="margin: 14px 0px;">Best regards,</p>
                <p style="margin: 14px 0px;">Your Videoflix Team.</p>
            </div>
        </div>
    </body>
    </html>
    """

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    logo_attachment = get_logo_mime_image()
    if logo_attachment:
        email.attach(logo_attachment)

    email.attach_alternative(html_message, "text/html")
    email.send(fail_silently=False)
