from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase


class LoginViewTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="securepassword",
        )

    def test_login_accepts_email_and_password(self):
        response = self.client.post(
            reverse("token-obtain-pair"),
            {"email": "user@example.com", "password": "securepassword"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["detail"], "Login successful")
        self.assertEqual(response.json()["user"]["username"], "user@example.com")
