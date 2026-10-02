"""Validate all 20 questions and resolve evidence against the current SQL database."""

import argparse
import json
from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError

from app.infrastructure.database import get_session
from app.modules.evaluation.dataset import validate_evaluations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', nargs='?', type=Path, default=Path('evals/questions.jsonl'))
    args = parser.parse_args()
    try:
        with get_session() as session:
            result = validate_evaluations(args.path, session)
    except (OSError, ValueError, SQLAlchemyError) as exc:
        message = '数据库不可用，无法验证来源' if isinstance(exc, SQLAlchemyError) else str(exc)
        result = {'ready': False, 'errors': [message]}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result['ready'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
