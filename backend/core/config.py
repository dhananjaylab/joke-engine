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

    # Redis (optional — required for P4+ ARQ workers)
    redis_url: str = "redis://localhost:6379"

    # CORS — Vite dev server
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Media
    media_dir: str = "./media"

    # Trends
    newsapi_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
