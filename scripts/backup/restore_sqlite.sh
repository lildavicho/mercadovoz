#!/usr/bin/env bash
set -euo pipefail

source_backup="${1:-}"
confirmation="${2:-}"
db_path="${MERCADOVOZ_DB:-}"

if [[ "$confirmation" != "RESTORE-MERCADOVOZ" ]]; then
  echo "Confirmation must equal RESTORE-MERCADOVOZ." >&2
  exit 2
fi
if [[ -z "$db_path" || ! -f "$source_backup" ]]; then
  echo "Set MERCADOVOZ_DB and provide an existing backup." >&2
  exit 3
fi

integrity_check() {
  local path="$1"
  if command -v sqlite3 >/dev/null 2>&1; then
    sqlite3 "$path" "PRAGMA integrity_check;" | grep -qx "ok"
  elif command -v python3 >/dev/null 2>&1; then
    python3 - "$path" <<'PY'
import sqlite3
import sys
with sqlite3.connect(sys.argv[1]) as database:
    if database.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
        raise SystemExit("database integrity check failed")
PY
  else
    echo "Neither sqlite3 nor python3 is available." >&2
    return 1
  fi
}

consistent_copy() {
  local source="$1"
  local target="$2"
  if command -v sqlite3 >/dev/null 2>&1; then
    sqlite3 "$source" ".timeout 10000" ".backup '$target'"
  else
    python3 - "$source" "$target" <<'PY'
import sqlite3
import sys
with sqlite3.connect(sys.argv[1], timeout=10) as source:
    with sqlite3.connect(sys.argv[2]) as target:
        source.backup(target)
PY
  fi
}

integrity_check "$source_backup"
if command -v systemctl >/dev/null 2>&1 && systemctl is-active --quiet mercadovoz-api; then
  echo "Stop mercadovoz-api before restoring." >&2
  exit 4
fi

umask 077
pre_restore="${db_path}.pre-restore-$(date -u +%Y%m%dT%H%M%SZ)"
if [[ -f "$db_path" ]]; then
  consistent_copy "$db_path" "$pre_restore"
fi
install -m 600 "$source_backup" "$db_path"
integrity_check "$db_path"
echo "Restored $db_path; pre-restore copy: $pre_restore"
