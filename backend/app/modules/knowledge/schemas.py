"""Knowledge input and detached read contracts."""

import re
from datetime import date, datetime, timezone
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from app.modules.knowledge.text import canonical_url


class ImportRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=512)
    organization: str = Field(min_length=1, max_length=255)
    source_url: HttpUrl
    language: str = Field(pattern=r"^[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$", max_length=35)
    published_at: date | None = None
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    text_path: Path

    @field_validator("source_url")
    @classmethod
    def public_url(cls, value: HttpUrl) -> HttpUrl:
        canonical_url(value)
        return value

    @field_validator("published_at", mode="before")
    @classmethod
    def iso_date(cls, value):
        if value is not None and not isinstance(value, date):
            if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                raise ValueError("published_at must be YYYY-MM-DD or null")
        return value

    @field_validator("fetched_at")
    @classmethod
    def utc_time(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("fetched_at must include a timezone")
        return value.astimezone(timezone.utc)


class Snapshot(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)


class DocumentSummary(Snapshot):
    id: str
    title: str
    organization: str
    source_url: str
    language: str
    published_at: date | None
    fetched_at: datetime
    status: str


class VersionSnapshot(Snapshot):
    id: str
    document_id: str
    version_number: int
    text: str
    content_hash: str


class ChunkSnapshot(Snapshot):
    id: str
    version_id: str
    sequence: int
    title_path: str
    text: str
    char_start: int
    char_end: int
