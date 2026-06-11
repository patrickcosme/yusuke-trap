from pathlib import Path

from src.main import should_render


def test_should_render_when_missing():
    assert should_render(Path("output/x.mp4"), force=False, exists=False) is True


def test_should_skip_when_exists_and_not_forced():
    assert should_render(Path("output/x.mp4"), force=False, exists=True) is False


def test_should_render_when_forced_even_if_exists():
    assert should_render(Path("output/x.mp4"), force=True, exists=True) is True
