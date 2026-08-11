from typing import List, Optional
from app.detectors.hybrid_detector import HybridDetector
from app.models.detection import DetectionResponse, DetectionItem
from app.models.transcription import TranscriptionResponse, TranscriptionSegment


class ProfanityService:
    """
    Main orchestration service for profanity detection logic.
    """

    def __init__(self, hybrid_detector: HybridDetector):
        self.hybrid_detector = hybrid_detector

    def analyze_transcription(self, transcription: TranscriptionResponse) -> DetectionResponse:
        """
        Runs detection algorithms over transcription segments and returns DetectionResponse.
        """
        detections: List[DetectionItem] = self.hybrid_detector.detect(transcription.segments)
        return DetectionResponse(
            video_id=transcription.video_id,
            detections=detections,
            total_detections=len(detections)
        )
