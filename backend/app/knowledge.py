"""Import and publication transactions, plus the mandatory SQL evidence gate."""

import hashlib
import re
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Chunk, Document, DocumentVersion, IndexJob


def clean_text(text: str) -> str:
    """Preserve paragraph/title boundaries and Unicode character offsets."""
    lines = [re.sub(r"[^\S\n]+", " ", line).strip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_url(url: str | HttpUrl) -> str:
    parsed = HttpUrl(url)
    if parsed.username or parsed.password:
        raise ValueError("source_url cannot contain credentials")
    return str(parsed).split("#", 1)[0]


def document_id(url: str | HttpUrl) -> str:
    return str(uuid5(NAMESPACE_URL, canonical_url(url)))


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


def latest_version(session: Session, source_id: str) -> DocumentVersion | None:
    return session.scalar(select(DocumentVersion).where(DocumentVersion.document_id == source_id)
                          .order_by(DocumentVersion.version_number.desc()).limit(1))


def import_record(session: Session, record: ImportRecord, base_dir: Path) -> tuple[str, str]:
    """Caller owns one transaction per line. Existing document row serializes versions."""
    text = clean_text((base_dir / record.text_path).read_text(encoding="utf-8-sig"))
    if not text:
        raise ValueError("正文为空")
    url = canonical_url(record.source_url)
    digest = content_hash(text)
    key = content_hash(url)
    doc = session.scalar(select(Document).where(Document.source_key == key).with_for_update())
    if doc is not None:
        duplicate = session.scalar(select(DocumentVersion.id).where(
            DocumentVersion.document_id == doc.id, DocumentVersion.content_hash == digest))
        if duplicate:
            return "skipped", doc.id
        previous = latest_version(session, doc.id)
        number = previous.version_number + 1 if previous else 1
        if doc.status == "published" and previous:
            session.add(IndexJob(document_id=doc.id, version_id=previous.id, action="delete"))
    else:
        doc = Document(id=document_id(url), source_url=url, source_key=key)
        session.add(doc)
        number = 1
    doc.title = record.title
    doc.organization = record.organization
    doc.language = record.language
    doc.published_at = record.published_at
    doc.fetched_at = record.fetched_at.astimezone(timezone.utc).replace(tzinfo=None)
    doc.status = "pending"
    session.flush()
    session.add(DocumentVersion(document_id=doc.id, text=text, content_hash=digest, version_number=number))
    session.flush()
    return "success", doc.id


TRANSITIONS = {
    "publish": ({"pending", "expired", "withdrawn"}, "published", "upsert"),
    "withdraw": ({"pending", "published", "expired"}, "withdrawn", "delete"),
    "expire": ({"published"}, "expired", "delete"),
}


def change_status(session: Session, source_id: str, action: str) -> Document:
    doc = session.scalar(select(Document).where(Document.id == source_id).with_for_update())
    if doc is None:
        raise ValueError("资料不存在")
    allowed, target, job_action = TRANSITIONS[action]
    if doc.status not in allowed:
        raise ValueError(f"不允许从 {doc.status} 执行 {action}")
    version = latest_version(session, doc.id)
    if version is None:
        raise ValueError("资料缺少正文版本")
    if action == "publish":
        if not all(value and value.strip() for value in (doc.title, doc.organization, doc.source_url, version.text, version.content_hash)):
            raise ValueError("发布需要标题、机构、来源 URL、正文和内容哈希")
        canonical_url(doc.source_url)
        if content_hash(version.text) != version.content_hash:
            raise ValueError("正文内容哈希不匹配")
    doc.status = target
    session.add(IndexJob(document_id=doc.id, version_id=version.id, action=job_action))
    session.flush()
    return doc


def published_documents(session: Session) -> list[Document]:
    """Read current SQL state, even if this session previously loaded a document."""
    return list(session.scalars(select(Document).where(Document.status == "published")
                               .execution_options(populate_existing=True)))


def eligible_chunks(session: Session, candidate_ids: list[str]) -> list[Chunk]:
    """Future Qdrant adapter must pass candidates through this fail-closed SQL gate.

    Ignore vector payload status; accept only current published versions. Text is
    read from SQL, never from an untrusted/stale vector payload.
    """
    if not candidate_ids:
        return []
    latest = select(DocumentVersion.document_id, func.max(DocumentVersion.version_number).label("number")) \
        .group_by(DocumentVersion.document_id).subquery()
    statement = select(Chunk).join(DocumentVersion, Chunk.version_id == DocumentVersion.id) \
        .join(Document, DocumentVersion.document_id == Document.id) \
        .join(latest, (latest.c.document_id == Document.id) & (latest.c.number == DocumentVersion.version_number)) \
        .where(Chunk.id.in_(candidate_ids), Document.status == "published") \
        .execution_options(populate_existing=True)
    found = {chunk.id: chunk for chunk in session.scalars(statement)}
    return [found[key] for key in dict.fromkeys(candidate_ids) if key in found]
