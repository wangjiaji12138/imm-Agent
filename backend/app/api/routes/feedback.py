"""Authenticated answer feedback endpoint."""

from uuid import UUID

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.api.dependencies import source_session
from app.api.schemas import ErrorEnvelope
from app.modules.feedback.schemas import FeedbackInput, FeedbackResult
from app.modules.feedback.service import submit

router = APIRouter()


@router.post("/api/feedback", response_model=FeedbackResult,
             responses={404: {"model": ErrorEnvelope}, 422: {"model": ErrorEnvelope}}, tags=["feedback"])
def feedback(body: FeedbackInput, conversation_id: UUID = Header(alias="X-Conversation-ID"),
             conversation_token: str = Header(alias="X-Conversation-Token"),
             session: Session = Depends(source_session)) -> FeedbackResult:
    with session.begin():
        return submit(session, str(conversation_id), conversation_token, body)
