# Image + Audio → MP4 (Ken Burns) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Pair an image and an audio file sharing the same base name and render a high-quality 1080p MP4 with a Ken Burns effect into `output/`.

**Architecture:** A small Python pipeline of single-purpose modules under `src/`: `pairing` (pure matching), `media` (audio duration via mutagen), `render` (pure ffmpeg-command builder + subprocess runner), and `main` (CLI orchestration). ffmpeg is supplied by the `imageio-ffmpeg` pip package, so no manual install is needed.

**Tech Stack:** Python 3.12, `imageio-ffmpeg==0.6.0` (bundled ffmpeg binary), `mutagen==1.47.0` (audio duration), `pytest` (tests).

---

## File Structure

- `requirements.txt` — pinned dependencies.
- `.gitignore` — ignore generated `output/*.mp4`, venv, pycache.
- `src/__init__.py` — marks `src` as a package.
- `src/pairing.py` — list media files and match image/audio by base name. Pure logic.
- `src/media.py` — `audio_duration(path)` via mutagen.
- `src/render.py` — `build_ffmpeg_command(...)` (pure) + `render(...)` (subprocess).
- `src/main.py` — CLI entry point, orchestration, summary, exit code.
- `tests/__init__.py` — marks `tests` as a package.
- `tests/test_pairing.py` — pairing unit tests.
- `tests/test_media.py` — duration test using a stdlib-generated WAV.
- `tests/test_render.py` — ffmpeg-command-builder unit tests.
- `tests/test_main.py` — render-decision helper unit tests.
- `.gitkeep` in `input/audio`, `input/image`, `lirycs`, `output`, `run-books`.

---

## Task 1: Project setup

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `src/__init__.py`
- Create: `tests/__init__.py`
- Create: `input/audio/.gitkeep`, `input/image/.gitkeep`, `lirycs/.gitkeep`, `output/.gitkeep`, `run-books/.gitkeep`

- [ ] **Step 1: Create `requirements.txt`**

```text
imageio-ffmpeg==0.6.0
mutagen==1.47.0
pytest==8.3.4
```

- [ ] **Step 2: Create `.gitignore`**

```gitignore
__pycache__/
*.pyc
.venv/
venv/
.pytest_cache/
output/*.mp4
```

- [ ] **Step 3: Create empty package markers**

Create `src/__init__.py` with a single line:

```python
"""yusuke-trap: image + audio -> MP4 pipeline."""
```

Create `tests/__init__.py` as an empty file (no content).

- [ ] **Step 4: Create `.gitkeep` files**

Create these five empty files so the scaffold is tracked:
`input/audio/.gitkeep`, `input/image/.gitkeep`, `lirycs/.gitkeep`, `output/.gitkeep`, `run-books/.gitkeep`

- [ ] **Step 5: Create and activate a virtualenv, install deps**

Run (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```
Expected: installs imageio-ffmpeg, mutagen, pytest without errors.

- [ ] **Step 6: Verify pytest runs (no tests yet)**

Run: `.\.venv\Scripts\python.exe -m pytest -q`
Expected: `no tests ran` (exit code 5 is fine at this point).

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "chore: project setup (deps, gitignore, scaffold)"
```

---

## Task 2: Pairing module

**Files:**
- Create: `src/pairing.py`
- Test: `tests/test_pairing.py`

Defines the supported extensions, a directory lister, and the pure matching function. Public API:
- `IMAGE_EXTS: set[str]`, `AUDIO_EXTS: set[str]`
- `list_media(directory: Path, extensions: set[str]) -> list[Path]`
- `match_pairs(images: list[Path], audios: list[Path]) -> PairingResult`
- `PairingResult` dataclass with `pairs: list[Pair]`, `images_without_audio: list[Path]`, `audio_without_image: list[Path]`
- `Pair` dataclass with `name: str`, `image: Path`, `audio: Path`

- [ ] **Step 1: Write the failing test**

Create `tests/test_pairing.py`:
```python
from pathlib import Path

from src.pairing import match_pairs


def test_matches_same_basename_case_insensitive():
    images = [Path("input/image/Yusuke.PNG"), Path("input/image/kuwabara.jpg")]
    audios = [Path("input/audio/yusuke.mp3"), Path("input/audio/hiei.wav")]

    result = match_pairs(images, audios)

    assert len(result.pairs) == 1
    pair = result.pairs[0]
    assert pair.name == "yusuke"
    assert pair.image == Path("input/image/Yusuke.PNG")
    assert pair.audio == Path("input/audio/yusuke.mp3")
    assert result.images_without_audio == [Path("input/image/kuwabara.jpg")]
    assert result.audio_without_image == [Path("input/audio/hiei.wav")]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_pairing.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'src.pairing'`.

- [ ] **Step 3: Write minimal implementation**

Create `src/pairing.py`:
```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_pairing.py -v`
Expected: PASS.

- [ ] **Step 5: Add an extension-filter test for `list_media`**

Append to `tests/test_pairing.py`:
```python
from src.pairing import list_media, IMAGE_EXTS


def test_list_media_filters_by_extension(tmp_path):
    (tmp_path / "a.png").write_bytes(b"x")
    (tmp_path / "b.JPG").write_bytes(b"x")
    (tmp_path / "notes.txt").write_bytes(b"x")

    found = list_media(tmp_path, IMAGE_EXTS)

    names = sorted(p.name for p in found)
    assert names == ["a.png", "b.JPG"]
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_pairing.py -v`
Expected: PASS (2 tests).

- [ ] **Step 7: Commit**

```bash
git add src/pairing.py tests/test_pairing.py
git commit -m "feat: pair image and audio files by base name"
```

---

## Task 3: Media duration module

**Files:**
- Create: `src/media.py`
- Test: `tests/test_media.py`

`audio_duration(path: Path) -> float` returns the audio length in seconds using mutagen. The test generates a real 0.5s silent WAV with the stdlib `wave` module (no ffmpeg needed), which mutagen can read.

- [ ] **Step 1: Write the failing test**

Create `tests/test_media.py`:
```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_media.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'src.media'`.

- [ ] **Step 3: Write minimal implementation**

Create `src/media.py`:
```python
"""Read audio metadata (duration) using mutagen."""
from __future__ import annotations

from pathlib import Path

import mutagen


def audio_duration(path: Path) -> float:
    """Return the duration of an audio file in seconds.

    Raises ValueError if the file cannot be read as audio.
    """
    audio = mutagen.File(str(path))
    if audio is None or audio.info is None:
        raise ValueError(f"Unsupported or unreadable audio file: {path}")
    return float(audio.info.length)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_media.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/media.py tests/test_media.py
git commit -m "feat: read audio duration via mutagen"
```

---

## Task 4: Render module (command builder + runner)

**Files:**
- Create: `src/render.py`
- Test: `tests/test_render.py`

Two functions:
- `build_ffmpeg_command(ffmpeg_exe, image, audio, output, duration, *, fps=30, max_zoom=1.10, crf=18, preset="slow", audio_bitrate="320k") -> list[str]` — pure; builds the full argument list. The video filter does cover-and-crop to a 4K intermediate (smooths zoompan), applies Ken Burns, and outputs 1920x1080.
- `render(image, audio, output, duration, *, ffmpeg_exe=None) -> None` — builds the command and runs it via `subprocess.run(..., check=True)`. Not unit-tested (needs the real binary); validated manually in Task 6.

The number of Ken Burns frames is `max(1, round(duration * fps))`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_render.py`:
```python
from pathlib import Path

from src.render import build_ffmpeg_command


def test_build_ffmpeg_command_has_expected_parts():
    cmd = build_ffmpeg_command(
        ffmpeg_exe="ffmpeg",
        image=Path("input/image/yusuke.png"),
        audio=Path("input/audio/yusuke.mp3"),
        output=Path("output/yusuke.mp4"),
        duration=10.0,
        fps=30,
    )

    assert cmd[0] == "ffmpeg"
    # input image is looped, then the audio is a second input
    assert "-loop" in cmd
    assert str(Path("input/image/yusuke.png")) in cmd
    assert str(Path("input/audio/yusuke.mp3")) in cmd
    # output path is the final argument
    assert cmd[-1] == str(Path("output/yusuke.mp4"))
    # codec/quality settings
    assert "libx264" in cmd
    assert "-crf" in cmd and "18" in cmd
    assert "yuv420p" in cmd
    assert "-shortest" in cmd
    # the filter chain does Ken Burns and outputs 1080p
    filter_arg = cmd[cmd.index("-filter_complex") + 1]
    assert "zoompan" in filter_arg
    assert "s=1920x1080" in filter_arg
    # frames = round(duration * fps) = 300
    assert "d=300" in filter_arg


def test_build_ffmpeg_command_frames_never_zero():
    cmd = build_ffmpeg_command(
        ffmpeg_exe="ffmpeg",
        image=Path("a.png"),
        audio=Path("a.mp3"),
        output=Path("a.mp4"),
        duration=0.0,
        fps=30,
    )
    filter_arg = cmd[cmd.index("-filter_complex") + 1]
    assert "d=1" in filter_arg
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_render.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'src.render'`.

- [ ] **Step 3: Write minimal implementation**

Create `src/render.py`:
```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_render.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add src/render.py tests/test_render.py
git commit -m "feat: build and run ffmpeg Ken Burns command"
```

---

## Task 5: CLI orchestration

**Files:**
- Create: `src/main.py`
- Test: `tests/test_main.py`

`main.py` ties everything together. A pure helper `should_render(output, force, exists)` is unit-tested; the rest is orchestration validated in Task 6.

- `should_render(output: Path, force: bool, exists: bool) -> bool` — returns `force or not exists`.
- `Summary` dataclass: `generated`, `skipped`, `failed`, `unpaired_images`, `unpaired_audio` (all `int`).
- `run(image_dir, audio_dir, output_dir, *, force) -> Summary` — pairs, iterates, renders, counts.
- `main(argv=None) -> int` — argparse CLI; returns `1` if `summary.failed > 0` else `0`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_main.py`:
```python
from pathlib import Path

from src.main import should_render


def test_should_render_when_missing():
    assert should_render(Path("output/x.mp4"), force=False, exists=False) is True


def test_should_skip_when_exists_and_not_forced():
    assert should_render(Path("output/x.mp4"), force=False, exists=True) is False


def test_should_render_when_forced_even_if_exists():
    assert should_render(Path("output/x.mp4"), force=True, exists=True) is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_main.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'src.main'`.

- [ ] **Step 3: Write minimal implementation**

Create `src/main.py`:
```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_main.py -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Run the full test suite**

Run: `.\.venv\Scripts\python.exe -m pytest -q`
Expected: all tests PASS (8 total).

- [ ] **Step 6: Commit**

```bash
git add src/main.py tests/test_main.py
git commit -m "feat: CLI orchestration and summary"
```

---

## Task 6: End-to-end verification and docs

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Create a real sample pair**

Generate a sample image and a short audio file, both named `sample`, using the venv Python (PowerShell):
```powershell
.\.venv\Scripts\python.exe -c "import wave; f=wave.open('input/audio/sample.wav','wb'); f.setnchannels(1); f.setsampwidth(2); f.setframerate(8000); f.writeframes(b'\x00\x00'*8000*3); f.close()"
.\.venv\Scripts\python.exe -c "from PIL import Image; Image.new('RGB',(1280,800),(40,30,60)).save('input/image/sample.png')"
```
If Pillow is not installed, install it just for this step: `.\.venv\Scripts\python.exe -m pip install pillow`. (Pillow is only for generating the test image; it is NOT a runtime dependency, so do not add it to `requirements.txt`.)

- [ ] **Step 2: Run the pipeline end-to-end**

Run: `.\.venv\Scripts\python.exe -m src.main`
Expected: prints `[render] sample.mp4 (3.0s)` then a summary line with `generated=1`. The first run downloads the ffmpeg binary (may take a moment).

- [ ] **Step 3: Verify the output exists and is playable**

Run: `.\.venv\Scripts\python.exe -c "from pathlib import Path; p=Path('output/sample.mp4'); print('exists:', p.exists(), 'bytes:', p.stat().st_size)"`
Expected: `exists: True` and a non-trivial byte count (> 10000).

Manually open `output/sample.mp4` and confirm: 1920x1080, the image slowly zooms, audio is present, length ≈ 3s.

- [ ] **Step 4: Verify idempotency**

Run `.\.venv\Scripts\python.exe -m src.main` again.
Expected: `[skip] sample.mp4 already exists` and `generated=0 skipped=1`.

- [ ] **Step 5: Clean up sample artifacts**

```powershell
Remove-Item input/audio/sample.wav, input/image/sample.png, output/sample.mp4
```

- [ ] **Step 6: Update `README.md`**

Replace the contents of `README.md` with:
```markdown
# yusuke-trap

Turn paired image + audio files into high-quality MP4 videos with a Ken Burns
(slow zoom) effect.

## How it works

Put an image in `input/image/` and an audio file with the **same base name** in
`input/audio/` (e.g. `yusuke.png` + `yusuke.mp3`). Running the tool produces
`output/yusuke.mp4` (1920x1080, H.264, the image slowly zooming for the length
of the audio).

`lirycs/` (song lyrics) and `run-books/` (character research) are working
material for writing the songs and are not used by the tool.

## Setup

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

The ffmpeg binary is downloaded automatically by `imageio-ffmpeg` on first run.

## Usage

```bash
.venv/Scripts/python.exe -m src.main
```

Options: `--force` (re-render existing MP4s), `--input-image`, `--input-audio`,
`--output` to override the default folders.

## Tests

```bash
.venv/Scripts/python.exe -m pytest
```
```

- [ ] **Step 7: Commit**

```bash
git add README.md
git commit -m "docs: usage instructions and verified end-to-end"
```

---

## Self-Review Notes

- **Spec coverage:** pairing (Task 2), audio duration (Task 3), 1080p cover-crop + Ken Burns + H.264/CRF18/AAC (Task 4), CLI skip-existing/`--force`/summary/exit-code/unpaired reporting (Task 5), `imageio-ffmpeg`/`mutagen` deps + `.gitkeep`/`.gitignore` (Task 1), manual ffmpeg validation + README (Task 6). All spec sections map to a task.
- **Type consistency:** `Pair`/`PairingResult`/`list_media`/`match_pairs`/`IMAGE_EXTS`/`AUDIO_EXTS` used identically across `pairing.py` and `main.py`; `build_ffmpeg_command`/`render` signatures match between `render.py` and its callers; `Summary` fields match between definition and `run`.
- **No placeholders:** every code/test step contains complete code and exact commands.
