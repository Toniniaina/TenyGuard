import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "TenyGuard"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # Database (PostgreSQL)
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/tenyguard_db"

    # STT & LLM configuration placeholders
    STT_MODEL_NAME: str = "whisper-mg"
    STT_LANGUAGE: str = "mg"
    LLM_API_KEY: str = ""
    LLM_MODEL_NAME: str = "gpt-4o-mini"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
