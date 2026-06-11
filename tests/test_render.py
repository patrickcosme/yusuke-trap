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
    assert "-loop" in cmd
    assert str(Path("input/image/yusuke.png")) in cmd
    assert str(Path("input/audio/yusuke.mp3")) in cmd
    assert cmd[-1] == str(Path("output/yusuke.mp4"))
    assert "libx264" in cmd
    assert "-crf" in cmd and "18" in cmd
    assert "yuv420p" in cmd
    assert "-shortest" in cmd
    filter_arg = cmd[cmd.index("-filter_complex") + 1]
    assert "zoompan" in filter_arg
    assert "s=1920x1080" in filter_arg
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
