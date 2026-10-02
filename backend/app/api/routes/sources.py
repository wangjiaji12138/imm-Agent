"""Expand a current published source, rechecking SQL on every request."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import source_session
from app.api.schemas import ErrorEnvelope, SourceResponse
from app.modules.knowledge.evidence import get_source_details

router = APIRouter()


@router.get("/api/sources/{chunk_id}", response_model=SourceResponse,
            responses={404: {"model": ErrorEnvelope}, 422: {"model": ErrorEnvelope},
                       503: {"model": ErrorEnvelope}}, tags=["sources"])
def source(chunk_id: UUID, session: Session = Depends(source_session)) -> SourceResponse:
    details = get_source_details(session, str(chunk_id))
    if details is None:
        raise HTTPException(status_code=404, detail="source not found")
    return SourceResponse.model_validate(details.model_dump())
