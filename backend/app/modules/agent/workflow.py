"""One-turn question flow: route, search, then generate from verified evidence."""

from app.modules.agent.state import QuestionResult
from app.modules.answering.schemas import AnswerResult
from app.modules.answering.service import classify_request, generate_answer
from app.modules.conversations.schemas import HistoryTurn


def run_question(message: str, provider, search, history: list[HistoryTurn] | None = None) -> QuestionResult:
    route = classify_request(message, provider, history)
    if route.result_type != "search":
        answer = AnswerResult(result_type=route.result_type, answer=route.response,
                              citations=[], evidence_status="not_applicable",
                              follow_up_question=route.response if route.result_type == "clarify" else None)
        return QuestionResult(answer=answer, evidence=[])
    query = route.search_query or message
    evidence = search(query)
    return QuestionResult(answer=generate_answer(query, evidence, provider), evidence=evidence)
