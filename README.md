# yusuke-trap

Turn paired image + audio files into high-quality MP4 videos with a Ken Burns
(slow zoom) effect.

## How it works

Put an image in `input/image/` and an audio file with the **same base name** in
`input/audio/` (e.g. `yusuke.png` + `yusuke.mp3`). Running the tool produces
`output/yusuke.mp4` (1920x1080, H.264, the image slowly zooming for the length
of the audio).

`lyrics/` (song lyrics) and `run-books/` (character research) are working
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
