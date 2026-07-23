import subprocess
from pathlib import Path

from .models import VideoModel


def convert_480(source):
    target = source + '480p.mp4'
    cmd = [
        'ffmpeg',
        '-y',
        '-i',
        source,
        '-s',
        'hd480',
        '-c:v',
        'libx264',
        '-crf',
        '23',
        '-c:a',
        'aac',
        '-strict',
        '-2',
        target,
    ]
    subprocess.run(cmd, check=True)


def generate_hls(source, resolution):
    if resolution not in VideoModel.HLS_RESOLUTIONS:
        raise ValueError(f"Unsupported resolution: {resolution}")

    source_path = Path(source)
    output_dir = source_path.parent / source_path.stem / resolution
    output_dir.mkdir(parents=True, exist_ok=True)

    playlist_path = output_dir / "index.m3u8"
    segment_pattern = output_dir / "segment_%03d.ts"

    cmd = [
        'ffmpeg',
        '-y',
        '-i',
        str(source_path),
        '-vf',
        f"scale={VideoModel.HLS_RESOLUTIONS[resolution]}",
        '-c:v',
        'libx264',
        '-crf',
        '23',
        '-preset',
        'veryfast',
        '-c:a',
        'aac',
        '-b:a',
        '128k',
        '-hls_time',
        '6',
        '-hls_playlist_type',
        'vod',
        '-hls_segment_filename',
        str(segment_pattern),
        str(playlist_path),
    ]
    subprocess.run(cmd, check=True)


def generate_hls_variants(source):
    for resolution in VideoModel.HLS_RESOLUTIONS:
        generate_hls(source, resolution)
