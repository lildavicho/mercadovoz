import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from mercadovoz_core.service import create_app


class ServiceIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.client = TestClient(create_app(Path(self.tempdir.name) / "api.db"))
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.tempdir.cleanup()

    def test_text_flow_interpret_propose_confirm_and_history(self):
        interpretation = self.client.post(
            "/interpret", json={"text": "Gasté cuatro en transporte"}
        )
        self.assertEqual(200, interpretation.status_code)
        self.assertEqual("PROPOSED", interpretation.json()["lifecycle_status"])

        proposal = self.client.post(
            "/proposals", json={"text": "Gasté cuatro en transporte"}
        ).json()
        confirmed = self.client.post(
            f"/proposals/{proposal['proposal_id']}/confirm",
            json={"idempotency_key": "service-confirm-1"},
        )
        self.assertEqual(200, confirmed.status_code)
        self.assertEqual("CONFIRMED", confirmed.json()["lifecycle_status"])
        history = self.client.get("/operations").json()
        self.assertEqual(1, len(history))

    def test_unsafe_text_returns_no_operation(self):
        result = self.client.post(
            "/interpret", json={"text": "Hoy hice como cuarenta"}
        ).json()
        self.assertEqual("AMBIGUOUS", result["status"])
        self.assertIsNone(result["operation"])


if __name__ == "__main__":
    unittest.main()
