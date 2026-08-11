import re
import unicodedata
from typing import List, Set, Optional
from app.detectors.base import BaseProfanityDetector
from app.models.detection import DetectionItem, ProfanityCategory, SeverityLevel
from app.models.transcription import TranscriptionSegment


class TextNormalizer:
    """
    Utility class for text normalization (lowercase, accent removal, character repetition handling).
    """

    @staticmethod
    def normalize(text: str) -> str:
        text = text.lower()
        # Remove accents
        text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
        # Remove repeated characters (e.g. "mooots" -> "mots")
        text = re.sub(r'(.)\1{2,}', r'\1', text)
        # Clean extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text


class DictionaryDetector(BaseProfanityDetector):
    """
    Level 1 & Level 2 Detector: Malagasy profanity dictionary matching and text normalization.
    """

    def __init__(self, dictionary_terms: Optional[Set[str]] = None):
        # Initial dictionary of Malagasy profanity terms (placeholder base set)
        self.dictionary_terms = dictionary_terms or set()

    def add_term(self, term: str) -> None:
        normalized = TextNormalizer.normalize(term)
        self.dictionary_terms.add(normalized)

    def detect(self, segments: List[TranscriptionSegment]) -> List[DetectionItem]:
        results: List[DetectionItem] = []
        # Skeleton implementation for dictionary detection
        for segment in segments:
            normalized_text = TextNormalizer.normalize(segment.text)
            words = normalized_text.split()
            for word in words:
                if word in self.dictionary_terms:
                    results.append(
                        DetectionItem(
                            text=segment.text,
                            term=word,
                            category=ProfanityCategory.PROFANITY,
                            severity=SeverityLevel.HIGH,
                            confidence=0.95,
                            start_time=segment.start_time,
                            end_time=segment.end_time
                        )
                    )
        return results
