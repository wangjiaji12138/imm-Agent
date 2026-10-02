"""HTTP contracts for health, chat, source expansion and errors."""

from datetime import date
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.answering.schemas import AnswerResult


class HealthResponse(BaseModel):
    """Stable response contract for process health checks."""

    status: Literal["ok"] = "ok"
    service: Literal["imm-agent"] = "imm-agent"


class ReadinessResponse(BaseModel):
    """Availability of services required to answer requests."""

    status: Literal["ready", "not_ready"]
    checks: dict[str, Literal["ok", "unavailable"]]


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    message: str = Field(min_length=2, max_length=500)
    conversation_id: UUID | None = None


class SourceSummary(BaseModel):
    chunk_id: str
    title: str
    organization: str
    source_url: str
    published_at: date | None


class ChatResponse(AnswerResult):
    request_id: str
    conversation_id: UUID | None
    conversation_token: str | None = None
    sources: list[SourceSummary]


class SourceResponse(BaseModel):
    chunk_id: str
    document_id: str
    version_id: str
    title: str
    organization: str
    source_url: str
    published_at: date | None
    text: str
    title_path: str
    char_start: int
    char_end: int


class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorDetail
