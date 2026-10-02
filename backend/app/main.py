"""FastAPI composition root."""

from fastapi import FastAPI

from app.api.errors import register_error_handlers
from app.api.middleware import add_request_id
from app.api.routes.chat import router as chat_router
from app.api.routes.feedback import router as feedback_router
from app.api.routes.health import router as health_router
from app.api.routes.sources import router as sources_router
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

    application.middleware("http")(add_request_id)
    register_error_handlers(application)
    application.include_router(health_router)
    application.include_router(chat_router)
    application.include_router(feedback_router)
    application.include_router(sources_router)
    return application


app = create_app()
