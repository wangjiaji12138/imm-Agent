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
    mysql_host: str = "127.0.0.1"
    mysql_port: int = Field(default=3306, ge=1, le=65535)
    mysql_database: str = "imm_agent"
    mysql_user: str = "imm_agent"
    mysql_password: str = ""
    qdrant_url: str = "http://127.0.0.1:6333"
    qdrant_collection: str = "imm_agent_chunks_v1"
    embedding_url: str = ""
    embedding_model: str = ""
    embedding_api_key: str = ""
    embedding_dimension: int = Field(default=1536, ge=1)
    embedding_batch_size: int = Field(default=10, ge=1, le=100)
    model_provider: str = "openai-compatible"
    model_url: str = ""
    model_name: str = ""
    model_api_key: str = ""
    model_timeout_seconds: float = Field(default=30.0, gt=0, le=120)
    rate_limit_per_minute: int = Field(default=30, ge=1, le=10000)


@lru_cache
def get_settings() -> Settings:
    """Return one validated settings instance per process."""

    return Settings()
