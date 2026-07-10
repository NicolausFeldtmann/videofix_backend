from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.shortcuts import get_object_or_404
from auth_app.models import UserProfile
from .serializers import UserProfileSerializer, RegistrationSerializer

class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            activation_token = default_token_generator.make_token(user)
            activation_path = reverse(
                "activate-account",
                kwargs={"uidb64": uidb64, "token": activation_token}
            )
            activation_url = f"{request.scheme}://{request.get_host()}{activation_path}"

            send_mail(
                subject="Activate your Account.",
                message=(
                    f"Almost done,\n\n"
                    f"please click the confirmation link to verify your email address:\n"
                    f"{activation_url}\n\n"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            data = {
                "user": {
                    "id": user.id,
                    "email": user.email,
                },
                "token": token.key
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ActivateAccountView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(User, pk=uid)
        except (TypeError, ValueError, OverflowError):
            return Response({"detail": "Invalid Activationslink"}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response(
                {"detail": "Activation token is invalid or expired."}, status=status.HTTP_400_BAD_REQUEST
            )

        profile = get_object_or_404(UserProfile, user=user)
        profile.status = "active"
        profile.save()
        return Response({"detail": "Account successfully activated"}, status=status.HTTP_200_OK)