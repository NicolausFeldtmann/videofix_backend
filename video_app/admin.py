from django.contrib import admin
from .models import VideoModel

@admin.register(VideoModel)
class CustomAdmin(admin.ModelAdmin):
    list_filter = ["titel", "created_at", "category"]
    list_display = ["titel", "created_at", "category"]