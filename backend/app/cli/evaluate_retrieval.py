"""Generate a retrieval baseline from evals/questions.jsonl."""

import argparse
import json
from pathlib import Path

import httpx
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.settings import get_settings
from app.infrastructure.database import get_session
from app.infrastructure.embedding import APIEmbedding
from app.infrastructure.vector_store import QdrantStore
from app.modules.evaluation.dataset import evaluate_retrieval, write_baseline
from app.modules.retrieval.service import RetrievalTimeout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", type=Path, default=Path("evals/questions.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/retrieval-baseline.json"))
    args = parser.parse_args()
    store = None
    try:
        settings = get_settings()
        embedding = APIEmbedding(settings)
        store = QdrantStore(settings)
        with get_session() as session:
            result = evaluate_retrieval(args.questions, session, embedding, store)
        write_baseline(args.output, result)
        print(json.dumps({"output": str(args.output), "question_count": result["question_count"],
                          "mean_recall_at_5": result["mean_recall_at_5"]}, ensure_ascii=False))
        return 0
    except (OSError, ValueError, ValidationError, SQLAlchemyError, httpx.HTTPError, RetrievalTimeout) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 1
    finally:
        if store is not None:
            store.close()


if __name__ == "__main__":
    raise SystemExit(main())
