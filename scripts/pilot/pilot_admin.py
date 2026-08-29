from __future__ import annotations

import argparse
import json
from pathlib import Path

from mercadovoz_core.storage import SQLiteLedger


ERROR_CATEGORIES = {
    "INTENT", "AMOUNT", "QUANTITY", "UNIT", "PRODUCT", "CUSTOMER", "CONTEXT",
    "COMPOUND", "STATE_VS_EVENT", "PERSONAL_VS_BUSINESS", "APPROXIMATION",
    "CORRECTION", "UX", "PERFORMANCE", "SCHEMA_GAP", "OTHER",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Private, local pilot administration")
    parser.add_argument("--db", required=True, type=Path)
    sub = parser.add_subparsers(dest="command", required=True)

    metrics = sub.add_parser("metrics")
    metrics.add_argument("--participant")

    annotate = sub.add_parser("annotate")
    annotate.add_argument("--participant", required=True)
    annotate.add_argument("--input", required=True)
    annotate.add_argument("--category", required=True, choices=sorted(ERROR_CATEGORIES))
    annotate.add_argument("--critical", action="store_true")
    annotate.add_argument("--note")

    delete = sub.add_parser("delete-participant")
    delete.add_argument("--participant", required=True)
    delete.add_argument("--confirm", required=True, help="Must exactly equal DELETE-PNN")

    args = parser.parse_args()
    ledger = SQLiteLedger(args.db)
    try:
        if args.command == "metrics":
            result = ledger.metrics(args.participant)
        elif args.command == "annotate":
            result = ledger.annotate_input(
                input_id=args.input,
                participant_id=args.participant,
                category=args.category,
                critical_financial_error=args.critical,
                note=args.note,
            )
        else:
            if args.confirm != f"DELETE-{args.participant}":
                raise SystemExit("confirmation did not match; no data was deleted")
            result = ledger.delete_participant(args.participant)
    finally:
        ledger.close()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
