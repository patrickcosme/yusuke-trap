from pathlib import Path

from src.main import should_render


def test_should_render_when_missing():
    assert should_render(Path("output/x.mp4"), force=False, exists=False) is True


def test_should_skip_when_exists_and_not_forced():
    assert should_render(Path("output/x.mp4"), force=False, exists=True) is False


def test_should_render_when_forced_even_if_exists():
    assert should_render(Path("output/x.mp4"), force=True, exists=True) is True


from src import main as main_module
from src.main import run


def test_run_generates_and_skips(tmp_path, monkeypatch):
    image_dir = tmp_path / "image"
    audio_dir = tmp_path / "audio"
    output_dir = tmp_path / "output"
    image_dir.mkdir()
    audio_dir.mkdir()
    output_dir.mkdir()
    (image_dir / "song.png").write_bytes(b"x")
    (audio_dir / "song.mp3").write_bytes(b"x")
    (image_dir / "lonely.png").write_bytes(b"x")  # image without audio

    calls = []
    monkeypatch.setattr(main_module, "audio_duration", lambda path: 5.0)
    monkeypatch.setattr(
        main_module, "render",
        lambda image, audio, output, duration: output.write_bytes(b"video"),
    )

    first = run(image_dir, audio_dir, output_dir, force=False)
    assert first.generated == 1
    assert first.unpaired_images == 1
    assert (output_dir / "song.mp4").exists()

    # second run: output exists, so it is skipped
    second = run(image_dir, audio_dir, output_dir, force=False)
    assert second.generated == 0
    assert second.skipped == 1
