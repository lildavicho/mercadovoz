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

sqlite3 "$source_backup" "PRAGMA integrity_check;" | grep -qx "ok"
if systemctl is-active --quiet mercadovoz-api; then
  echo "Stop mercadovoz-api before restoring." >&2
  exit 4
fi

umask 077
pre_restore="${db_path}.pre-restore-$(date -u +%Y%m%dT%H%M%SZ)"
if [[ -f "$db_path" ]]; then
  sqlite3 "$db_path" ".timeout 10000" ".backup '$pre_restore'"
fi
install -m 600 "$source_backup" "$db_path"
sqlite3 "$db_path" "PRAGMA integrity_check;" | grep -qx "ok"
echo "Restored $db_path; pre-restore copy: $pre_restore"
