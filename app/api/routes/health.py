from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Health Check Endpoint")
def health_check():
    """
    Returns the operational status of the TenyGuard API.
    """
    return {
        "status": "ok",
        "app": settings.PROJECT_NAME,
        "version": "0.1.0"
    }
