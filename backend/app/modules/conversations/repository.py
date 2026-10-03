"""All message queries are scoped to an authenticated conversation."""

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.conversations.models import Conversation, Message


def get_conversation(session: Session, conversation_id: str) -> Conversation | None:
    return session.get(Conversation, conversation_id)


def recent_messages(session: Session, conversation_id: str, limit: int = 3) -> list[Message]:
    rows = session.scalars(select(Message).where(Message.conversation_id == conversation_id)
                           .order_by(Message.sequence.desc()).limit(limit)).all()
    return list(reversed(rows))


def append_message(session: Session, conversation: Conversation, question: str, answer: str,
                   result_type: str, request_id: str) -> Message:
    sequence = session.scalar(select(func.coalesce(func.max(Message.sequence), 0) + 1)
                              .where(Message.conversation_id == conversation.id))
    message = Message(conversation_id=conversation.id, sequence=sequence, question=question,
                      answer=answer, result_type=result_type, request_id=request_id)
    session.add(message)
    return message


def owns_request(session: Session, conversation_id: str, request_id: str) -> bool:
    return session.scalar(select(Message.id).where(Message.conversation_id == conversation_id,
                                                    Message.request_id == request_id)) is not None


def delete_older_than(session: Session, cutoff) -> int:
    return session.execute(delete(Conversation).where(Conversation.updated_at < cutoff)).rowcount
