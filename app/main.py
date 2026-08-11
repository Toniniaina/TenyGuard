from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import health_router, videos_router, detection_router
from app.core.config import settings
from app.core.logging import logger
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB tables
    logger.info("Initializing database tables...")
    init_db()
    yield
    # Shutdown logic if any
    logger.info("Application shutdown.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Application de détection de gros mots, insultes et expressions vulgaires en langue malagasy dans des vidéos.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health_router)
app.include_router(videos_router, prefix=settings.API_V1_STR)
app.include_router(detection_router, prefix=settings.API_V1_STR)


@app.get("/", include_in_schema=False)
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting TenyGuard development server...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
