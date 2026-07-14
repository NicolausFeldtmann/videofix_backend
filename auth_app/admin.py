from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfile(admin.ModelAdmin):
    list_display = ('__str__', "user", "email", "status")

    def get_user(self, obj):
        return obj.user
    get_user.short_description = 'User'