from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://hockey:hockey_secret@localhost:5432/hockey_analytics"
    REDIS_URL: str = "redis://localhost:6379"
    S3_ENDPOINT_URL: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin123"
    S3_BUCKET: str = "hockey-clips"
    S3_REGION: str = "us-east-1"
    SECRET_KEY: str = "change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_ID: str = ""
    FRONTEND_URL: str = "http://localhost:3001"
    FREE_CLIP_LIMIT: int = 3
    CLIP_PRE_SECONDS: int = 5
    CLIP_POST_SECONDS: int = 8
    VIDEO_STORAGE_PATH: str = "/tmp/video_storage"
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
