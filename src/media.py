"""Read audio metadata (duration) using mutagen."""
from __future__ import annotations

from pathlib import Path

import mutagen


def audio_duration(path: Path) -> float:
    """Return the duration of an audio file in seconds.

    Raises ValueError if the file cannot be read as audio.
    """
    try:
        audio = mutagen.File(str(path))
    except mutagen.MutagenError as exc:
        raise ValueError(f"Unsupported or unreadable audio file: {path}") from exc
    if audio is None or audio.info is None:
        raise ValueError(f"Unsupported or unreadable audio file: {path}")
    return float(audio.info.length)
