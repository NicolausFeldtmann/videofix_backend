from django.conf import settings
from django.db import models
from pathlib import Path

class VideoModel(models.Model):
    """Model class for videos and all needed fields ans fieldtypes."""

    title = models.CharField(max_length=30, default="")
    description = models.TextField(blank=True, default="", max_length=350)
    thumbnail_url = models.URLField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=20, default="")
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)

    HLS_RESOLUTIONS = {
        "480p": "854x480",
        "720p": "1280x720",
        "1080p": "1920x1080",
    }

    def __str__(self):
        return self.title