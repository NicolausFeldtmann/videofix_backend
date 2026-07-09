from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework import serializers
from auth_app.models import UserProfile

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):

    type = serializers.CharField(source='status')

    class Meta:
        model = UserProfile
        field = ["user", "email", "username"]

class RegistrationSerializer(serializers.ModelSerializer):
    confirmed_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        field = ["email", "password", "confirmed_password", "status"]

    def validate_email(self, value):
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Invalid email.")
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError({"Email allready in use."})
        return value

    def validate(self, data):
        if data.get("password") != data.get("confirmed_password"):
            raise serializers.ValidationError({"Passwords don't match."})
        return data

    def create(self, validated_data):
        username = validated_data.pop("username")
        email = validated_data.pop("email")
        password = validated_data.pop("password")
        status = validated_data.pop("status")

        user = User(username=username, email=email, password=password, status=status)
        user.set_password(password)
        user.save()

        UserProfile.objects.create(user=user, username=username, password=password, email=email)
        return user