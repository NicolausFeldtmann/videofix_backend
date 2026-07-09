from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):

    USER_STATUS = [
        ("active", "Active"),
        ("inactive", "Inactive")
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=50, default="")
    email = models.EmailField(max_length=50)
    status = models.CharField(max_length=20, choices=USER_STATUS, default="inactive")
    
    def username(self):
        return f"{self.email}".strip()