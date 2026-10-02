"""Review and change document lifecycle state."""

import argparse
import json
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_session
from app.knowledge import TRANSITIONS, change_status, latest_version
from app.models import Document


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=[*TRANSITIONS, "list", "show"])
    parser.add_argument("document_id", nargs="?", type=UUID)
    args = parser.parse_args()
    if args.action != "list" and args.document_id is None:
        parser.error("此命令需要 document-id")
    try:
        with get_session() as session, session.begin():
            if args.action == "list":
                docs = session.scalars(select(Document).order_by(Document.source_url))
            elif args.action == "show":
                doc = session.get(Document, str(args.document_id))
                if doc is None:
                    raise ValueError("资料不存在")
                docs = [doc]
            else:
                docs = [change_status(session, str(args.document_id), args.action)]
            output = []
            for doc in docs:
                row = {"id": doc.id, "title": doc.title, "organization": doc.organization,
                       "source_url": doc.source_url, "status": doc.status,
                       "published_at": str(doc.published_at) if doc.published_at else None,
                       "fetched_at": doc.fetched_at.isoformat() + "Z"}
                if args.action == "show":
                    version = latest_version(session, doc.id)
                    row["version"] = {"id": version.id, "number": version.version_number,
                                      "content_hash": version.content_hash, "text": version.text} if version else None
                output.append(row)
        for row in output:
            print(json.dumps(row, ensure_ascii=False))
        return 0
    except (ValueError, SQLAlchemyError) as exc:
        message = "数据库操作失败" if isinstance(exc, SQLAlchemyError) else str(exc)
        print(json.dumps({"error": message}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
