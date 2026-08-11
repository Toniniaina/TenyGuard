from typing import List
from app.detectors.base import BaseProfanityDetector
from app.detectors.dictionary_detector import DictionaryDetector
from app.detectors.context_detector import ContextDetector
from app.models.detection import DetectionItem
from app.models.transcription import TranscriptionSegment


class HybridDetector(BaseProfanityDetector):
    """
    Level 4 Detector: Combines dictionary detection and LLM context analysis
    to generate final confidence score and severity category.
    """

    def __init__(
        self,
        dictionary_detector: DictionaryDetector,
        context_detector: ContextDetector
    ):
        self.dictionary_detector = dictionary_detector
        self.context_detector = context_detector

    def detect(self, segments: List[TranscriptionSegment]) -> List[DetectionItem]:
        """
        Orchestrates detection layers and merges detection results.
        """
        # Step 1: Run fast dictionary check
        dict_results = self.dictionary_detector.detect(segments)

        # Step 2: For items requiring context check, delegate to context detector
        context_results = self.context_detector.detect(segments)

        # Skeleton merging logic
        combined_results = dict_results + context_results
        return combined_results
