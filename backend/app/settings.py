"""Environment-based application configuration."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from ``IMM_AGENT_*`` environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="IMM_AGENT_",
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: Literal["development", "test", "production"] = "development"
    log_level: str = Field(default="INFO", min_length=1)


@lru_cache
def get_settings() -> Settings:
    """Return one validated settings instance per process."""

    return Settings()

