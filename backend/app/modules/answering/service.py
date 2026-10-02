"""Request routing and grounded structured answer generation."""

import json
import logging
from pathlib import Path
from time import perf_counter

from pydantic import ValidationError

from app.core.errors import DependencyTimeout
from app.modules.answering.citations import validate_citations
from app.modules.answering.ports import ModelProvider
from app.modules.answering.schemas import AnswerResult, RouteResult
from app.modules.retrieval.schemas import SearchResult

PROMPT_VERSION = "v1"
ROUTING_VERSION = "routing-v1"
PROMPT_DIR = Path(__file__).with_name("prompts")
logger = logging.getLogger(__name__)


class InvalidModelResponse(ValueError):
    """Model output does not satisfy the answer contract or evidence boundary."""


def _complete(provider: ModelProvider, system: str, user: str, version: str):
    started = perf_counter()
    try:
        try:
            output = provider.complete(system, user)
        except DependencyTimeout:
            output = provider.complete(system, user)
        return output
    finally:
        elapsed_ms = round((perf_counter() - started) * 1000, 2)
        if "output" in locals():
            logger.info("model_call model=%s prompt_version=%s elapsed_ms=%s input_tokens=%s output_tokens=%s",
                        output.model, version, elapsed_ms, output.input_tokens, output.output_tokens)
        else:
            logger.info("model_call prompt_version=%s elapsed_ms=%s failed=true", version, elapsed_ms)


def route_request(question: str, provider: ModelProvider) -> AnswerResult | None:
    """Return a non-search business result before retrieval, or None to search."""
    if not 2 <= len(question.strip()) <= 500:
        raise ValueError("问题长度必须为 2～500 字符")
    system = (PROMPT_DIR / "routing-v1.md").read_text(encoding="utf-8")
    output = _complete(provider, system, json.dumps({"question": question}, ensure_ascii=False), ROUTING_VERSION)
    try:
        route = RouteResult.model_validate_json(output.content)
        if route.result_type == "search":
            return None
        return AnswerResult(result_type=route.result_type, answer=route.response,
                            citations=[], evidence_status="not_applicable",
                            follow_up_question=route.response if route.result_type == "clarify" else None)
    except (ValidationError, ValueError) as exc:
        raise InvalidModelResponse("模型分流响应无效") from exc


def generate_answer(question: str, evidence: list[SearchResult], provider: ModelProvider) -> AnswerResult:
    """Use only the supplied verified snippets; empty evidence skips the model."""
    if not evidence:
        return AnswerResult(result_type="insufficient", answer="当前资料不足以回答这个问题。",
                            citations=[], evidence_status="insufficient", follow_up_question=None)
    system = (PROMPT_DIR / "v1.md").read_text(encoding="utf-8")
    supplied = [{"chunk_id": item.chunk_id, "text": item.text, "title": item.title,
                 "organization": item.organization, "published_at": item.published_at.isoformat()
                 if item.published_at else None} for item in evidence]
    user = json.dumps({"question": question, "evidence": supplied}, ensure_ascii=False)
    output = _complete(provider, system, user, PROMPT_VERSION)
    try:
        result = AnswerResult.model_validate_json(output.content)
        if result.result_type not in ("answer", "insufficient"):
            raise ValueError("知识生成只能返回回答或证据不足")
        validate_citations(result, evidence)
        return result
    except (ValidationError, ValueError) as exc:
        raise InvalidModelResponse("模型回答或引用无效") from exc
