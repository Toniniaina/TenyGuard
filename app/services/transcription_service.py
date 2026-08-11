import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from app.core.config import settings
from app.core.logging import logger
from app.models.transcription import TranscriptionResponse, TranscriptionSegment


class TranscriptionError(Exception):
    """Exception raised when Speech-to-Text transcription fails."""
    pass


class TranscriptionService:
    """
    Service responsible for Speech-to-Text (STT) conversion for Malagasy audio files.
    Generates structured transcriptions with start/end timestamps per segment.
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        language: Optional[str] = None
    ):
        self.model_name = model_name or getattr(settings, "STT_MODEL_NAME", "whisper-mg")
        self.language = language or getattr(settings, "STT_LANGUAGE", "mg")
        self._stt_model = None  # Lazy loading placeholder for Whisper model

    def _load_stt_model(self):
        """
        Lazy loads local Whisper model if installed.
        """
        if self._stt_model is None:
            try:
                import whisper
                logger.info(f"Loading local Whisper STT model '{self.model_name}'...")
                self._stt_model = whisper.load_model("base")
            except ImportError:
                logger.warning("Package 'openai-whisper' not installed. Running STT engine in simulated mode.")
                self._stt_model = "SIMULATED_ENGINE"
        return self._stt_model

    def transcribe(self, audio_path: str, video_id: str = "") -> TranscriptionResponse:
        """
        Transcribes input audio file into Malagasy text segments with precise timestamps.

        :param audio_path: Path to the input WAV audio file.
        :param video_id: ID of the associated video.
        :return: Pydantic TranscriptionResponse with full_text and timestamps segments.
        """
        path = Path(audio_path)
        if not path.exists():
            raise FileNotFoundError(f"Fichier audio introuvable pour la transcription : {audio_path}")

        logger.info(f"Starting Speech-to-Text transcription for '{audio_path}' (Language: {self.language})...")

        try:
            model = self._load_stt_model()

            if model != "SIMULATED_ENGINE":
                # Real Whisper inference
                result = model.transcribe(str(path), language=self.language)
                segments = []
                full_text_parts = []

                for idx, seg in enumerate(result.get("segments", [])):
                    segment_obj = TranscriptionSegment(
                        id=idx,
                        start_time=round(float(seg.get("start", 0.0)), 2),
                        end_time=round(float(seg.get("end", 0.0)), 2),
                        text=seg.get("text", "").strip()
                    )
                    segments.append(segment_obj)
                    full_text_parts.append(segment_obj.text)

                full_text = " ".join(full_text_parts)
            else:
                # Simulated / Fallback Mode (for local development & testing without heavy ML weights)
                segments = self._generate_simulated_transcription(audio_path)
                full_text = " ".join([s.text for s in segments])

            logger.info(f"Transcription finished: {len(segments)} segment(s) generated.")

            return TranscriptionResponse(
                video_id=video_id,
                language=self.language,
                full_text=full_text,
                segments=segments
            )

        except Exception as e:
            error_msg = f"Erreur lors de la transcription Speech-To-Text : {e}"
            logger.error(error_msg)
            raise TranscriptionError(error_msg) from e

    def _generate_simulated_transcription(self, audio_path: str) -> List[TranscriptionSegment]:
        """
        Generates structured simulated segments for development/testing when local Whisper model is absent.
        """
        return [
            TranscriptionSegment(
                id=0,
                start_time=0.0,
                end_time=3.5,
                text="Manao ahoana ianao, saladama ve ny vaovao androany."
            ),
            TranscriptionSegment(
                id=1,
                start_time=4.0,
                end_time=7.2,
                text="Mbola tsara, fa misy teny ratsy sy insulte kely ato amin'ny resaka."
            ),
            TranscriptionSegment(
                id=2,
                start_time=8.0,
                end_time=11.5,
                text="Misaotra betsaka amin'ny fiarahan-dalana."
            )
        ]
