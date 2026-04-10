from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        case_sensitive=False,
        env_file=ROOT_DIR / ".env",
    )

    app_env: str = "development"
    debug: bool = True
    project_name: str = "Korkyt Queue"
    api_prefix: str = "/api/v1"
    secret_key: str = "change-me"
    default_language: str = "ru"

    database_url: str = "postgresql+asyncpg://korkyt:korkyt@postgres:5432/korkyt_queue"
    redis_url: str = "redis://redis:6379/0"
    celery_broker_url: str | None = None
    celery_result_backend: str | None = None

    bot_token: str = ""
    bot_parse_mode: str = "HTML"

    media_root: str = "/data/uploads"
    frontend_url: str = "http://localhost:8080"
    cors_origins: Annotated[list[str], NoDecode] = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:5173",
    ]
    vite_api_base: str = "/api/v1"
    vite_app_title: str = "Korkyt Queue"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("debug", mode="before")
    @classmethod
    def normalize_debug(cls, value: bool | str) -> bool | str:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on", "debug", "development"}:
                return True
            if normalized in {"0", "false", "no", "off", "release", "production", "prod"}:
                return False
        return value

    @property
    def celery_broker(self) -> str:
        return self.celery_broker_url or self.redis_url

    @property
    def celery_backend(self) -> str:
        return self.celery_result_backend or self.redis_url

    @property
    def media_root_path(self) -> Path:
        configured_path = Path(self.media_root)
        try:
            configured_path.mkdir(parents=True, exist_ok=True)
            return configured_path
        except OSError:
            fallback_path = ROOT_DIR / "uploads"
            fallback_path.mkdir(parents=True, exist_ok=True)
            return fallback_path


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
