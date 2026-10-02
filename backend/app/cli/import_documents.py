"""Import a JSONL manifest; text_path is relative to the working directory."""

import argparse
import json
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.infrastructure.database import get_session
from app.modules.knowledge.schemas import ImportRecord
from app.modules.knowledge.service import import_record


def import_manifest(session: Session, manifest: Path, base_dir: Path | None = None) -> dict[str, int]:
    counts = {"success": 0, "skipped": 0, "failed": 0}
    with manifest.open("rb") as stream:
        for number, raw_line in enumerate(stream, 1):
            try:
                line = raw_line.decode("utf-8-sig")
                record = ImportRecord.model_validate_json(line)
                with session.begin():
                    status, source_id = import_record(session, record, base_dir or Path.cwd())
                counts[status] += 1
                result = {"line": number, "status": status, "document_id": source_id}
            except (ValueError, OSError, SQLAlchemyError) as exc:
                session.rollback()
                counts["failed"] += 1
                if isinstance(exc, ValidationError):
                    message = "; ".join(f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in exc.errors(include_input=False))
                elif isinstance(exc, SQLAlchemyError):
                    message = "数据库写入失败（约束冲突或连接不可用），本行已回滚"
                else:
                    message = str(exc)
                result = {"line": number, "status": "failed", "error": message}
            print(json.dumps(result, ensure_ascii=False))
    print(json.dumps(counts, ensure_ascii=False))
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    try:
        with get_session() as session:
            counts = import_manifest(session, args.manifest)
        return int(counts["failed"] > 0)
    except OSError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
