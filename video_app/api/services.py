import os
import django_rq
from pathlib import Path
from video_app.models import VideoModel
from video_app.tasks import generate_hls

def ensure_hls_for_resolution(video: VideoModel, resolution: str):
    playlist = video.get_hls_playlist_path(resolution)
    if not (playlist and playlist.exists()):
        queue = django_rq.get_queue("default")
        queue.enqueue(generate_hls, video.video_file.path, resolution)
        return False
    return True

def resolve_segemtn_path(video: VideoModel, resolution: str, segment: str) -> Path:
    return video.get_hls_segment_path(resolution, segment)