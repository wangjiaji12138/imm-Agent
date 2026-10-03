"""Delete conversations older than the configured retention window."""

import argparse
from app.infrastructure.database import get_session
from app.modules.conversations.service import prune


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=30)
    args = parser.parse_args()
    if not 1 <= args.days <= 3650:
        parser.error("days 必须在 1～3650 之间")
    with get_session() as session, session.begin():
        count = prune(session, args.days)
    print({"deleted_conversations": count, "older_than_days": args.days})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
