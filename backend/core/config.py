from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # App
    app_name: str = "Giggle API"
    debug: bool = False
    secret_key: str = "dev-secret-change-in-prod"

    # DB — auto-detects sqlite vs postgres from URL prefix
    database_url: str = "sqlite+aiosqlite:///./giggle.db"

    # AI
    openai_api_key: str
    groq_api_key: str = ""

    # Redis (optional — required for P4+ ARQ workers)
    redis_url: str = "redis://localhost:6379"

    # CORS — Vite dev server
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"]

    # Media
    media_dir: str = "./media"

    # Cloud Storage (optional - for R2/S3)
    use_cloud_storage: bool = False
    s3_endpoint_url: str = ""  # e.g., https://account-id.r2.cloudflarestorage.com
    s3_access_key_id: str = ""
    s3_secret_access_key: str = ""
    s3_bucket_name: str = ""
    s3_public_url: str = ""  # e.g., https://your-bucket.r2.dev

    # Trends
    newsapi_key: str = ""

    # API Ninjas
    api_ninjas_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
