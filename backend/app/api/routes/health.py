"""Process health and service readiness routes."""

from fastapi import APIRouter, Depends, Response, status

from app.api.dependencies import check_mysql, check_qdrant
from app.api.schemas import HealthResponse, ReadinessResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    return HealthResponse()

@router.get(
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
