from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from mercadovoz_core.pilot_version import REAL_DEVELOPMENT_SCHEMA_VERSION
from mercadovoz_core.storage import SQLiteLedger


def write_jsonl(path: Path, records: list[dict]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Export private pilot data without secrets")
    parser.add_argument("--db", required=True, type=Path)
    parser.add_argument("--participant", required=True)
    parser.add_argument("--kind", choices=("operational", "real-development"), required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--csv", action="store_true", dest="write_csv")
    args = parser.parse_args()

    ledger = SQLiteLedger(args.db)
    try:
        records = (
            ledger.export_operational(args.participant)
            if args.kind == "operational"
            else ledger.export_real_development(args.participant)
        )
    finally:
        ledger.close()
    digest = write_jsonl(args.output, records)
    if args.write_csv and records:
        csv_path = args.output.with_suffix(".csv")
        with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=records[0].keys())
            writer.writeheader()
            for record in records:
                writer.writerow({
                    key: json.dumps(value, ensure_ascii=False, sort_keys=True)
                    if isinstance(value, (dict, list)) else value
                    for key, value in record.items()
                })
    print(json.dumps({
        "schema_version": REAL_DEVELOPMENT_SCHEMA_VERSION if args.kind == "real-development" else "operational-export-v1",
        "participant_id": args.participant,
        "records": len(records),
        "sha256": digest,
        "output": str(args.output),
    }, indent=2))


if __name__ == "__main__":
    main()
