"""Verify a backup and restore only to an explicit, absent test database."""

import argparse
import json
import re
import subprocess
import tarfile
from pathlib import Path

from app.cli.backup import digest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compose", type=Path, default=Path("compose.yaml"))
    parser.add_argument("--backup-dir", type=Path, required=True)
    parser.add_argument("--target-database", required=True)
    parser.add_argument("--raw-target", type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"imm_agent_restore_[A-Za-z0-9_]+", args.target_database):
        parser.error("目标库必须以 imm_agent_restore_ 开头，且只含字母、数字和下划线")
    if args.raw_target.exists() and any(args.raw_target.iterdir()):
        parser.error("原始资料恢复目录必须为空")
    manifest = json.loads((args.backup_dir / "manifest.json").read_text(encoding="utf-8"))
    for name, expected in manifest["files"].items():
        if name not in {"mysql.sql", "raw.tar.gz"} or digest(args.backup_dir / name) != expected:
            parser.error("备份文件校验失败")
    compose = ["docker", "compose", "-f", str(args.compose.resolve()), "exec", "-T", "mysql", "sh", "-c"]
    query = f"SELECT COUNT(*) FROM information_schema.SCHEMATA WHERE SCHEMA_NAME='{args.target_database}'"
    check = subprocess.run(compose + ['MYSQL_PWD="$MYSQL_ROOT_PASSWORD" exec mysql -uroot -N -e "$1"', "sh", query],
                           check=True, capture_output=True, text=True)
    if check.stdout.strip() != "0":
        parser.error("目标库已存在，拒绝覆盖")
    subprocess.run(compose + [f'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" exec mysql -uroot -e "CREATE DATABASE {args.target_database}"'], check=True)
    with (args.backup_dir / "mysql.sql").open("rb") as handle:
        subprocess.run(compose + [f'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" exec mysql -uroot {args.target_database}'],
                       stdin=handle, check=True)
    args.raw_target.mkdir(parents=True, exist_ok=True)
    with tarfile.open(args.backup_dir / "raw.tar.gz", "r:gz") as archive:
        if any(member.name != "raw" and not member.name.startswith("raw/") for member in archive.getmembers()):
            parser.error("原始资料包路径无效")
        for member in archive.getmembers():
            if member.issym() or member.islnk() or member.isdev():
                parser.error("原始资料包包含不允许的文件类型")
            destination = (args.raw_target / member.name).resolve()
            if not destination.is_relative_to(args.raw_target.resolve()):
                parser.error("原始资料包路径越界")
        archive.extractall(args.raw_target)
    print(json.dumps({"database": args.target_database, "raw_target": str(args.raw_target)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
