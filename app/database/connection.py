from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
from app.core.logging import logger

Base = declarative_base()

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

# Connection engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True if not settings.DATABASE_URL.startswith("sqlite") else False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def seed_reference_data(db_session):
    """
    Seeds initial reference values into lookup tables.
    """
    from app.database.models import VideoStatusModel, ProfanityCategoryModel, SeverityLevelModel

    # 1. Video Statuses
    statuses = [
        ("uploaded", "Téléversé", "Fichier vidéo reçu et prêt pour traitement"),
        ("processing", "En cours", "Extraction audio ou transcription Speech-to-Text en cours"),
        ("completed", "Terminé", "Analyse de détection terminée avec succès"),
        ("error", "Erreur", "Erreur survenue durant l'extraction ou la détection"),
    ]
    for code, label, desc in statuses:
        if not db_session.query(VideoStatusModel).filter_by(code=code).first():
            db_session.add(VideoStatusModel(code=code, label=label, description=desc))

    # 2. Profanity Categories
    categories = [
        ("profanity", "Vulgarité", "Termes grossiers ou vulgaires généraux"),
        ("insult", "Insulte", "Injures et attaques ad hominem"),
        ("offensive", "Offensant", "Propos offensants ou discriminatoires"),
        ("neutral", "Neutre", "Texte ordinaire sans vulgarité"),
        ("ambiguous", "Ambigu", "Terme nécessitant une analyse contextuelle LLM"),
    ]
    for code, label, desc in categories:
        if not db_session.query(ProfanityCategoryModel).filter_by(code=code).first():
            db_session.add(ProfanityCategoryModel(code=code, label=label, description=desc))

    # 3. Severity Levels
    severities = [
        ("low", "Faible", 1),
        ("medium", "Moyen", 2),
        ("high", "Élevé", 3),
    ]
    for code, label, weight in severities:
        if not db_session.query(SeverityLevelModel).filter_by(code=code).first():
            db_session.add(SeverityLevelModel(code=code, label=label, weight=weight))

    db_session.commit()


def init_db():
    """
    Creates all database tables defined in SQLAlchemy models and seeds reference data.
    """
    from app.database import models  # noqa: F401
    try:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            seed_reference_data(db)
        finally:
            db.close()
        logger.info("Database tables & reference data initialized successfully.")
    except Exception as e:
        logger.warning(f"Could not initialize database tables: {e}")


def get_db() -> Generator:
    """
    Dependency generator for database sessions.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
