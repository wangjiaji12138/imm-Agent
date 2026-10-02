"""Issue bearer secrets, authenticate before reading, and store bounded context."""

import hashlib
import hmac
import secrets
from datetime import datetime

from sqlalchemy.orm import Session

from app.modules.conversations.models import Conversation
from app.modules.conversations.repository import append_message, get_conversation, owns_request as query_owns_request, recent_messages
from app.modules.conversations.schemas import HistoryTurn


class ConversationNotFound(Exception):
    """A missing or unauthenticated conversation is intentionally indistinguishable."""


def _digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def authenticate(session: Session, conversation_id: str, credential: str | None) -> Conversation:
    conversation = get_conversation(session, conversation_id)
    if not conversation or not credential or not hmac.compare_digest(conversation.credential_hash, _digest(credential)):
        raise ConversationNotFound
    return conversation


def create(session: Session) -> tuple[Conversation, str]:
    token = secrets.token_urlsafe(32)
    conversation = Conversation(credential_hash=_digest(token))
    session.add(conversation)
    session.flush()
    return conversation, token


def context(session: Session, conversation: Conversation) -> list[HistoryTurn]:
    return [HistoryTurn(question=row.question, answer=row.answer[:600])
            for row in recent_messages(session, conversation.id)]


def record(session: Session, conversation: Conversation, question: str, answer: str, result_type: str,
           request_id: str) -> None:
    append_message(session, conversation, question, answer, result_type, request_id)
    conversation.updated_at = datetime.utcnow()


def owns_request(session: Session, conversation_id: str, request_id: str) -> bool:
    return query_owns_request(session, conversation_id, request_id)
