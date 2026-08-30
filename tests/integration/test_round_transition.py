from __future__ import annotations

import json
import gc
import sqlite3
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from mercadovoz_core.service import create_app
from mercadovoz_core.versioning import ENGINE_VERSION
from scripts.pilot.close_abandoned_round import close_round
from scripts.pilot.freeze_round import freeze_round


class RoundTransitionTests(unittest.TestCase):
    def test_round_id_closure_and_private_freeze_are_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            database = root / "pilot.db"
            app = create_app(
                database,
                pilot_access_codes={"P01": "round-transition-secret"},
                pilot_mode=True,
                pilot_round_id="P01_R2",
            )
            with TestClient(app) as client:
                access = client.post("/pilot/access", json={
                    "participant_id": "P01", "access_code": "round-transition-secret",
                }).json()
                headers = {"Authorization": f"Bearer {access['access_token']}"}
                session = client.post("/pilot/consent", headers=headers, json={
                    "consent_given": True,
                    "consent_version": "pilot-consent-v1",
                    "device_class": "mobile",
                }).json()
                session_headers = {**headers, "X-Pilot-Session": session["id"]}
                response = client.post("/pilot/interpret", headers=session_headers, json={
                    "text": "Vendí dos libras de tomate a tres dólares cada una",
                })
                self.assertEqual(200, response.status_code)
            app.state.storage.close()

            result = close_round(
                database,
                participant_id="P01",
                engine_version=ENGINE_VERSION,
                round_id="P01_R2",
                reason="synthetic transition test",
            )
            self.assertEqual(1, result["sessions_closed"])
            self.assertEqual("ABANDONED_SESSION_CLOSED", result["closure_type"])

            export = freeze_round(
                database,
                root / "private-export",
                participant_id="P01",
                engine_version=ENGINE_VERSION,
                round_id="P01_R2",
            )
            manifest = json.loads(Path(export["manifest"]).read_text(encoding="utf-8"))
            self.assertEqual(1, manifest["input_count"])
            self.assertEqual("P01_R2", manifest["round_id"])
            self.assertEqual(0, manifest["open_sessions"])

            connection = sqlite3.connect(database)
            try:
                stored_round = connection.execute(
                    "SELECT round_id FROM pilot_sessions"
                ).fetchone()[0]
                closure = json.loads(connection.execute(
                    "SELECT payload_json FROM pilot_events WHERE event_type = 'SESSION_ENDED'"
                ).fetchone()[0])
            finally:
                connection.close()
            self.assertEqual("P01_R2", stored_round)
            self.assertEqual("ABANDONED_SESSION_CLOSED", closure["closure_type"])
            del app
            gc.collect()


if __name__ == "__main__":
    unittest.main()
