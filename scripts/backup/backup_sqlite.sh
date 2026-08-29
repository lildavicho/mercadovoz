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
sqlite3 "$db_path" ".timeout 10000" ".backup '$target'"
sqlite3 "$target" "PRAGMA integrity_check;" | grep -qx "ok"
sha256sum "$target" > "$target.sha256"
echo "$target"
