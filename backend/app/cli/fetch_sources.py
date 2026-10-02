"""Download only the reviewed NCI seed allowlist; never arbitrary input URLs."""

import argparse
import json
from pathlib import Path

import httpx

from app.modules.knowledge.acquisition import fetch


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('data/raw/nci'))
    args = parser.parse_args()
    try:
        print(fetch(args.output))
        return 0
    except (httpx.HTTPError, OSError, ValueError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
