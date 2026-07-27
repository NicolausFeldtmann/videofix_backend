from django.contrib.auth import get_user_model
from rest_framework import serializers
from auth_app.models import UserProfile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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