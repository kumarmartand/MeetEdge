from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "MeetEdge"
    debug: bool = False
    secret_key: str = "change-me-in-production-min-32-chars"
    database_url: str = "postgresql://meetedge:meetedge_dev@localhost:5432/meetedge"

    @property
    def async_database_url(self) -> str:
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self.database_url
    redis_url: str = "redis://localhost:6379/0"
    google_credentials_path: str | None = None
    google_token_path: str = "token.json"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    jwt_private_key_path: str | None = None
    jwt_public_key_path: str | None = None
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str = "noreply@meetedge.local"
    slack_bot_token: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
