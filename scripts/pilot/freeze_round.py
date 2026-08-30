"""Create immutable private exports and a hash manifest for one engine round."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = (len(ordered) - 1) * fraction
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (index - lower)


def freeze_round(
    db_path: Path,
    output_dir: Path,
    *,
    participant_id: str,
    engine_version: str,
    round_id: str,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        session_columns = {row[1] for row in connection.execute("PRAGMA table_info(pilot_sessions)")}
        where = "participant_id = ? AND engine_version = ?"
        parameters: list[object] = [participant_id, engine_version]
        if "round_id" in session_columns:
            where += " AND round_id = ?"
            parameters.append(round_id)
        sessions = connection.execute(
            f"SELECT * FROM pilot_sessions WHERE {where} ORDER BY started_at", parameters
        ).fetchall()
        if not sessions:
            raise RuntimeError("round has no sessions")
        if any(session["ended_at"] is None for session in sessions):
            raise RuntimeError("round still has open sessions")
        session_ids = [session["id"] for session in sessions]
        placeholders = ",".join("?" for _ in session_ids)
        events = connection.execute(
            f"SELECT * FROM pilot_events WHERE session_id IN ({placeholders}) ORDER BY occurred_at, id",
            session_ids,
        ).fetchall()
        grouped: dict[str, list[sqlite3.Row]] = defaultdict(list)
        for event in events:
            if event["input_id"]:
                grouped[event["input_id"]].append(event)
        operations = connection.execute(
            f"SELECT * FROM operations WHERE session_id IN ({placeholders}) ORDER BY confirmed_at",
            session_ids,
        ).fetchall()
        operations_by_input = {row["input_id"]: row for row in operations}
        records: list[dict[str, Any]] = []
        for input_id, input_events in grouped.items():
            submitted = next((row for row in input_events if row["event_type"] == "TEXT_SUBMITTED"), None)
            interpreted = next((row for row in input_events if row["event_type"] == "INTERPRETATION_CREATED"), None)
            if submitted is None or interpreted is None:
                continue
            submitted_payload = json.loads(submitted["payload_json"])
            interpreted_payload = json.loads(interpreted["payload_json"])
            initial_fields = interpreted_payload.get("fields", {})
            predicted_operation = interpreted_payload.get("predicted_operation")
            initial_operation = (
                {"type": predicted_operation, **initial_fields}
                if isinstance(predicted_operation, str)
                else predicted_operation
            )
            terminal = next((row for row in reversed(input_events) if row["event_type"] in {
                "OPERATION_CONFIRMED", "OPERATION_REJECTED", "OPERATION_CANCELLED"
            }), None)
            operation = operations_by_input.get(input_id)
            accepted = json.loads(operation["payload_json"]) if operation else None
            records.append({
                "record_id": input_id,
                "dataset_class": "REAL_DEVELOPMENT",
                "round_id": round_id,
                "participant_id": participant_id,
                "session_id": submitted["session_id"],
                "original_text": submitted_payload["original_text"],
                "engine_version": engine_version,
                "initial_interpretation_state": interpreted_payload.get("interpretation_state"),
                "initial_prediction": initial_operation,
                "initial_fields": initial_fields,
                "missing_fields": interpreted_payload.get("missing_fields", []),
                "warnings": interpreted_payload.get("warnings", []),
                "context_used": interpreted_payload.get("context_used", []),
                "safety_events": interpreted_payload.get("safety_rules_triggered", []),
                "expected_or_final_accepted_operation": accepted,
                "ground_truth_status": "USER_ACCEPTED_OPERATION" if accepted else "NOT_ESTABLISHED",
                "corrections": [json.loads(row["payload_json"]) for row in input_events if row["event_type"] == "OPERATION_CORRECTED"],
                "outcome": terminal["event_type"] if terminal else "OPEN",
                "timestamps": {
                    "submitted_at": submitted["occurred_at"],
                    "interpreted_at": interpreted["occurred_at"],
                    "terminal_at": terminal["occurred_at"] if terminal else None,
                },
                "interpretation_latency_ms": interpreted["duration_ms"],
            })

        prefix = f"{participant_id.lower()}-{round_id.rsplit('_', 1)[-1].lower()}"
        jsonl_path = output_dir / f"{prefix}-real-development.jsonl"
        with jsonl_path.open("w", encoding="utf-8", newline="\n") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        events_path = output_dir / f"{prefix}-events.csv"
        event_fields = [
            "id", "event_type", "session_id", "participant_id", "input_id",
            "occurred_at", "engine_version", "duration_ms", "payload_json",
        ]
        with events_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=event_fields)
            writer.writeheader()
            for event in events:
                writer.writerow({field: event[field] for field in event_fields})

        operations_path = output_dir / f"{prefix}-operations.csv"
        operation_fields = [row[1] for row in connection.execute("PRAGMA table_info(operations)")]
        with operations_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=operation_fields)
            writer.writeheader()
            for operation in operations:
                writer.writerow({field: operation[field] for field in operation_fields})

        event_counts = Counter(event["event_type"] for event in events)
        latencies = [float(event["duration_ms"]) for event in events if event["event_type"] == "INTERPRETATION_CREATED" and event["duration_ms"] is not None]
        summary = {
            "participant_id": participant_id,
            "round_id": round_id,
            "dataset_class": "REAL_DEVELOPMENT",
            "engine_version": engine_version,
            "sessions": len(sessions),
            "open_sessions": 0,
            "input_count": event_counts["TEXT_SUBMITTED"],
            "event_count": len(events),
            "operation_count": len(operations),
            "event_counts": dict(sorted(event_counts.items())),
            "interpretation_latency_ms": {
                "median": median(latencies) if latencies else None,
                "p95": percentile(latencies, 0.95),
            },
            "started_at": min(session["started_at"] for session in sessions),
            "ended_at": max(session["ended_at"] for session in sessions),
        }
        summary_path = output_dir / f"{prefix}-summary.json"
        write_json(summary_path, summary)
        created_at = datetime.now(timezone.utc).isoformat()
        versions = {
            key: sorted({session[key] for session in sessions})
            for key in ("engine_version", "parser_version", "schema_version", "pilot_version", "ui_version", "consent_version")
        }
        manifest = {
            **summary,
            "real_interview": False,
            "export_created_at": created_at,
            "versions": versions,
            "files": {
                jsonl_path.name: {"sha256": digest(jsonl_path), "records": len(records)},
                events_path.name: {"sha256": digest(events_path), "records": len(events)},
                operations_path.name: {"sha256": digest(operations_path), "records": len(operations)},
                summary_path.name: {"sha256": digest(summary_path)},
            },
        }
        manifest_path = output_dir / f"{prefix}-manifest.json"
        write_json(manifest_path, manifest)
        manifest_hash = digest(manifest_path)
        checksum_path = output_dir / f"{prefix}-manifest.json.sha256"
        checksum_path.write_text(f"{manifest_hash}  {manifest_path.name}\n", encoding="ascii")
        for path in (jsonl_path, events_path, operations_path, summary_path, manifest_path, checksum_path):
            os.chmod(path, 0o600)
        return {
            "output_dir": str(output_dir),
            "manifest": str(manifest_path),
            "manifest_sha256": manifest_hash,
            "files": manifest["files"],
        }
    finally:
        connection.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--participant", required=True)
    parser.add_argument("--engine", required=True)
    parser.add_argument("--round", required=True, dest="round_id")
    args = parser.parse_args()
    print(json.dumps(freeze_round(
        args.db,
        args.output_dir,
        participant_id=args.participant,
        engine_version=args.engine,
        round_id=args.round_id,
    ), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
