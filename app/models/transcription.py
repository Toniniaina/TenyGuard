from typing import List
from pydantic import BaseModel, Field, ConfigDict


class TranscriptionSegment(BaseModel):
    id: int
    start_time: float = Field(..., description="Start timestamp in seconds")
    end_time: float = Field(..., description="End timestamp in seconds")
    text: str = Field(..., description="Transcribed spoken text in Malagasy")


class TranscriptionResponse(BaseModel):
    video_id: str
    language: str = "mg"
    full_text: str
    segments: List[TranscriptionSegment] = []

    model_config = ConfigDict(from_attributes=True)
