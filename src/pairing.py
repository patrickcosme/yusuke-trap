"""Match image and audio files by their shared base name."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
AUDIO_EXTS = {".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg"}


@dataclass(frozen=True)
class Pair:
    name: str
    image: Path
    audio: Path


@dataclass(frozen=True)
class PairingResult:
    pairs: list[Pair]
    images_without_audio: list[Path]
    audio_without_image: list[Path]


def list_media(directory: Path, extensions: set[str]) -> list[Path]:
    """Return files in `directory` whose suffix is in `extensions` (case-insensitive)."""
    if not directory.is_dir():
        return []
    return sorted(
        p for p in directory.iterdir()
        if p.is_file() and p.suffix.lower() in extensions
    )


def match_pairs(images: list[Path], audios: list[Path]) -> PairingResult:
    images_by_stem = {p.stem.lower(): p for p in images}
    audios_by_stem = {p.stem.lower(): p for p in audios}

    pairs: list[Pair] = []
    for stem in sorted(images_by_stem.keys() & audios_by_stem.keys()):
        pairs.append(Pair(stem, images_by_stem[stem], audios_by_stem[stem]))

    images_without_audio = [
        images_by_stem[s] for s in sorted(images_by_stem.keys() - audios_by_stem.keys())
    ]
    audio_without_image = [
        audios_by_stem[s] for s in sorted(audios_by_stem.keys() - images_by_stem.keys())
    ]
    return PairingResult(pairs, images_without_audio, audio_without_image)
