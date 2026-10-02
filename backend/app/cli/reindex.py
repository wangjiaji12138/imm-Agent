"""Rebuild Qdrant from current MySQL publication state."""

import argparse
import json
from uuid import UUID

import httpx
from sqlalchemy.exc import SQLAlchemyError

from app.core.settings import get_settings
from app.infrastructure.database import get_session
from app.infrastructure.embedding import APIEmbedding
from app.infrastructure.vector_store import QdrantStore
from app.modules.knowledge.service import fail_index_jobs, list_documents
from app.modules.retrieval.indexing import reindex_document


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--all", action="store_true")
    target.add_argument("--document", type=UUID)
    args = parser.parse_args()
    store = None
    try:
        embedding = APIEmbedding(get_settings())
        store = QdrantStore(get_settings())
        with get_session() as session:
            source_ids = [doc.id for doc in list_documents(session)] if args.all else [str(args.document)]
            session.rollback()
            failures = 0
            for source_id in source_ids:
                try:
                    with session.begin():
                        count = reindex_document(session, source_id, embedding, store)
                    print(json.dumps({"document_id": source_id, "chunks": count}, ensure_ascii=False))
                except (ValueError, SQLAlchemyError, httpx.HTTPError) as exc:
                    failures += 1
                    message = str(exc)
                    print(json.dumps({"document_id": source_id, "error": message}, ensure_ascii=False))
                    with session.begin():
                        fail_index_jobs(session, source_id, message)
        return 1 if failures else 0
    except (ValueError, SQLAlchemyError, httpx.HTTPError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 1
    finally:
        if store is not None:
            store.close()


if __name__ == "__main__":
    raise SystemExit(main())
