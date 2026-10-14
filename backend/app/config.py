from functools import lru_cache

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.exceptions import ConfigurationError


class Settings(BaseSettings):
    database_url: str = Field(min_length=1)
    el_toque_api_token: str = Field(min_length=1)
    el_toque_api_url: str = "https://api.eltoque.com/api/v1/tasas"
    el_toque_auth_header: str = "Authorization"
    el_toque_auth_scheme: str = "Bearer"
    bcc_widget_url: str = "https://www.bc.gob.cu/widget/tasas-de-cambio"
    bcc_fallback_api_url: str | None = None
    bcc_fallback_api_token: str | None = None
    bcc_fallback_auth_header: str = "Authorization"
    bcc_fallback_auth_scheme: str = "Bearer"
    scheduler_enabled: bool = True
    scheduler_interval_minutes: int | None = Field(default=None, ge=1)
    log_level: str = "INFO"
    http_timeout_seconds: float = Field(default=20, gt=0)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as exc:
        fields = sorted({str(error["loc"][0]) for error in exc.errors()})
        raise ConfigurationError(
            "Missing or invalid configuration fields: " + ", ".join(fields)
        ) from None