import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from app.services.audio_service import AudioService, AudioExtractionError


@pytest.fixture
def tmp_audio_service(tmp_path):
    output_dir = tmp_path / "audio_out"
    return AudioService(output_dir=str(output_dir))


def test_ensure_output_directory(tmp_path):
    output_dir = tmp_path / "custom_audio_dir"
    assert not output_dir.exists()

    service = AudioService(output_dir=str(output_dir))
    assert output_dir.exists()


def test_extract_audio_file_not_found(tmp_audio_service):
    with pytest.raises(FileNotFoundError):
        tmp_audio_service.extract_audio("non_existent_video.mp4")


def test_extract_audio_ffmpeg_not_installed(tmp_audio_service, tmp_path):
    dummy_video = tmp_path / "dummy.mp4"
    dummy_video.write_text("fake video content")

    with patch.object(tmp_audio_service, "is_ffmpeg_available", return_value=False):
        with pytest.raises(AudioExtractionError) as exc_info:
            tmp_audio_service.extract_audio(str(dummy_video))
        assert "FFmpeg" in str(exc_info.value)


def test_extract_audio_success(tmp_audio_service, tmp_path):
    dummy_video = tmp_path / "sample.mp4"
    dummy_video.write_bytes(b"dummy video data")

    with patch.object(tmp_audio_service, "is_ffmpeg_available", return_value=True):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

            # Create destination file so resolve() works
            expected_output = tmp_audio_service.output_dir / "sample_audio.wav"
            expected_output.write_bytes(b"RIFF dummy wav data")

            result_path = tmp_audio_service.extract_audio(str(dummy_video))

            assert result_path.endswith(".wav")
            assert mock_run.called
            args, _ = mock_run.call_args
            command = args[0]
            assert command[0] == "ffmpeg"
            assert "-acodec" in command
            assert "pcm_s16le" in command
            assert "-ar" in command
            assert "16000" in command
            assert "-ac" in command
            assert "1" in command


def test_extract_audio_subprocess_error(tmp_audio_service, tmp_path):
    dummy_video = tmp_path / "invalid.mp4"
    dummy_video.write_bytes(b"corrupted video data")

    with patch.object(tmp_audio_service, "is_ffmpeg_available", return_value=True):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                returncode=1,
                cmd=["ffmpeg"],
                stderr="Invalid data found when processing input"
            )

            with pytest.raises(AudioExtractionError) as exc_info:
                tmp_audio_service.extract_audio(str(dummy_video))
            assert "exit code 1" in str(exc_info.value)


def test_cleanup_audio(tmp_audio_service, tmp_path):
    dummy_wav = tmp_path / "temp.wav"
    dummy_wav.write_bytes(b"fake wav")
    assert dummy_wav.exists()

    success = tmp_audio_service.cleanup_audio(str(dummy_wav))
    assert success is True
    assert not dummy_wav.exists()

    # Deleting non-existent file
    assert tmp_audio_service.cleanup_audio(str(dummy_wav)) is False
