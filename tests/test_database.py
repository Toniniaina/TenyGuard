import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.connection import Base, seed_reference_data
from app.database.models import (
    VideoModel, TranscriptionModel, DetectionModel, TermsDictionaryModel,
    VideoStatusModel, ProfanityCategoryModel, SeverityLevelModel
)


@pytest.fixture
def test_db_session():
    """
    Creates an in-memory SQLite database session for unit testing ORM models and reference tables.
    """
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    seed_reference_data(session)
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_reference_tables_seeded(test_db_session):
    statuses = test_db_session.query(VideoStatusModel).all()
    assert len(statuses) >= 4
    status_codes = [s.code for s in statuses]
    assert "uploaded" in status_codes
    assert "completed" in status_codes

    categories = test_db_session.query(ProfanityCategoryModel).all()
    assert len(categories) >= 5

    severities = test_db_session.query(SeverityLevelModel).all()
    assert len(severities) >= 3


def test_video_model_crud_with_reference(test_db_session):
    video = VideoModel(
        filename="sample_video.mp4",
        content_type="video/mp4",
        filepath="data/videos/sample_video.mp4",
        status_code="uploaded"
    )
    test_db_session.add(video)
    test_db_session.commit()
    test_db_session.refresh(video)

    assert video.id is not None
    assert video.status_code == "uploaded"
    assert video.status_ref.label == "Téléversé"


def test_detection_model_with_references(test_db_session):
    video = VideoModel(
        filename="test_rel.mp4",
        content_type="video/mp4",
        filepath="data/videos/test_rel.mp4"
    )
    test_db_session.add(video)
    test_db_session.commit()

    detection = DetectionModel(
        video_id=video.id,
        text="Izay olona izay",
        term="olona",
        category_code="neutral",
        severity_code="low",
        confidence=0.9,
        start_time=0.0,
        end_time=1.5
    )
    test_db_session.add(detection)
    test_db_session.commit()

    queried = test_db_session.query(DetectionModel).filter_by(video_id=video.id).first()
    assert queried.category_ref.label == "Neutre"
    assert queried.severity_ref.label == "Faible"
