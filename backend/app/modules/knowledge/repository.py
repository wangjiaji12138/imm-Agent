"""Knowledge SQL access. Only this module and knowledge services handle ORM rows.

The caller owns the Session and transaction; these functions never commit.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.knowledge.models import Chunk, Document, DocumentVersion, IndexJob


def latest_version(session: Session, source_id: str) -> DocumentVersion | None:
    return session.scalar(select(DocumentVersion).where(DocumentVersion.document_id == source_id)
                          .order_by(DocumentVersion.version_number.desc()).limit(1))


def get_document(session: Session, source_id: str) -> Document | None:
    return session.get(Document, source_id, populate_existing=True)


def list_documents(session: Session) -> list[Document]:
    return list(session.scalars(select(Document).order_by(Document.source_url)))


def lock_document(session: Session, source_id: str) -> Document | None:
    return session.scalar(select(Document).where(Document.id == source_id).with_for_update())


def lock_source(session: Session, source_key: str) -> Document | None:
    return session.scalar(select(Document).where(Document.source_key == source_key).with_for_update())


def has_version_hash(session: Session, source_id: str, digest: str) -> bool:
    return session.scalar(select(DocumentVersion.id).where(
        DocumentVersion.document_id == source_id, DocumentVersion.content_hash == digest)) is not None


def add_index_job(session: Session, source_id: str, version_id: str, action: str) -> None:
    session.add(IndexJob(document_id=source_id, version_id=version_id, action=action))


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


def search_evidence(session: Session, candidate_versions: dict[str, str], *, language: str | None,
                    document_id: str | None, published_from, published_to) -> dict[str, tuple[Chunk, Document]]:
    """Verify vector candidates against current SQL publication, version and metadata."""
    if not candidate_versions:
        return {}
    latest = select(DocumentVersion.document_id, func.max(DocumentVersion.version_number).label("number")) \
        .group_by(DocumentVersion.document_id).subquery()
    statement = select(Chunk, Document).join(DocumentVersion, Chunk.version_id == DocumentVersion.id) \
        .join(Document, DocumentVersion.document_id == Document.id) \
        .join(latest, (latest.c.document_id == Document.id) & (latest.c.number == DocumentVersion.version_number)) \
        .where(Chunk.id.in_(candidate_versions), Document.status == "published") \
        .execution_options(populate_existing=True)
    if language is not None:
        statement = statement.where(Document.language == language)
    if document_id is not None:
        statement = statement.where(Document.id == document_id)
    if published_from is not None:
        statement = statement.where(Document.published_at >= published_from)
    if published_to is not None:
        statement = statement.where(Document.published_at <= published_to)
    return {chunk.id: (chunk, doc) for chunk, doc in session.execute(statement)
            if chunk.version_id == candidate_versions[chunk.id]}
