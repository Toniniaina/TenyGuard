from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from app.services.transcription_service import TranscriptionService, TranscriptionError
from app.models.transcription import TranscriptionResponse, TranscriptionSegment


@pytest.fixture
def transcription_service():
    return TranscriptionService(model_name="whisper-mg", language="mg")


def test_transcribe_file_not_found(transcription_service):
    with pytest.raises(FileNotFoundError):
        transcription_service.transcribe("non_existent_audio.wav")


def test_transcribe_simulated_mode(transcription_service, tmp_path):
    dummy_wav = tmp_path / "test.wav"
    dummy_wav.write_bytes(b"dummy wav content")

    # Force simulated mode
    with patch.object(transcription_service, "_load_stt_model", return_value="SIMULATED_ENGINE"):
        result = transcription_service.transcribe(str(dummy_wav), video_id="video-uuid-123")

        assert isinstance(result, TranscriptionResponse)
        assert result.video_id == "video-uuid-123"
        assert result.language == "mg"
        assert len(result.segments) > 0
        assert len(result.full_text) > 0

        first_segment = result.segments[0]
        assert isinstance(first_segment, TranscriptionSegment)
        assert first_segment.start_time >= 0.0
        assert first_segment.end_time > first_segment.start_time
        assert isinstance(first_segment.text, str)


def test_transcribe_real_whisper_mock(transcription_service, tmp_path):
    dummy_wav = tmp_path / "mock_audio.wav"
    dummy_wav.write_bytes(b"mock wav header")

    mock_whisper_model = MagicMock()
    mock_whisper_model.transcribe.return_value = {
        "text": "Salama tompoko",
        "segments": [
            {"start": 0.0, "end": 2.5, "text": "Salama tompoko"},
            {"start": 2.5, "end": 5.0, "text": "Inona no vaovao"}
        ]
    }

    with patch.object(transcription_service, "_load_stt_model", return_value=mock_whisper_model):
        response = transcription_service.transcribe(str(dummy_wav), video_id="vid-456")

        assert response.video_id == "vid-456"
        assert response.language == "mg"
        assert len(response.segments) == 2
        assert response.segments[0].text == "Salama tompoko"
        assert response.segments[0].start_time == 0.0
        assert response.segments[0].end_time == 2.5
        assert response.segments[1].text == "Inona no vaovao"
        assert response.full_text == "Salama tompoko Inona no vaovao"


def test_transcribe_exception_handling(transcription_service, tmp_path):
    dummy_wav = tmp_path / "failing_audio.wav"
    dummy_wav.write_bytes(b"corrupted wav")

    mock_model = MagicMock()
    mock_model.transcribe.side_effect = RuntimeError("Whisper decoding failure")

    with patch.object(transcription_service, "_load_stt_model", return_value=mock_model):
        with pytest.raises(TranscriptionError) as exc_info:
            transcription_service.transcribe(str(dummy_wav))
        assert "Whisper decoding failure" in str(exc_info.value)
