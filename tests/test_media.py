import wave
from pathlib import Path

from src.media import audio_duration


def _make_silent_wav(path: Path, seconds: float, framerate: int = 8000) -> None:
    frames = int(seconds * framerate)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(framerate)
        wav.writeframes(b"\x00\x00" * frames)


def test_audio_duration_reads_wav_length(tmp_path):
    wav_path = tmp_path / "tone.wav"
    _make_silent_wav(wav_path, seconds=0.5)

    duration = audio_duration(wav_path)

    assert abs(duration - 0.5) < 0.05


import pytest

from src.media import audio_duration


def test_audio_duration_rejects_non_audio(tmp_path):
    bad = tmp_path / "bad.mp3"
    bad.write_text("this is not audio")

    with pytest.raises(ValueError):
        audio_duration(bad)
