"""SQL-authoritative evidence gate with detached chunk results."""

from sqlalchemy.orm import Session

from app.modules.knowledge import repository
from app.modules.knowledge.schemas import ChunkSnapshot


def eligible_chunks(session: Session, candidate_ids: list[str]) -> list[ChunkSnapshot]:
    """Keep candidate order; reject unpublished and superseded versions in SQL."""
    return [ChunkSnapshot.model_validate(chunk) for chunk in repository.eligible_chunks(session, candidate_ids)]
