import django_rq
from django.http import HttpRequest
from typing import List, Optional
from pathlib import Path
from video_app.models import VideoModel
from video_app.tasks import generate_hls

def get_hls_base_dir(video: VideoModel) -> Optional[Path]:
    """Function to get base directory to return HLS versions of video."""

    if not video.video_file:
        return None
    video_path = Path(video.video_file.path)
    return video_path.parent / video_path.stem

def validate_and_get_base_dir(video: VideoModel, resolution: str) -> Path:
    """Validates existance of requested resolution. Calls 'get_hls_base_dir' function."""

    if resolution not in VideoModel.HLS_RESOLUTIONS:
        raise ValueError("Unsupported resolution")

    base_dir = get_hls_base_dir(video)
    if base_dir is None:
        raise ValueError("Video file path not available.")
    return base_dir

def safe_join(base: Path, *parts:str) -> Path:
    """Constructs path. Add parts to base and validates segment path"""

    p = (base.joinpath(*parts)).resolve()
    if base.resolve() not in p.parents and p != base.resolve():
        raise ValueError("Invalid segment path")
    return p

def get_hls_playlist_path(video: VideoModel, resolution: str) -> Path:
    """Calls 'validate_and_get_base' function. Validates resolution and returns path to playlist."""

    base = validate_and_get_base_dir(video, resolution)
    return base / resolution / "index.m3u8"

def get_hls_segment_path(video: VideoModel, resolution: str, segment_name: str) -> Path:
    """Validates resolution and video path. Creates and returns segment path (protection of path-traversal)."""

    base = validate_and_get_base_dir(video, resolution)
    return safe_join(base, resolution, segment_name)

def ensure_hls_for_resolution(video: VideoModel, resolution: str) -> bool:
    """Calls 'get_hls_for_resolution'. Generates hls if no playlist exists."""

    playlist = get_hls_playlist_path(video, resolution)
    if not playlist.exists():
        queue = django_rq.get_queue("default")
        queue.enqueue(generate_hls, video.video_file.path, resolution)
        return False
    return True

def ensure_hls_variants_queued(video: VideoModel, queue_name: str = "default") -> None:
    """Safty function. If playlist file is missing, sets generate hls prompt in queue."""

    queue = django_rq.get_queue(queue_name)
    for resolution in VideoModel.HLS_RESOLUTIONS:
        playlist = get_hls_playlist_path(video, resolution)
        if not playlist.exists():
            queue.enqueue(generate_hls, video.video_file.path, resolution)

def build_master_playlist_lines(video: VideoModel, request: HttpRequest) -> List[str]:
    """Starts master-playlist and defines bandwidth. Greates finaly playlist url"""

    lines = ["#EXTM3U"]
    bandwidth_map = {"360p": 800000, "480p": 1400000, "720p": 2800000}

    for resolution, size in VideoModel.HLS_RESOLUTIONS.items():
        width, height = size.split("x")
        bandwidth = bandwidth_map.get(resolution, 1000000)
        playlist_url = request.build_absolute_uri(f"/video/{video.pk}/{resolution}/index.m3u8")
        lines.append(f"#EXT-X-STREAM-INF:BANDWIDTH={bandwidth},RESOLUTION={width}x{height}")
        lines.append(playlist_url)
    return lines

def is_supported_resolution(resolution: str) -> bool:
    """Checks if requested resolution is supported by VideoModel"""

    return resolution in VideoModel.HLS_RESOLUTIONS

def get_playlist_or_enqueue(video: VideoModel, resolution: str, queue_name: str = "default") -> Optional[Path]:
    """Gets expectes playlist path. If not existing, sets creation prompt in queue."""

    playlist = get_hls_playlist_path(video, resolution)
    if playlist.exists():
        return playlist
    queue = django_rq.get_queue(queue_name)
    queue.enqueue(generate_hls, video.video_file.path, resolution)
    return None