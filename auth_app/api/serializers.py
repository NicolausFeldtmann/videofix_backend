from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from auth_app.models import UserProfile

from . import services

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):

    type = serializers.CharField(source='status')

    class Meta:
        model = UserProfile
        fields = ["user", "email"]

class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirmed_password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Invalid email.")
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already in use.")
        return value

    def validate(self, data):
        if data['password'] != data["confirmed_password"]:
            raise serializers.ValidationError("Passwords don't match.")
        return data

    def create(self, validated_data):
        email = validated_data["email"]
        password = validated_data["password"]

        user = User(username=email, email=email)
        user.set_password(password)
        user.save()

        UserProfile.objects.create(user=user, email=email)
        return user

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("username", None)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        email, oassword = services.validate_required_fields(attrs)
        user = services.get_user_by_email(email)
        services.check_user_password(user, password)
        services.check_profile_active(user)
        data = services.get_jwt_tokens(self, user, password)

        self.user = user
        return data

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email__iexact=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Email not found.")
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Password don't match")
        return data