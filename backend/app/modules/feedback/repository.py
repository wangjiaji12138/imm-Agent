"""Upsert after ownership verification; uniqueness is enforced in SQL."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.feedback.models import Feedback


def save(session: Session, conversation_id: str, request_id: str, rating: str,
         note: str | None) -> Feedback:
    row = session.scalar(select(Feedback).where(Feedback.conversation_id == conversation_id,
                                                Feedback.request_id == request_id))
    if row is None:
        row = Feedback(conversation_id=conversation_id, request_id=request_id, rating=rating, note=note)
        session.add(row)
    else:
        row.rating = rating
        row.note = note
        row.updated_at = datetime.utcnow()
    return row
