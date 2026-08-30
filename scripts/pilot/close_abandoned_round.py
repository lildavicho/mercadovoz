"""Administratively close abandoned pilot sessions without impersonating the user."""

from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def close_round(
    db_path: Path,
    *,
    participant_id: str,
    engine_version: str,
    round_id: str,
    reason: str,
) -> dict[str, object]:
    connection = sqlite3.connect(db_path, timeout=10)
    connection.row_factory = sqlite3.Row
    try:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(pilot_events)")}
        session_columns = {row[1] for row in connection.execute("PRAGMA table_info(pilot_sessions)")}
        round_filter = " AND round_id = ?" if "round_id" in session_columns else ""
        parameters: tuple[object, ...] = (
            (participant_id, engine_version, round_id)
            if round_filter else (participant_id, engine_version)
        )
        sessions = connection.execute(
            """
            SELECT * FROM pilot_sessions
            WHERE participant_id = ? AND engine_version = ? AND ended_at IS NULL
            """ + round_filter + """
            ORDER BY started_at
            """,
            parameters,
        ).fetchall()
        foreign_open = connection.execute(
            """
            SELECT COUNT(*) FROM pilot_sessions
            WHERE participant_id = ? AND engine_version <> ? AND ended_at IS NULL
            """,
            (participant_id, engine_version),
        ).fetchone()[0]
        if foreign_open:
            raise RuntimeError("participant has open sessions from another engine version")

        closed_at = utc_now()
        revoked = 0
        connection.execute("BEGIN IMMEDIATE")
        for session in sessions:
            payload = json.dumps(
                {
                    "event_schema_version": "pilot-event-v1",
                    "closure_type": "ABANDONED_SESSION_CLOSED",
                    "closed_by": "OPERATOR_TOOL",
                    "reason": reason,
                    "round_id": round_id,
                },
                ensure_ascii=False,
                sort_keys=True,
            )
            fields = [
                "id", "event_type", "session_id", "participant_id", "input_id",
                "occurred_at", "engine_version", "payload_json", "duration_ms",
            ]
            values: list[object] = [
                str(uuid4()), "SESSION_ENDED", session["id"], participant_id, None,
                closed_at, engine_version, payload, None,
            ]
            if "round_id" in columns:
                fields.append("round_id")
                values.append(round_id)
            placeholders = ", ".join("?" for _ in fields)
            connection.execute(
                f"INSERT INTO pilot_events ({', '.join(fields)}) VALUES ({placeholders})",
                values,
            )
            connection.execute(
                "UPDATE pilot_sessions SET ended_at = ?, event_count = event_count + 1 WHERE id = ?",
                (closed_at, session["id"]),
            )
        cursor = connection.execute(
            """
            UPDATE access_sessions SET revoked_at = ?
            WHERE participant_id = ? AND revoked_at IS NULL
            """,
            (closed_at, participant_id),
        )
        revoked = cursor.rowcount
        connection.commit()
        return {
            "participant_id": participant_id,
            "round_id": round_id,
            "engine_version": engine_version,
            "closure_type": "ABANDONED_SESSION_CLOSED",
            "closed_at": closed_at,
            "sessions_closed": len(sessions),
            "access_sessions_revoked": revoked,
            "session_ids": [session["id"] for session in sessions],
        }
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True, type=Path)
    parser.add_argument("--participant", required=True)
    parser.add_argument("--engine", required=True)
    parser.add_argument("--round", required=True, dest="round_id")
    parser.add_argument("--reason", default="inactive session closed at round freeze")
    args = parser.parse_args()
    print(json.dumps(close_round(
        args.db,
        participant_id=args.participant,
        engine_version=args.engine,
        round_id=args.round_id,
        reason=args.reason,
    ), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
