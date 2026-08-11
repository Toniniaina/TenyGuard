import sys
from sqlalchemy import inspect
from app.core.config import settings
from app.database import (
    SessionLocal, engine, init_db,
    VideoStatusModel, ProfanityCategoryModel, SeverityLevelModel, VideoModel
)


def verify_postgres_production():
    """
    Script de verification en production / integration reelle pour le Ticket 1 sur PostgreSQL.
    """
    print("=========================================================")
    print("[INFO] VERIFICATION DE LA BASE POSTGRESQL (TICKET 1)")
    print("=========================================================")
    print(f"URL de Connexion : {settings.DATABASE_URL}")

    # 1. Test de Connexion & Inspection des tables
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"\n[OK] Connexion PostgreSQL etablie avec succes !")
        print(f"[OK] Tables detectees ({len(tables)}) : {tables}")
    except Exception as e:
        print(f"\n[ERROR] ERREUR DE CONNEXION POSTGRESQL : {e}")
        sys.exit(1)

    # 2. Verification des tables requises
    expected_tables = [
        "ref_video_statuses",
        "ref_profanity_categories",
        "ref_severity_levels",
        "videos",
        "transcriptions",
        "detections",
        "terms_dictionary"
    ]
    missing = [t for t in expected_tables if t not in tables]
    if missing:
        print(f"[WARNING] Tables manquantes : {missing}. Execution de init_db()...")
        init_db()
        tables = inspector.get_table_names()
        print(f"[OK] Tables apres init : {tables}")
    else:
        print("[OK] Toutes les 7 tables requises sont bien presentes dans PostgreSQL !")

    # 3. Verification du populage des tables de reference
    db = SessionLocal()
    try:
        statuses = db.query(VideoStatusModel).all()
        categories = db.query(ProfanityCategoryModel).all()
        severities = db.query(SeverityLevelModel).all()

        print(f"\n[INFO] Donnees de reference populees :")
        print(f"  - Statuses video ({len(statuses)}) : {[s.code for s in statuses]}")
        print(f"  - Categories ({len(categories)}) : {[c.code for c in categories]}")
        print(f"  - Niveaux de severite ({len(severities)}) : {[s.code for s in severities]}")

        assert len(statuses) >= 4, "Table ref_video_statuses non populee"
        assert len(categories) >= 5, "Table ref_profanity_categories non populee"
        assert len(severities) >= 3, "Table ref_severity_levels non populee"

        # 4. Test CRUD transactionnel reel
        print("\n[TEST] Test d'ecriture / lecture / suppression reelle sur PostgreSQL...")
        test_video = VideoModel(
            filename="prod_test_video.mp4",
            content_type="video/mp4",
            filepath="data/videos/prod_test.mp4",
            status_code="uploaded"
        )
        db.add(test_video)
        db.commit()
        db.refresh(test_video)
        created_id = test_video.id
        print(f"  - Video de test inseree avec ID: {created_id}")

        # Lecture
        queried = db.query(VideoModel).filter_by(id=created_id).first()
        assert queried is not None
        print(f"  - Video relue avec succes (Statut relie FK: code='{queried.status_code}')")

        # Nettoyage
        db.delete(queried)
        db.commit()
        print("  - Video de test nettoyee avec succes.")

        print("\n[SUCCESS] LE TICKET 1 EST 100% OPERATIONNEL SUR VOTRE POSTGRESQL EN PRODUCTION !")

    except Exception as e:
        print(f"\n[ERROR] ERREUR DE VERIFICATION POSTGRESQL : {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    verify_postgres_production()
