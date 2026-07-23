from django.conf import settings
from django.db import models
from pathlib import Path

class VideoModel(models.Model):
    titel = models.CharField(max_length=30, default="")
    description = models.TextField(blank=True, default="", max_length=150)
    thumbnail_url = models.URLField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=20, default="")
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)

    HLS_RESOLUTIONS = {
        "360p": "640x360",
        "480p": "854x480",
        "720p": "1280x720",
    }

    @property
    def hls_base_dir(self):
        if not self.video_file:
            return None
        video_path = Path(self.video_file.path)
        # Gibt das Verzeichnis zurück, in dem die Videodatei liegt
        # plus den Namen der Videodatei ohne Extension
        return video_path.parent / video_path.stem

    def get_hls_playlist_path(self, resolution):
        if resolution not in self.HLS_RESOLUTIONS:
            raise ValueError(f"Unsupported resolution: {resolution}")
        # Rückgabe: /app/env/media/videos/videoname/480p/index.m3u8
        playlist_path = self.hls_base_dir / resolution / "index.m3u8"
        return playlist_path

    def get_hls_segment_path(self, resolution, segment_name):
        if resolution not in self.HLS_RESOLUTIONS:
            raise ValueError(f"Unsupported resolution: {resolution}")
        # Rückgabe: /app/env/media/videos/videoname/480p/segment_xxx.ts
        segment_path = self.hls_base_dir / resolution / segment_name
        
        resolved = segment_path.resolve()
        base_resolved = self.hls_base_dir.resolve()

        # Sicherheitsprüfung gegen Directory Traversal
        if base_resolved not in resolved.parents and resolved.parent.parent != base_resolved:
            raise ValueError("Invalid segment path")
        
        return segment_path

    def __str__(self):
        return self.titel
