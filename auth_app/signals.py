from .models import UserProfile
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.test import RequestFactory

@receiver(post_save, sender=UserProfile)
def send_link_post_save(sender, instance, created, **kwargs):
    print("Account created")
    if created:
        user = instance.user
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        activation_token = default_token_generator.make_token(user)
        factory = RequestFactory()
        request = factory.get('/')
        activation_path = reverse(
            "activate-account",
            kwargs={"uidb64": uidb64, "token": activation_token}
        )
        domain = settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost'
        protocol = 'https' if not settings.DEBUG else 'http'
        activation_url = f"{request.scheme}://{request.get_host()}{activation_path}"

        send_mail(
            subject="Activate your Account.",
            message=(
                f"Hallo, \n\n"
                f"pleasae click the link to verify your email:\n"
                f"{activation_url}\n\n"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
        print("Verifiyation link send.")