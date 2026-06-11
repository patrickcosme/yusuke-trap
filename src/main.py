"""CLI: turn paired image+audio files into MP4 videos."""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from src import pairing
from src.media import audio_duration
from src.render import render


@dataclass
class Summary:
    generated: int = 0
    skipped: int = 0
    failed: int = 0
    unpaired_images: int = 0
    unpaired_audio: int = 0


def should_render(output: Path, force: bool, exists: bool) -> bool:
    return force or not exists


def run(image_dir: Path, audio_dir: Path, output_dir: Path, *, force: bool) -> Summary:
    images = pairing.list_media(image_dir, pairing.IMAGE_EXTS)
    audios = pairing.list_media(audio_dir, pairing.AUDIO_EXTS)
    result = pairing.match_pairs(images, audios)

    summary = Summary(
        unpaired_images=len(result.images_without_audio),
        unpaired_audio=len(result.audio_without_image),
    )

    for path in result.images_without_audio:
        print(f"[warn] image without audio: {path.name}")
    for path in result.audio_without_image:
        print(f"[warn] audio without image: {path.name}")

    for pair in result.pairs:
        output = output_dir / f"{pair.name}.mp4"
        if not should_render(output, force, output.exists()):
            print(f"[skip] {output.name} already exists")
            summary.skipped += 1
            continue
        try:
            duration = audio_duration(pair.audio)
            print(f"[render] {pair.name}.mp4 ({duration:.1f}s)")
            render(pair.image, pair.audio, output, duration)
            summary.generated += 1
        except Exception as exc:  # noqa: BLE001 - report and continue
            print(f"[fail] {pair.name}: {exc}")
            summary.failed += 1

    print(
        f"\nDone. generated={summary.generated} skipped={summary.skipped} "
        f"failed={summary.failed} unpaired_images={summary.unpaired_images} "
        f"unpaired_audio={summary.unpaired_audio}"
    )
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Turn paired image+audio into MP4 videos.")
    parser.add_argument("--input-image", default="input/image", type=Path)
    parser.add_argument("--input-audio", default="input/audio", type=Path)
    parser.add_argument("--output", default="output", type=Path)
    parser.add_argument("--force", action="store_true", help="re-render existing MP4s")
    args = parser.parse_args(argv)

    summary = run(args.input_image, args.input_audio, args.output, force=args.force)
    return 1 if summary.failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
