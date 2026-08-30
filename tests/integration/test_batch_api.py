from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from mercadovoz_core.service import create_app


class BatchApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        app = create_app(
            Path(self.directory.name) / "pilot.db",
            pilot_access_codes={"P01": "private-code-01", "P02": "private-code-02"},
            pilot_mode=True,
            pilot_round_id="SYNTHETIC_QA",
            batch_experiment=True,
        )
        self.client = TestClient(app)
        access = self.client.post(
            "/pilot/access", json={"participant_id": "P01", "access_code": "private-code-01"}
        ).json()
        self.headers = {"Authorization": f"Bearer {access['access_token']}"}
        session = self.client.post(
            "/pilot/consent",
            headers=self.headers,
            json={
                "consent_given": True,
                "consent_version": "pilot-consent-v1",
                "device_class": "mobile",
            },
        ).json()
        self.headers["X-Pilot-Session"] = session["id"]

    def tearDown(self) -> None:
        self.client.close()
        self.client.app.state.storage.close()
        self.directory.cleanup()

    def test_batch_interpret_correction_and_idempotent_confirmation(self) -> None:
        batch_response = self.client.post(
            "/pilot/interpret-batch",
            headers=self.headers,
            json={"text": "Vendí 3 panes a 50 centavos cada uno y gasté 4 en taxi"},
        )
        self.assertEqual(200, batch_response.status_code)
        batch = batch_response.json()
        self.assertEqual("READY", batch["status"])
        sale = batch["segments"][0]
        corrected_response = self.client.post(
            f"/pilot/batches/{batch['batch_id']}/items/{sale['segment_id']}/correct",
            headers=self.headers,
            json={"changes": {"quantity": 4}},
        )
        self.assertEqual(200, corrected_response.status_code)
        corrected_batch = corrected_response.json()["batch"]
        self.assertEqual(2, corrected_batch["segments"][0]["operation"]["total"])

        payload = {
            "item_ids": corrected_batch["confirmable_item_ids"],
            "idempotency_key": "stable-api-batch-key",
        }
        first = self.client.post(
            f"/pilot/batches/{batch['batch_id']}/confirm", headers=self.headers, json=payload
        )
        repeated = self.client.post(
            f"/pilot/batches/{batch['batch_id']}/confirm", headers=self.headers, json=payload
        )
        self.assertEqual(200, first.status_code)
        self.assertEqual(first.json(), repeated.json())
        self.assertEqual(2, len(first.json()["operations"]))

    def test_backend_rejects_nonconfirmable_item(self) -> None:
        batch = self.client.post(
            "/pilot/interpret-batch",
            headers=self.headers,
            json={"text": "María llevó algo y gasté 4 en taxi"},
        ).json()
        ambiguous = next(item for item in batch["segments"] if not item["confirmable"])
        response = self.client.post(
            f"/pilot/batches/{batch['batch_id']}/confirm",
            headers=self.headers,
            json={"item_ids": [ambiguous["segment_id"]], "idempotency_key": "unsafe-item-key"},
        )
        self.assertEqual(409, response.status_code)

    def test_batch_is_isolated_between_participants(self) -> None:
        batch = self.client.post(
            "/pilot/interpret-batch", headers=self.headers, json={"text": "Gasté 4 en taxi"}
        ).json()
        access = self.client.post(
            "/pilot/access", json={"participant_id": "P02", "access_code": "private-code-02"}
        ).json()
        p02_headers = {"Authorization": f"Bearer {access['access_token']}"}
        session = self.client.post(
            "/pilot/consent",
            headers=p02_headers,
            json={"consent_given": True, "consent_version": "pilot-consent-v1"},
        ).json()
        p02_headers["X-Pilot-Session"] = session["id"]
        response = self.client.post(
            f"/pilot/batches/{batch['batch_id']}/confirm",
            headers=p02_headers,
            json={"item_ids": batch["confirmable_item_ids"], "idempotency_key": "p02-cross-tenant"},
        )
        self.assertEqual(404, response.status_code)

    def test_batch_routes_are_absent_when_flag_is_off(self) -> None:
        second_directory = tempfile.TemporaryDirectory()
        try:
            app = create_app(
                Path(second_directory.name) / "disabled.db",
                pilot_access_codes={},
                pilot_mode=False,
                batch_experiment=False,
            )
            with TestClient(app) as client:
                self.assertEqual(
                    404,
                    client.post("/pilot/interpret-batch", json={"text": "Gasté 4"}).status_code,
                )
        finally:
            second_directory.cleanup()


if __name__ == "__main__":
    unittest.main()
