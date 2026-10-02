"""Validated search input and detached results."""

from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SearchFilters(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    language: str | None = Field(default=None, pattern=r"^[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$", max_length=35)
    document_id: UUID | None = None
    published_from: date | None = None
    published_to: date | None = None

    @model_validator(mode="after")
    def valid_range(self):
        if self.published_from and self.published_to and self.published_from > self.published_to:
            raise ValueError("发布日期起点不能晚于终点")
        return self


class SearchInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    query: str = Field(min_length=2, max_length=500)
    filters: SearchFilters = Field(default_factory=SearchFilters)
    limit: int = Field(default=5, ge=1, le=20, strict=True)


class Candidate(BaseModel):
    chunk_id: str
    version_id: str
    score: float


class SearchResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    chunk_id: str
    document_id: str
    text: str
    title: str
    organization: str
    source_url: str
    published_at: date | None
    score: float
