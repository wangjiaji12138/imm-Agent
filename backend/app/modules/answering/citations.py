"""Reject references outside the current verified retrieval result."""

from app.modules.answering.schemas import AnswerResult
from app.modules.retrieval.schemas import SearchResult


def validate_citations(result: AnswerResult, evidence: list[SearchResult]) -> None:
    allowed = {item.chunk_id for item in evidence}
    if any(citation.chunk_id not in allowed for citation in result.citations):
        raise ValueError("模型引用了本次检索之外的片段")
    if result.evidence_status == "conflicting" and result.result_type == "answer":
        cited = {citation.chunk_id for citation in result.citations}
        if len(cited) < 2:
            raise ValueError("冲突回答需要分别引用不同片段")
