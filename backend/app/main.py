"""FastAPI application entry point."""

from typing import Literal

from fastapi import Depends, FastAPI, Response, status
from pydantic import BaseModel

from app.readiness import mysql_is_ready, qdrant_is_ready
from app.settings import get_settings


class HealthResponse(BaseModel):
    """Stable response contract for process health checks."""

    status: Literal["ok"] = "ok"
    service: Literal["imm-agent"] = "imm-agent"


class ReadinessResponse(BaseModel):
    """Availability of services required to answer requests."""

    status: Literal["ready", "not_ready"]
    checks: dict[str, Literal["ok", "unavailable"]]


def check_mysql() -> bool:
    return mysql_is_ready(get_settings())


def check_qdrant() -> bool:
    return qdrant_is_ready(get_settings())


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

    @application.get(
        "/ready",
        response_model=ReadinessResponse,
        responses={503: {"model": ReadinessResponse}},
        tags=["system"],
    )
    def ready(
        response: Response,
        mysql_ready: bool = Depends(check_mysql),
        qdrant_ready: bool = Depends(check_qdrant),
    ) -> ReadinessResponse:
        checks = {
            "mysql": "ok" if mysql_ready else "unavailable",
            "qdrant": "ok" if qdrant_ready else "unavailable",
        }
        is_ready = mysql_ready and qdrant_ready
        if not is_ready:
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return ReadinessResponse(
            status="ready" if is_ready else "not_ready",
            checks=checks,
        )

    return application


app = create_app()
