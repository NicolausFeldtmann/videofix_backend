from django.contrib.auth import get_user_model
from rest_framework import serializers
from auth_app.models import UserProfile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer

User = get_user_model()

def validate_required_fields(attrs):
    email = attrs.get("email")
    password = attrs.get("password")

    if not email or not password:
        raise serializers.ValidationError("Email and password required.")
    
    return email, password

def get_user_by_email(email):
    try:
        return User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        raise serilaizers.ValidationError("Failed to login. Check email and password.")

def check_user_password(user, password):
    if not user.check_password(password):
        raise serializers.ValidationError("Failed to login. Check email and password.")

def check_profile_active(user):
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        raise serializers.ValidationError("Failed to login. Check email and password.")

    if profile.status != "active":
        raise serializers.ValidationError("No active account found. Please verify your email adress first.")

def get_jwt_tokens(serializer: TokenObtainPairSerializer, user, password):
    return super(TokenObtainPairSerializer, serializer).validate(
        {"username": user.username, "password": password}
    )

def get_access_token_from_refresh_cookie(request):
    """
    Liest den Refresh-Token aus dem Cookie, validiert ihn über SimpleJWT
    und gibt den neuen Access-Token zurück.
    Hebt bei Fehlern eine serializers.ValidationError aus.
    """
    refresh_token = request.COOKIES.get("refresh_token")
    if not refresh_token:
        raise serializers.ValidationError("Refresh token not found.")

    serializer = TokenRefreshSerializer(data={"refresh": refresh_token})
    try:
        serializer.is_valid(raise_exception=True)
    except Exception:
        raise serializers.ValidationError("Refresh token invalid.")

    access_token = serializer.validated_data.get("access")
    return access_token