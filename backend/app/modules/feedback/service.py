"""Authenticate conversation and answer ownership before updating feedback."""

from sqlalchemy.orm import Session

from app.modules.conversations.service import ConversationNotFound, authenticate, owns_request
from app.modules.feedback.repository import save
from app.modules.feedback.schemas import FeedbackInput, FeedbackResult


def submit(session: Session, conversation_id: str, token: str | None,
           body: FeedbackInput) -> FeedbackResult:
    conversation = authenticate(session, conversation_id, token)
    if not owns_request(session, conversation.id, str(body.request_id)):
        raise ConversationNotFound
    row = save(session, conversation.id, str(body.request_id), body.rating, body.note)
    return FeedbackResult(request_id=body.request_id, rating=row.rating, note=row.note)
