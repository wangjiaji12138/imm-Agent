"""SQL-authoritative evidence gate with detached chunk results."""

from sqlalchemy.orm import Session

from app.modules.knowledge import repository
from app.modules.knowledge.schemas import ChunkSnapshot, SourceDetails, VerifiedEvidence


def eligible_chunks(session: Session, candidate_ids: list[str]) -> list[ChunkSnapshot]:
    """Keep candidate order; reject unpublished and superseded versions in SQL."""
    return [ChunkSnapshot.model_validate(chunk) for chunk in repository.eligible_chunks(session, candidate_ids)]


def search_evidence(session: Session, candidate_versions: dict[str, str], *, language=None,
                    document_id=None, published_from=None, published_to=None) -> dict[str, VerifiedEvidence]:
    found = repository.search_evidence(
        session, candidate_versions, language=language, document_id=document_id,
        published_from=published_from, published_to=published_to)
    return {chunk_id: VerifiedEvidence(chunk_id=chunk.id, document_id=doc.id, text=chunk.text,
                                       title=doc.title, organization=doc.organization,
                                       source_url=doc.source_url, published_at=doc.published_at)
            for chunk_id, (chunk, doc) in found.items()}


def get_source_details(session: Session, chunk_id: str) -> SourceDetails | None:
    found = repository.source_details(session, chunk_id)
    if found is None:
        return None
    chunk, doc = found
    return SourceDetails(chunk_id=chunk.id, document_id=doc.id, version_id=chunk.version_id,
                         text=chunk.text, title=doc.title, organization=doc.organization,
                         source_url=doc.source_url, published_at=doc.published_at,
                         title_path=chunk.title_path, char_start=chunk.char_start,
                         char_end=chunk.char_end)
