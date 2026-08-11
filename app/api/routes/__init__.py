from app.api.routes.health import router as health_router
from app.api.routes.videos import router as videos_router
from app.api.routes.detection import router as detection_router

__all__ = ["health_router", "videos_router", "detection_router"]
