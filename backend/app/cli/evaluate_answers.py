"""Run the held-out questions and write an immutable, timestamped report."""

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from time import perf_counter

from app.api.dependencies import get_chat_runtime
from app.core.settings import get_settings
from app.infrastructure.database import get_session
from app.modules.agent.workflow import run_question
from app.modules.conversations.schemas import HistoryTurn
from app.modules.evaluation.schemas import EvaluationQuestion
from app.modules.knowledge.evidence import get_source_details


def percentile_95(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return round(ordered[max(0, (95 * len(ordered) + 99) // 100 - 1)], 2)


def run(questions_path: Path, output_dir: Path) -> Path:
    raw = questions_path.read_bytes()
    questions = [EvaluationQuestion.model_validate_json(line) for line in raw.splitlines() if line.strip()]
    held_out = [item for item in questions if item.split == "test"]
    settings = get_settings()
    runtime = get_chat_runtime()
    rows = []
    for question in held_out:
        history = []
        for index in range(0, len(question.history) - 1, 2):
            pair = question.history[index:index + 2]
            if pair[0].role == "user" and pair[1].role == "assistant":
                history.append(HistoryTurn(question=pair[0].content, answer=pair[1].content))
        searched = []
        usage = {"input_tokens": 0, "output_tokens": 0}

        class MeteredProvider:
            def complete(self, system, user):
                output = runtime.provider.complete(system, user)
                usage["input_tokens"] += output.input_tokens or 0
                usage["output_tokens"] += output.output_tokens or 0
                return output

        def search(query):
            result = runtime.search(query)
            searched.extend(result)
            return result

        started = perf_counter()
        row = {"id": question.id, "category": question.category,
               "expected_behavior": question.expected_behavior, "expected_source_ids": [str(x) for x in question.expected_source_ids]}
        try:
            result = run_question(question.question, MeteredProvider(), search, history)
            cited = [item.chunk_id for item in result.answer.citations]
            with get_session() as session:
                resolved = {item: get_source_details(session, item) for item in cited}
            row.update(success=True, actual_behavior=result.answer.result_type,
                       answer=result.answer.answer, cited_chunk_ids=cited,
                       cited_resolved=sum(value is not None for value in resolved.values()),
                       cited_total=len(cited), top_5_document_ids=[item.document_id for item in searched[:5]],
                       has_unsourced_key_claim=result.answer.result_type == "answer" and not cited,
                       withdrew_hit=any(value is None for value in resolved.values()),
                       input_tokens=usage["input_tokens"], output_tokens=usage["output_tokens"])
        except Exception as exc:
            row.update(success=False, error_type=type(exc).__name__, actual_behavior=None,
                       cited_resolved=0, cited_total=0, top_5_document_ids=[],
                       has_unsourced_key_claim=False, withdrew_hit=False)
        row["estimated_model_cost_cny"] = round((usage["input_tokens"] * 0.8 +
                                                  usage["output_tokens"] * 2) / 1_000_000, 6)
        row["elapsed_ms"] = round((perf_counter() - started) * 1000, 2)
        expected = set(row["expected_source_ids"])
        row["recall_at_5"] = len(expected.intersection(row["top_5_document_ids"])) / len(expected) if expected else None
        row["behavior_correct"] = row["actual_behavior"] == row["expected_behavior"]
        rows.append(row)
    scored = [row["recall_at_5"] for row in rows if row["recall_at_5"] is not None]
    total_citations = sum(row["cited_total"] for row in rows)
    unanswerable = [row for row in rows if row["category"] == "unanswerable"]
    report = {
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_sha256": hashlib.sha256(raw).hexdigest(), "test_count": len(rows),
        "embedding_model": settings.embedding_model, "generation_model": settings.model_name,
        "routing_prompt": "routing-v2", "answer_prompt": "v1", "collection": settings.qdrant_collection,
        "metrics": {"recall_at_5": round(mean(scored), 4) if scored else None,
                    "citation_resolution_rate": sum(row["cited_resolved"] for row in rows) / total_citations if total_citations else None,
                    "insufficient_behavior_rate": sum(row["behavior_correct"] for row in unanswerable) / len(unanswerable) if unanswerable else None,
                    "request_success_rate": sum(row["success"] for row in rows) / len(rows) if rows else None,
                    "p95_latency_ms": percentile_95([row["elapsed_ms"] for row in rows]),
                    "estimated_cost_per_request_cny": round(mean(row["estimated_model_cost_cny"] for row in rows), 6) if rows else None,
                    "cost_note": "qwen-plus 北京区 0.8/2 元每百万输入/输出 token；不含 Embedding 查询、免费额度或缓存优惠",
                    "withdrawn_hits": sum(row["withdrew_hit"] for row in rows),
                    "unsourced_key_claims": sum(row["has_unsourced_key_claim"] for row in rows)},
        "questions": rows,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = datetime.now(timezone.utc).strftime("evaluation-%Y%m%dT%H%M%S%fZ.json")
    path = output_dir / filename
    with path.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", type=Path, default=Path("evals/questions.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/evaluations"))
    args = parser.parse_args()
    path = run(args.questions, args.output_dir)
    print(json.dumps({"report": str(path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
