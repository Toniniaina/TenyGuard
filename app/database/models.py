import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Text, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship
from app.database.connection import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now():
    return datetime.now(timezone.utc)


# ==========================================
# TABLES DE RÉFÉRENCE (LOOKUP TABLES)
# ==========================================

class VideoStatusModel(Base):
    """
    Reference table for video processing statuses.
    """
    __tablename__ = "ref_video_statuses"

    code = Column(String(50), primary_key=True)  # e.g. 'uploaded', 'processing', 'completed', 'error'
    label = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)


class ProfanityCategoryModel(Base):
    """
    Reference table for profanity categories.
    """
    __tablename__ = "ref_profanity_categories"

    code = Column(String(50), primary_key=True)  # e.g. 'profanity', 'insult', 'offensive', 'neutral', 'ambiguous'
    label = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)


class SeverityLevelModel(Base):
    """
    Reference table for severity levels.
    """
    __tablename__ = "ref_severity_levels"

    code = Column(String(50), primary_key=True)  # e.g. 'low', 'medium', 'high'
    label = Column(String(100), nullable=False)
    weight = Column(Integer, nullable=False, default=1)


# ==========================================
# TABLES PRINCIPALES (BUSINESS ENTITIES)
# ==========================================

class VideoModel(Base):
    """
    SQLAlchemy ORM Model representing an uploaded video.
    """
    __tablename__ = "videos"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    filepath = Column(String(500), nullable=False)
    status_code = Column(String(50), ForeignKey("ref_video_statuses.code"), nullable=False, default="uploaded")
    duration = Column(Float, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    status_ref = relationship("VideoStatusModel")
    transcriptions = relationship("TranscriptionModel", back_populates="video", cascade="all, delete-orphan")
    detections = relationship("DetectionModel", back_populates="video", cascade="all, delete-orphan")


class TranscriptionModel(Base):
    """
    SQLAlchemy ORM Model representing a video transcription with timestamps.
    """
    __tablename__ = "transcriptions"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    video_id = Column(String(36), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    language = Column(String(10), nullable=False, default="mg")
    full_text = Column(Text, nullable=False, default="")
    segments = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    video = relationship("VideoModel", back_populates="transcriptions")


class DetectionModel(Base):
    """
    SQLAlchemy ORM Model representing detected profanity/insult items.
    """
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    video_id = Column(String(36), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    text = Column(Text, nullable=False)
    term = Column(String(255), nullable=True)
    category_code = Column(String(50), ForeignKey("ref_profanity_categories.code"), nullable=False)
    severity_code = Column(String(50), ForeignKey("ref_severity_levels.code"), nullable=False)
    confidence = Column(Float, nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    video = relationship("VideoModel", back_populates="detections")
    category_ref = relationship("ProfanityCategoryModel")
    severity_ref = relationship("SeverityLevelModel")


class TermsDictionaryModel(Base):
    """
    SQLAlchemy ORM Model representing Malagasy profanity dictionary entries.
    """
    __tablename__ = "terms_dictionary"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    term = Column(String(255), unique=True, nullable=False, index=True)
    normalized_term = Column(String(255), nullable=False, index=True)
    category_code = Column(String(50), ForeignKey("ref_profanity_categories.code"), nullable=False, default="profanity")
    severity_code = Column(String(50), ForeignKey("ref_severity_levels.code"), nullable=False, default="high")
    created_at = Column(DateTime, default=utc_now, nullable=False)

    category_ref = relationship("ProfanityCategoryModel")
    severity_ref = relationship("SeverityLevelModel")
