"""Authoritative knowledge records; vector indexes are derived from these tables."""

from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column


from app.infrastructure.orm import Base


def new_id() -> str:
    return str(uuid4())


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (
        CheckConstraint("status IN ('pending','published','expired','withdrawn')", name="ck_document_status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    title: Mapped[str] = mapped_column(String(512))
    organization: Mapped[str] = mapped_column(String(255))
    source_url: Mapped[str] = mapped_column(Text)
    source_key: Mapped[str] = mapped_column(String(64), unique=True)
    language: Mapped[str] = mapped_column(String(35), index=True)
    published_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(16), default="pending", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DocumentVersion(Base):
    __tablename__ = "document_versions"
    __table_args__ = (
        UniqueConstraint("document_id", "content_hash", name="uq_version_hash"),
        UniqueConstraint("document_id", "version_number", name="uq_version_number"),
        CheckConstraint("version_number > 0", name="ck_version_number"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    text: Mapped[str] = mapped_column(Text().with_variant(LONGTEXT(), "mysql"))
    content_hash: Mapped[str] = mapped_column(String(64))
    version_number: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Chunk(Base):
    __tablename__ = "chunks"
    __table_args__ = (
        UniqueConstraint("version_id", "sequence", name="uq_chunk_sequence"),
        CheckConstraint("sequence >= 0 AND char_start >= 0 AND char_end > char_start", name="ck_chunk_position"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    version_id: Mapped[str] = mapped_column(ForeignKey("document_versions.id", ondelete="CASCADE"), index=True)
    sequence: Mapped[int] = mapped_column(Integer)
    title_path: Mapped[str] = mapped_column(Text, default="")
    text: Mapped[str] = mapped_column(Text)
    char_start: Mapped[int] = mapped_column(Integer)
    char_end: Mapped[int] = mapped_column(Integer)


class Term(Base):
    __tablename__ = "terms"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    definition: Mapped[str | None] = mapped_column(Text)


class TermAlias(Base):
    __tablename__ = "term_aliases"
    __table_args__ = (UniqueConstraint("language", "alias", name="uq_term_alias"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    term_id: Mapped[str] = mapped_column(ForeignKey("terms.id", ondelete="CASCADE"), index=True)
    language: Mapped[str] = mapped_column(String(35))
    alias: Mapped[str] = mapped_column(String(255))


class IndexJob(Base):
    __tablename__ = "index_jobs"
    __table_args__ = (
        CheckConstraint("action IN ('upsert','delete')", name="ck_job_action"),
        CheckConstraint("status IN ('pending','running','succeeded','failed')", name="ck_job_status"),
        CheckConstraint("attempts >= 0", name="ck_job_attempts"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    version_id: Mapped[str] = mapped_column(ForeignKey("document_versions.id", ondelete="CASCADE"))
    action: Mapped[str] = mapped_column(String(16))
    status: Mapped[str] = mapped_column(String(16), default="pending", index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
