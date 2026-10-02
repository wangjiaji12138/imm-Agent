"""Detached result of one routed question."""

from dataclasses import dataclass

from app.modules.answering.schemas import AnswerResult
from app.modules.retrieval.schemas import SearchResult


@dataclass(frozen=True)
class QuestionResult:
    answer: AnswerResult
    evidence: list[SearchResult]
