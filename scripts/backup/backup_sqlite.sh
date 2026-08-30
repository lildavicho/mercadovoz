#!/usr/bin/env bash
set -euo pipefail

db_path="${MERCADOVOZ_DB:-}"
backup_dir="${MERCADOVOZ_BACKUP_DIR:-}"

if [[ -z "$db_path" || -z "$backup_dir" ]]; then
  echo "Set MERCADOVOZ_DB and MERCADOVOZ_BACKUP_DIR." >&2
  exit 2
fi
if [[ ! -f "$db_path" ]]; then
  echo "Database not found: $db_path" >&2
  exit 3
fi

mkdir -p "$backup_dir"
umask 077
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
target="$backup_dir/mercadovoz-$timestamp.sqlite"
if command -v sqlite3 >/dev/null 2>&1; then
  sqlite3 "$db_path" ".timeout 10000" ".backup '$target'"
  sqlite3 "$target" "PRAGMA integrity_check;" | grep -qx "ok"
elif command -v python3 >/dev/null 2>&1; then
  python3 - "$db_path" "$target" <<'PY'
import sqlite3
import sys

source_path, target_path = sys.argv[1:]
with sqlite3.connect(source_path, timeout=10) as source:
    with sqlite3.connect(target_path) as target:
        source.backup(target)
with sqlite3.connect(target_path) as restored:
    if restored.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
        raise SystemExit("backup integrity check failed")
PY
else
  echo "Neither sqlite3 nor python3 is available for a consistent backup." >&2
  exit 4
fi
sha256sum "$target" > "$target.sha256"
echo "$target"
