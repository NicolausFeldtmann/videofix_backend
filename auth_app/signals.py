from .models import UserProfile
from django.dispatch import Signal, receiver
from django.db.models.signals import post_save
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.html import escape
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.urls import reverse
from pathlib import Path
import base64

password_reset_requested = Signal()

def get_logo_base64():
    """Converts logo to Base64. For logo insertion for compatible email providers."""

    logo_path = Path(settings.BASE_DIR) / "static" / "images" / "logo.png"

    if logo_path.exists():
        with open(logo_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
        return None

@receiver(post_save, sender=UserProfile)
def send_link_post_save(sender, instance, created, **kwargs):
    """Handles content and sending of activation mail."""

    if not created:
        return

    user = instance.user
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    activation_token = default_token_generator.make_token(user)

    activation_path = reverse(
        "activate-account",
        kwargs={"uidb64": uidb64, "token": activation_token}
    )

    domain = settings.FRONTEND_URL
    protocol = "https" if not settings.DEBUG else "http"
    activation_url = f"{protocol}://{domain}{activation_path}"

    frontend_link = f"{settings.FRONTEND_URL}/pages/auth/activate.html?uid={uidb64}&token={activation_token}"

    logo_base64 = get_logo_base64()
    logo_html = ""

    if logo_base64:
        logo_html = f'<img src="data:image/png;base64,{logo_base64}" alt="Videoflix" style="max-width: 200px; height: auto;">'

    username_safe = escape(user.username)
    highlight_color = "#6500df"

    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content"width=device-width, initial-scale=1.0">
    </head>
        <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                <div style="width: 100%;">
                    {logo_html}
                </div>
                <div style="display: flex; margin: 24px 0px;">
                    <div style="margin: 24px 0px;">
                        Dear <span style="color:{highlight_color};">{username_safe}</span>,
                        <br><br>
                        Thank you for registering with <span style="color:{highlight_color}">Videoflix</span>
                        . To complete your registration and verify your email address, please click the link below:
                    </div>
                    <div style="margin: 48px 0px;">
                        <a href="{frontend_link}" style="color: rgb(255, 255, 255); text-decoration: none; text-align: center; border-radius: 30px; background-color: #6500df; font-size: 24px; 
                        display: flex; justify-content: flex-start; padding: 12px; margin: 24px 0px; width: 280px;">Activate account</a>
                    </div>
                    <p style="margin: 14px 0px;">If you did not create an account with us, please disregard this email.</p>
                    <p style="margin: 14px 0px;">Best regards,</p>
                    <p style="margin: 14px 0px">Your Videoflix Team.</p>
                </div>
            </div>
        </body>
    """

    send_mail(
        subject="Activate Your VideoFlix Account",
        message="Please activate your account by clicking the link in the HTML version of this email.",
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

@receiver(password_reset_requested)
def handle_password_reset(sender, user, **kwargs):
    """Sends password reset mail with auth-link to frontend.html."""

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    username_safe = escape(user.username)
    logo_base64 = get_logo_base64()
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" alt="Videoflix" style="max-width: 200px; height: auto;">'

    highlight_color = "#6500df"

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
                    Hello <span style="color:{highlight_color};">{username_safe}</span>,<br><br>
                    We recently received a request to reset your password. If you made this request, please click on the following link
                    to reset your password:
                </div>
                <div style="margin: 48px 0px; text-align: center;">
                    <a href="{reset_url}" style="color: rgb(255, 255, 255); text-decoration: none; text-align: center; border-radius: 30px; background-color: #6500df; font-size: 24px; 
                    display: inline-block; padding: 12px 24px;">Reset Password</a>
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

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email]
    )
    email.attach_alternative(html_message, "text/html")
    email.send(fail_silently=False)