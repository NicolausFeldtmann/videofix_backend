# video_app/services.py
import django_rq
from django.http import HttpRequest
from typing import List, Optional
from pathlib import Path

from video_app.models import VideoModel
from video_app.tasks import generate_hls


def get_hls_base_dir(video: VideoModel) -> Optional[Path]:
    if not video.video_file:
        return None
    video_path = Path(video.video_file.path)
    return video_path.parent / video_path.stem


def get_hls_playlist_path(video: VideoModel, resolution: str) -> Path:
    if resolution not in VideoModel.HLS_RESOLUTIONS:
        raise ValueError(f"Unsupported resolution: {resolution}")
    base_dir = get_hls_base_dir(video)
    if base_dir is None:
        raise ValueError("Video file path not available.")
    return base_dir / resolution / "index.m3u8"


def get_hls_segment_path(video: VideoModel, resolution: str, segment_name: str) -> Path:
    if resolution not in VideoModel.HLS_RESOLUTIONS:
        raise ValueError(f"Unsupported resolution: {resolution}")
    base_dir = get_hls_base_dir(video)
    if base_dir is None:
        raise ValueError("Video file path not available.")

    segment_path = base_dir / resolution / segment_name
    resolved = segment_path.resolve()
    base_resolved = base_dir.resolve()

    # Sicherheitsprüfung
    if base_resolved not in resolved.parents and resolved.parent.parent != base_resolved:
        raise ValueError("Invalid segment path")
    return segment_path


def ensure_hls_for_resolution(video: VideoModel, resolution: str) -> bool:
    playlist = get_hls_playlist_path(video, resolution)
    if not playlist.exists():
        queue = django_rq.get_queue("default")
        queue.enqueue(generate_hls, video.video_file.path, resolution)
        return False
    return True


def resolve_segment_path(video: VideoModel, resolution: str, segment: str) -> Path:
    return get_hls_segment_path(video, resolution, segment)


def ensure_hls_variants_queued(video: VideoModel, queue_name: str = "default") -> None:
    queue = django_rq.get_queue(queue_name)
    for resolution in VideoModel.HLS_RESOLUTIONS:
        playlist = get_hls_playlist_path(video, resolution)
        if not playlist.exists():
            queue.enqueue(generate_hls, video.video_file.path, resolution)


def build_master_playlist_lines(video: VideoModel, request: HttpRequest) -> List[str]:
    lines = ["#EXTM3U"]
    bandwidth_map = {"360p": 800000, "480p": 1400000, "720p": 2800000}

    for resolution, size in VideoModel.HLS_RESOLUTIONS.items():
        width, height = size.split("x")
        bandwidth = bandwidth_map.get(resolution, 1000000)
        playlist_url = request.build_absolute_uri(
            f"/video/{video.pk}/{resolution}/index.m3u8"
        )
        lines.append(
            f"#EXT-X-STREAM-INF:BANDWIDTH={bandwidth},RESOLUTION={width}x{height}"
        )
        lines.append(playlist_url)
    return lines


def is_supported_resolution(resolution: str) -> bool:
    return resolution in VideoModel.HLS_RESOLUTIONS


def get_playlist_or_enqueue(
    video: VideoModel, resolution: str, queue_name: str = "default"
) -> Optional[Path]:
    playlist = get_hls_playlist_path(video, resolution)
    if playlist.exists():
        return playlist
    queue = django_rq.get_queue(queue_name)
    queue.enqueue(generate_hls, video.video_file.path, resolution)
    return None
