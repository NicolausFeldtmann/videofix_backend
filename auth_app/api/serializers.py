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