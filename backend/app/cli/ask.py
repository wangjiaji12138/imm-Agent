"""Ask one question and print a structured answer with resolvable sources."""

import argparse
import json

import httpx
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.errors import DependencyTimeout, DependencyUnavailable
from app.core.settings import get_settings
from app.infrastructure.database import get_session
from app.infrastructure.embedding import APIEmbedding
from app.infrastructure.llm import APIModel
from app.infrastructure.vector_store import QdrantStore
from app.modules.answering.service import InvalidModelResponse, generate_answer, route_request
from app.modules.retrieval.service import search_knowledge


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question", help="中文科普问题")
    args = parser.parse_args()
    store = None
    try:
        settings = get_settings()
        provider = APIModel(settings)
        routed = route_request(args.question, provider)
        evidence = []
        if routed is None:
            embedding = APIEmbedding(settings)
            store = QdrantStore(settings)
            with get_session() as session:
                evidence = search_knowledge(args.question, limit=5, session=session,
                                            embedding=embedding, store=store)
            answer = generate_answer(args.question, evidence, provider)
        else:
            answer = routed
        by_id = {item.chunk_id: item for item in evidence}
        result = answer.model_dump()
        result["sources"] = [{"chunk_id": citation.chunk_id, "title": by_id[citation.chunk_id].title,
                              "organization": by_id[citation.chunk_id].organization,
                              "source_url": by_id[citation.chunk_id].source_url,
                              "published_at": by_id[citation.chunk_id].published_at.isoformat()
                              if by_id[citation.chunk_id].published_at else None,
                              "text": by_id[citation.chunk_id].text}
                             for citation in answer.citations]
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ValueError, ValidationError, SQLAlchemyError, httpx.HTTPError,
            DependencyTimeout, DependencyUnavailable, InvalidModelResponse) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 1
    finally:
        if store is not None:
            store.close()


if __name__ == "__main__":
    raise SystemExit(main())
