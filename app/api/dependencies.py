from app.core.config import settings
from app.detectors.context_detector import ContextDetector
from app.detectors.dictionary_detector import DictionaryDetector
from app.detectors.hybrid_detector import HybridDetector
from app.services.audio_service import AudioService
from app.services.llm_service import LLMService
from app.services.profanity_service import ProfanityService
from app.services.transcription_service import TranscriptionService
from app.services.video_service import VideoService


def get_video_service() -> VideoService:
    return VideoService()


def get_audio_service() -> AudioService:
    return AudioService()


def get_transcription_service() -> TranscriptionService:
    return TranscriptionService(
        model_name=settings.STT_MODEL_NAME,
        language=settings.STT_LANGUAGE
    )


def get_llm_service() -> LLMService:
    return LLMService(
        api_key=settings.LLM_API_KEY,
        model_name=settings.LLM_MODEL_NAME
    )


def get_profanity_service() -> ProfanityService:
    dict_detector = DictionaryDetector()
    llm_service = get_llm_service()
    context_detector = ContextDetector(llm_service=llm_service)
    hybrid_detector = HybridDetector(
        dictionary_detector=dict_detector,
        context_detector=context_detector
    )
    return ProfanityService(hybrid_detector=hybrid_detector)
