# Design: Image + Audio → MP4 (Ken Burns)

**Date:** 2026-06-11
**Status:** Approved (pending spec review)

## Goal

A Python pipeline that pairs an image and an audio file sharing the same base
name and renders a high-quality MP4 into `output/`. The video shows the image
with a slow Ken Burns (zoom/pan) effect for the full duration of the audio.

Out of scope: lyrics (`lirycs/`) and character research (`run-books/`) are
manual inputs to the songwriting process, not consumed by this program.

## Inputs / Outputs

- **Input images:** `input/image/` — extensions `.jpg .jpeg .png .webp .bmp`
- **Input audio:** `input/audio/` — extensions `.mp3 .wav .flac .m4a .aac .ogg`
- **Output:** `output/<basename>.mp4`
- **Pairing rule:** match by base name (filename without extension),
  case-insensitive. `yusuke.png` + `yusuke.mp3` → `output/yusuke.mp4`.

## Video specification

- Resolution / aspect: **1920x1080 (16:9)**, 30 fps.
- Framing: **cover-and-crop** — scale the image to fill the frame, crop the
  overflow (no black bars; edges may be trimmed).
- Motion: **Ken Burns** zoom from 1.0 → ~1.1 across the whole song. To avoid
  the classic `zoompan` jitter, the image is pre-scaled to a large size before
  `zoompan`, then the output is rendered at 1080p.
- Video codec: H.264 (`libx264`), CRF 18, `yuv420p`, preset `slow`.
- Audio codec: AAC 320k (re-encoded from source for broad compatibility).

## ffmpeg dependency

Resolved automatically via the `imageio-ffmpeg` pip package. The binary path is
obtained with `imageio_ffmpeg.get_ffmpeg_exe()`; no manual system install is
required. Audio duration (needed to compute the number of Ken Burns frames) is
read with the `mutagen` pip package, which covers all supported audio formats.

## Architecture

Small, single-purpose modules under `src/`:

### `pairing.py`
Pure function. Given the two directory listings, returns:
- `pairs`: list of `(basename, image_path, audio_path)`
- `images_without_audio`: list of image paths
- `audio_without_image`: list of audio paths

Matching is by base name, case-insensitive. No filesystem side effects beyond
listing (listing can be injected for testability).

### `media.py`
`audio_duration(path) -> float` — returns duration in seconds using `mutagen`.
Raises a clear error if the file is unreadable / unsupported.

### `render.py`
- `build_ffmpeg_command(image, audio, output, duration, ffmpeg_exe, *, fps, ...)
  -> list[str]` — pure function that builds the full ffmpeg argument list
  (scale → zoompan → cover/crop to 1920x1080, H.264 settings, AAC audio,
  `-shortest`). No execution; this is the unit-tested surface.
- `render(...)` — calls the builder and runs it via `subprocess.run`, raising on
  non-zero exit with captured stderr.

### `main.py`
CLI entry point:
- Walks `pairing` output.
- For each pair: skip if `output/<name>.mp4` already exists (unless `--force`);
  otherwise read duration, build+run ffmpeg.
- Per-file progress messages; isolates per-pair failures (logs and continues).
- Final summary: generated / skipped / failed / unpaired counts.
- Exit code non-zero if any pair failed.

CLI flags: `--force` (re-render existing), `--input-image`, `--input-audio`,
`--output` (override default folders).

## Data flow

```
input/image + input/audio
        │
        ▼
   pairing.py ──► (pairs, images_without_audio, audio_without_image)
        │
        ▼  for each pair
   media.audio_duration ──► duration
        │
        ▼
   render.build_ffmpeg_command ──► render() ──► output/<name>.mp4
```

A failure on one pair is recorded and does not stop the others.

## Error handling

- Unpaired files are reported in the final summary, not treated as errors.
- A pair that fails to render (bad image, ffmpeg error, unreadable audio) is
  skipped, the error is logged with context, processing continues, and the
  program exits non-zero so failures are visible in automation.

## Testing strategy

TDD on the pure logic, no ffmpeg execution required:
- `pairing.py`: correct matching, case-insensitivity, multiple extensions,
  unpaired-file reporting.
- `render.build_ffmpeg_command`: asserts the produced argument list contains the
  expected filters/flags (resolution, codec, CRF, zoompan, `-shortest`, output
  path) for given inputs.

`media.audio_duration` and the real ffmpeg execution are validated manually with
a sample image+audio pair, since they depend on external binaries/files.

## Project setup

- `requirements.txt` (or `pyproject.toml`) pinning `imageio-ffmpeg` and
  `mutagen` (+ `pytest` for tests).
- `.gitkeep` files in `input/audio`, `input/image`, `lirycs`, `output`,
  `run-books` so the scaffold is tracked; `output/*.mp4` git-ignored.
- Runnable as `python -m src.main` (or a thin `src/main.py`).
