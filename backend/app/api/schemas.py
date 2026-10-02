"""Stable process health and dependency readiness response contracts."""

from typing import Literal
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Stable response contract for process health checks."""

    status: Literal["ok"] = "ok"
    service: Literal["imm-agent"] = "imm-agent"


class ReadinessResponse(BaseModel):
    """Availability of services required to answer requests."""

    status: Literal["ready", "not_ready"]
    checks: dict[str, Literal["ok", "unavailable"]]
