from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.constants import (
    APP_ROOT,
    API_V1_PREFIX_DEFAULT,
    DEFAULT_AI_MODEL,
    DEFAULT_AI_REQUEST_TIMEOUT_SECONDS,
    DEFAULT_ANALYSIS_RATE_LIMIT,
    DEFAULT_MAX_FILE_SIZE_MB,
    DEFAULT_MAX_PDF_PAGES,
    DEFAULT_MAX_TOOL_CALL_ROUNDS,
    DEFAULT_RATE_LIMIT,
    DEFAULT_RATE_LIMIT_STORAGE_URI,
    DEFAULT_STORE_SOURCE_TEXT,
)


class Settings(BaseSettings):
    app_name: str = "SkillBridge"
    app_env: str = "development"
    debug: bool = False
    api_v1_prefix: str = API_V1_PREFIX_DEFAULT
    database_url: str | None = None
    gemini_api_key: str | None = None
    ai_model: str = DEFAULT_AI_MODEL
    ai_request_timeout_seconds: int = Field(default=DEFAULT_AI_REQUEST_TIMEOUT_SECONDS, ge=5, le=300)
    store_source_text: bool = DEFAULT_STORE_SOURCE_TEXT
    max_file_size_mb: int = Field(default=DEFAULT_MAX_FILE_SIZE_MB, ge=1, le=50)
    max_pdf_pages: int = Field(default=DEFAULT_MAX_PDF_PAGES, ge=1, le=1000)
    max_tool_call_rounds: int = Field(default=DEFAULT_MAX_TOOL_CALL_ROUNDS, ge=1, le=5)
    rate_limit_analysis: str = DEFAULT_ANALYSIS_RATE_LIMIT
    rate_limit_default: str = DEFAULT_RATE_LIMIT
    rate_limit_storage_uri: str = DEFAULT_RATE_LIMIT_STORAGE_URI

    model_config = SettingsConfigDict(env_file=APP_ROOT / ".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value):
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "production", "prod", "false", "0", "no", "off"}:
                return False
            if normalized in {"development", "dev", "true", "1", "yes", "on"}:
                return True
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
