"""Retrieval baseline over the fixed evaluation questions."""

import json
from pathlib import Path
from time import perf_counter

from app.modules.evaluation.schemas import EvaluationQuestion
from app.modules.retrieval.service import search_knowledge


def evaluate_retrieval(path: Path, session, embedding, store) -> dict:
    questions = [EvaluationQuestion.model_validate_json(line) for line in
                 path.read_text(encoding="utf-8").splitlines() if line.strip()]
    rows = []
    for question in questions:
        start = perf_counter()
        results = search_knowledge(question.question, limit=5, session=session,
                                   embedding=embedding, store=store)
        elapsed_ms = round((perf_counter() - start) * 1000, 2)
        expected = {str(value) for value in question.expected_source_ids}
        found = {item.document_id for item in results}
        rows.append({"id": question.id, "split": question.split, "question": question.question,
                     "top_5": [{"chunk_id": item.chunk_id, "document_id": item.document_id,
                                "score": item.score} for item in results],
                     "recall_at_5": len(expected & found) / len(expected) if expected else None,
                     "elapsed_ms": elapsed_ms})
    scored = [row["recall_at_5"] for row in rows if row["recall_at_5"] is not None]
    return {"question_count": len(rows), "mean_recall_at_5": sum(scored) / len(scored) if scored else None,
            "questions": rows}


def write_baseline(path: Path, result: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
