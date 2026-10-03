"""Back up Compose MySQL and raw source files without storing credentials."""

import argparse
import hashlib
import json
import subprocess
import tarfile
from datetime import datetime, timezone
from pathlib import Path


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compose", type=Path, default=Path("compose.yaml"))
    parser.add_argument("--raw", type=Path, default=Path("data/raw"))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    sql_path = output / "mysql.sql"
    command = ["docker", "compose", "-f", str(args.compose.resolve()), "exec", "-T", "mysql", "sh", "-c",
               'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" exec mysqldump -uroot --single-transaction --routines --triggers "$MYSQL_DATABASE"']
    with sql_path.open("wb") as handle:
        subprocess.run(command, stdout=handle, check=True)
    raw_path = output / "raw.tar.gz"
    with tarfile.open(raw_path, "w:gz") as archive:
        if args.raw.exists():
            archive.add(args.raw, arcname="raw")
    manifest = {"created_at_utc": datetime.now(timezone.utc).isoformat(),
                "files": {path.name: digest(path) for path in (sql_path, raw_path)}}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"backup": str(output), "files": list(manifest["files"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
