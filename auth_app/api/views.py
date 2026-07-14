from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.shortcuts import get_object_or_404

from auth_app.models import UserProfile
from .serializers import UserProfileSerializer, RegistrationSerializer, EmailTokenObtainPairSerializer, PasswordResetConfirmSerializer, PasswordResetSerializer
from auth_app.signals import password_reset_requested

class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)

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

class CookieTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = EmailTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.user
        refresh = serializer.validated_data.get("refresh")
        access = serializer.validated_data.get("access")

        cookie_secure = not settings.DEBUG

        response = Response(
            {
                "detail": "Login successful",
                "user": {
                    "id": user.id,
                    "username": user.username,
                },
            },
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            key="access_token",
            value=access,
            httponly=True,
            secure=cookie_secure,
            samesite="Lax",
            path="/",
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh,
            httponly=True,
            secure=cookie_secure,
            samesite="Lax",
            path="/",
        )
        return response

class CookieRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token is None:
            return Response({"detail": "Refresh token not found."}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except:
            return Response({"detail": "Refresh token invalid"}, status=status.HTTP_401_UNAUTHORIZED)
        
        access_token = serializer.validated_data.get("access")
        cookie_secure = not settings.DEBUG
        response = Response({"detail": "Token refreshed."})
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=cookie_secure,
            samesite="Lax",
            path="/"
        )
        return response

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response(
            {"detail": "Logout successful"},
            status=status.HTTP_200_OK
        )
        
        response.delete_cookie(key="access_token", path="/")
        response.delete_cookie(key="refresh_token", path="/")
        
        return response

class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email__iexact=email)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            reset_token = default_token_generator.make_token(user)
            
            reset_path = reverse(
                "password-reset-confirm",
                kwargs={"uidb64": uidb64, "token": reset_token}
            )
            domain = settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost'
            protocol = 'https' if not settings.DEBUG else 'http'
            reset_url = f"{protocol}://{domain}{reset_path}"
            password_reset_requested.send(sender=PasswordResetView, user=user, reset_url=reset_url)

            return Response(
                {"detail": "Password-reset-link has been send."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        serializer = PasswordResetConfirmSerializer(data=request.data)

        if serializer.is_valid():
            try:
                uid = urlsafe_base64_decode(uidb64).decode()
                user = get_object_or_404(User, pk=uid)
            except (TypeError, ValueError, OverflowError):
                return Response(
                    {"detail": "Invalid reset-link"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not default_token_generator.check_token(user, token):
                return Response(
                    {"detail": "Reset token is invalid or expired."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            new_password = serializer.validated_data['new_password']
            user.set_password(new_password)
            user.save()

            return Response(
                {"detail": "Password successfully changed."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)