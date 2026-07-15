from django.db import models

class VideoModel(models.Model):
    titel = models.CharField(max_length=30, default="")
    description = models.TextField(blank=True, default="", max_length=150)
    thumbnail_url = models.URLField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=20, default="")
    video_file = models.FileField(upload_to='video', blank=True, null=True)

    def __str__(self):
        return self.titel