"""Build and run the ffmpeg command that turns an image + audio into an MP4."""
from __future__ import annotations

import subprocess
from pathlib import Path

import imageio_ffmpeg


def _video_filter(frames: int, fps: int, max_zoom: float) -> str:
    """Cover-crop to a 4K intermediate, apply Ken Burns, output 1920x1080.

    The 4K intermediate (force_original_aspect_ratio=increase + crop) removes
    black bars and gives zoompan enough resolution to avoid visible jitter.
    """
    zoom_step = 0.0008
    return (
        "[0:v]"
        "scale=3840:2160:force_original_aspect_ratio=increase,"
        "crop=3840:2160,"
        f"zoompan=z='min(zoom+{zoom_step},{max_zoom})':d={frames}"
        f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps={fps},"
        "setsar=1,format=yuv420p[v]"
    )


def build_ffmpeg_command(
    ffmpeg_exe: str,
    image: Path,
    audio: Path,
    output: Path,
    duration: float,
    *,
    fps: int = 30,
    max_zoom: float = 1.10,
    crf: int = 18,
    preset: str = "slow",
    audio_bitrate: str = "320k",
) -> list[str]:
    frames = max(1, round(duration * fps))
    return [
        ffmpeg_exe,
        "-y",
        "-loop", "1",
        "-i", str(image),
        "-i", str(audio),
        "-filter_complex", _video_filter(frames, fps, max_zoom),
        "-map", "[v]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-preset", preset,
        "-crf", str(crf),
        "-pix_fmt", "yuv420p",
        "-r", str(fps),
        "-c:a", "aac",
        "-b:a", audio_bitrate,
        "-shortest",
        str(output),
    ]


def render(
    image: Path,
    audio: Path,
    output: Path,
    duration: float,
    *,
    ffmpeg_exe: str | None = None,
) -> None:
    """Render one image+audio pair to `output`. Raises on ffmpeg failure."""
    exe = ffmpeg_exe or imageio_ffmpeg.get_ffmpeg_exe()
    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = build_ffmpeg_command(exe, image, audio, output, duration)
    subprocess.run(cmd, check=True, capture_output=True)
