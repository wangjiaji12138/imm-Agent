"""Minimal feedback contract."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FeedbackInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    request_id: UUID
    rating: Literal["helpful", "not_helpful"]
    note: str | None = Field(default=None, max_length=500)


class FeedbackResult(BaseModel):
    request_id: UUID
    rating: Literal["helpful", "not_helpful"]
    note: str | None
