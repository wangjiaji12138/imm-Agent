"""FastAPI application entry point."""

from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from app.settings import get_settings


class HealthResponse(BaseModel):
    """Stable response contract for process health checks."""

    status: Literal["ok"] = "ok"
    service: Literal["imm-agent"] = "imm-agent"


def create_app() -> FastAPI:
    """Build the API without requiring databases or model credentials."""

    settings = get_settings()
    application = FastAPI(
        title="Imm-Agent API",
        version="0.1.0",
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url=None,
    )

    @application.get("/health", response_model=HealthResponse, tags=["system"])
    def health() -> HealthResponse:
        return HealthResponse()

    return application


app = create_app()

