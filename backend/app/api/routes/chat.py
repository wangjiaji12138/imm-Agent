"""Chat endpoint for one routed question."""

from fastapi import APIRouter, Depends, Header, Request

from app.api.dependencies import ChatRuntime, get_chat_runtime
from app.api.schemas import ChatRequest, ChatResponse, ErrorEnvelope, SourceSummary
from app.modules.agent.workflow import run_question
from app.modules.conversations.service import authenticate, context, create, record

router = APIRouter()


@router.post("/api/chat", response_model=ChatResponse,
             responses={422: {"model": ErrorEnvelope}, 503: {"model": ErrorEnvelope}}, tags=["chat"])
def chat(body: ChatRequest, request: Request, runtime: ChatRuntime = Depends(get_chat_runtime),
         conversation_token: str | None = Header(default=None, alias="X-Conversation-Token")) -> ChatResponse:
    history = []
    if body.conversation_id:
        with runtime.session_factory() as session:
            conversation = authenticate(session, str(body.conversation_id), conversation_token)
            history = context(session, conversation)
    result = run_question(body.message, runtime.provider, runtime.search, history)
    issued_token = None
    conversation_id = body.conversation_id
    if result.answer.result_type in {"answer", "insufficient", "clarify"}:
        with runtime.session_factory() as session:
            with session.begin():
                if conversation_id:
                    conversation = authenticate(session, str(conversation_id), conversation_token)
                else:
                    conversation, issued_token = create(session)
                    conversation_id = conversation.id
                record(session, conversation, body.message, result.answer.answer, result.answer.result_type,
                       request.state.request_id)
    by_id = {item.chunk_id: item for item in result.evidence}
    sources = [SourceSummary(chunk_id=citation.chunk_id, title=by_id[citation.chunk_id].title,
                             organization=by_id[citation.chunk_id].organization,
                             source_url=by_id[citation.chunk_id].source_url,
                             published_at=by_id[citation.chunk_id].published_at)
               for citation in result.answer.citations]
    return ChatResponse(**result.answer.model_dump(), request_id=request.state.request_id,
                        conversation_id=conversation_id, conversation_token=issued_token, sources=sources)
