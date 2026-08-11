from abc import ABC, abstractmethod
from typing import List
from app.models.detection import DetectionItem
from app.models.transcription import TranscriptionSegment


class BaseProfanityDetector(ABC):
    """
    Abstract Base Class for all profanity detection algorithms (POO design).
    """

    @abstractmethod
    def detect(self, segments: List[TranscriptionSegment]) -> List[DetectionItem]:
        """
        Analyze transcription segments and return a list of detection results.
        """
        pass
