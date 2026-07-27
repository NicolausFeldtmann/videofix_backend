from django.contrib import admin
from .models import VideoModel

@admin.register(VideoModel)
class CustomAdmin(admin.ModelAdmin):
    list_filter = ["title", "created_at", "category"]
    list_display = ["title", "created_at", "category"]