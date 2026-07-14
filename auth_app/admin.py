from django.contrib import admin
from .models import UserProfile

class CustomAdmin(admin.ModelAdmin):
    list_filter = ["user", "email", "status"]
    list_display = ["user", "email", "status"]

admin.site.register(UserProfile, CustomAdmin)