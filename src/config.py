from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "URL Shortener Microservice"
    environment: str = Field(default="development", validation_alias="ENV")
    database_url: str = Field(
        default="sqlite:///urls.db",
        validation_alias="DATABASE_URL",
    )
    use_postgres: bool = Field(
        default=False,
        validation_alias="USE_POSTGRES",
    )
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="REDIS_URL",
    )
    analytics_api_key: str | None = Field(
        default=None,
        validation_alias="ANALYTICS_API_KEY",
    )
    trusted_proxy_cidrs: list[str] = Field(
        default_factory=lambda: ["127.0.0.1/32", "::1/128"],
        validation_alias="TRUSTED_PROXY_CIDRS",
    )
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    log_file_path: str = Field(
        default="app_errors.log",
        validation_alias="LOG_FILE_PATH",
    )
    base_counter_seed: int = Field(
        default=10_000_000,
        validation_alias="BASE_COUNTER_SEED",
    )
    rate_limit_create_per_minute: int = Field(
        default=60,
        validation_alias="RATE_LIMIT_CREATE_PER_MINUTE",
    )
    rate_limit_redirect_per_minute: int = Field(
        default=600,
        validation_alias="RATE_LIMIT_REDIRECT_PER_MINUTE",
    )
    rate_limit_analytics_per_minute: int = Field(
        default=60,
        validation_alias="RATE_LIMIT_ANALYTICS_PER_MINUTE",
    )
    metrics_host: str = Field(default="127.0.0.1", validation_alias="METRICS_HOST")
    metrics_port: int = Field(default=9100, validation_alias="METRICS_PORT")
    enable_rate_limits: bool = Field(
        default=False,
        validation_alias="ENABLE_RATE_LIMITS",
    )

    model_config = SettingsConfigDict(
        env_file=Path(".env"),
        extra="ignore",
        case_sensitive=False,
    )

    @property
    def is_postgres_enabled(self) -> bool:
        return self.use_postgres and self.database_url.startswith("postgresql")

    @property
    def analytics_auth_required(self) -> bool:
        return self.analytics_api_key is not None


settings = Settings()
