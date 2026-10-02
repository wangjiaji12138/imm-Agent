"""FastAPI composition root."""

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.core.settings import get_settings


def create_app() -> FastAPI:
    """Build the API without requiring databases or model credentials."""

    settings = get_settings()
    application = FastAPI(
        title="Imm-Agent API",
        version="0.1.0",
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url=None,
    )

    application.include_router(health_router)
    return application


app = create_app()
