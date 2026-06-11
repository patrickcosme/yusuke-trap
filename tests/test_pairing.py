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


from src.pairing import list_media, IMAGE_EXTS


def test_list_media_filters_by_extension(tmp_path):
    (tmp_path / "a.png").write_bytes(b"x")
    (tmp_path / "b.JPG").write_bytes(b"x")
    (tmp_path / "notes.txt").write_bytes(b"x")

    found = list_media(tmp_path, IMAGE_EXTS)

    names = sorted(p.name for p in found)
    assert names == ["a.png", "b.JPG"]


from src.pairing import match_pairs, AUDIO_EXTS


def test_list_media_missing_directory_returns_empty(tmp_path):
    missing = tmp_path / "nope"
    assert list_media(missing, AUDIO_EXTS) == []


def test_match_pairs_no_overlap():
    images = [Path("input/image/a.png")]
    audios = [Path("input/audio/b.mp3")]

    result = match_pairs(images, audios)

    assert result.pairs == []
    assert result.images_without_audio == [Path("input/image/a.png")]
    assert result.audio_without_image == [Path("input/audio/b.mp3")]
