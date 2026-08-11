from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class VideoBase(BaseModel):
    filename: str
    content_type: str


class VideoCreate(VideoBase):
    size: int


class VideoResponse(VideoBase):
    id: str
    filepath: str
    status: str = Field(default="uploaded", description="Status: uploaded, processing, completed, error")
    duration: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)
