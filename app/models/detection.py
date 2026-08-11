from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ProfanityCategory(str, Enum):
    PROFANITY = "profanity"
    INSULT = "insult"
    OFFENSIVE = "offensive"
    NEUTRAL = "neutral"
    AMBIGUOUS = "ambiguous"


class DetectionItem(BaseModel):
    text: str = Field(..., description="Detected phrase or segment")
    term: Optional[str] = Field(None, description="Matched dictionary term or normalized word")
    category: ProfanityCategory = Field(..., description="Category of detected language")
    severity: SeverityLevel = Field(..., description="Severity level")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    start_time: float = Field(..., description="Start time in video (seconds)")
    end_time: float = Field(..., description="End time in video (seconds)")


class DetectionRequest(BaseModel):
    video_id: Optional[str] = None
    text: Optional[str] = None


class DetectionResponse(BaseModel):
    video_id: Optional[str] = None
    detections: List[DetectionItem] = []
    total_detections: int = 0
