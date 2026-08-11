from typing import List
from app.models.transcription import TranscriptionResponse, TranscriptionSegment


class TranscriptionService:
    """
    Service responsible for Speech-to-Text conversion for the Malagasy language (mg).
    """

    def __init__(self, model_name: str = "whisper-mg", language: str = "mg"):
        self.model_name = model_name
        self.language = language

    def transcribe(self, audio_path: str, video_id: str = "") -> TranscriptionResponse:
        """
        Skeleton method: Transcribes audio file into text segments with start and end timestamps.
        """
        # Placeholder segments for initialization
        dummy_segments: List[TranscriptionSegment] = []
        return TranscriptionResponse(
            video_id=video_id,
            language=self.language,
            full_text="",
            segments=dummy_segments
        )
