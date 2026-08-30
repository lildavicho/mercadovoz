import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from mercadovoz_core.pilot_version import CONSENT_VERSION
from mercadovoz_core.service import create_app


class PilotReadinessTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.db = Path(self.tempdir.name) / "pilot.db"
        self.app = create_app(
            self.db,
            pilot_mode=True,
            pilot_access_codes={"P01": "pilot-code-p01", "P02": "pilot-code-p02"},
            operator_token="operator-test-token",
        )
        self.client = TestClient(self.app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.tempdir.cleanup()

    def access(self, participant="P01", code="pilot-code-p01"):
        response = self.client.post(
            "/pilot/access",
            json={"participant_id": participant, "access_code": code},
        )
        self.assertEqual(200, response.status_code, response.text)
        return response.json()["access_token"]

    def consent(self, token, device="mobile"):
        response = self.client.post(
            "/pilot/consent",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "consent_given": True,
                "consent_version": CONSENT_VERSION,
                "device_class": device,
            },
        )
        self.assertEqual(200, response.status_code, response.text)
        return response.json()["id"]

    def headers(self, token, session):
        return {
            "Authorization": f"Bearer {token}",
            "X-Pilot-Session": session,
        }

    def test_consent_is_required_before_participant_and_session_exist(self):
        token = self.access()
        rejected = self.client.post(
            "/pilot/consent",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "consent_given": False,
                "consent_version": CONSENT_VERSION,
                "device_class": "mobile",
            },
        )
        self.assertEqual(400, rejected.status_code)
        self.assertEqual(0, self.app.state.storage.counts()["participants"])

    def test_full_pilot_flow_captures_correction_and_is_idempotent(self):
        token = self.access()
        session = self.consent(token)
        headers = self.headers(token, session)
        proposed = self.client.post(
            "/pilot/interpret",
            headers=headers,
            json={"text": "Gasté cuatro en transporte"},
        ).json()
        self.assertEqual("PROPOSED", proposed["lifecycle_status"])
        corrected = self.client.post(
            f"/pilot/proposals/{proposed['proposal_id']}/correct",
            headers=headers,
            json={"text": "eran seis dólares"},
        ).json()
        self.assertEqual(6, corrected["operation"]["amount"])
        confirm_url = f"/pilot/proposals/{proposed['proposal_id']}/confirm"
        first = self.client.post(
            confirm_url,
            headers=headers,
            json={"idempotency_key": "stable-confirm-key"},
        )
        repeated = self.client.post(
            confirm_url,
            headers=headers,
            json={"idempotency_key": "stable-confirm-key"},
        )
        self.assertEqual(200, first.status_code)
        self.assertEqual(200, repeated.status_code)
        self.assertEqual(
            first.json()["persisted_operation"]["id"],
            repeated.json()["persisted_operation"]["id"],
        )
        self.assertEqual(1, len(self.client.get("/pilot/operations", headers=headers).json()))
        exported = self.app.state.storage.export_real_development("P01")
        self.assertEqual(1, len(exported))
        self.assertEqual("REAL_DEVELOPMENT", exported[0]["evidence_class"])
        self.assertEqual("USER_ACCEPTED_OPERATION", exported[0]["ground_truth_status"])
        self.assertEqual("Gasté cuatro en transporte", exported[0]["original_text"])
        self.assertEqual("amount", exported[0]["corrections"][0]["changes"][0]["field_changed"])
        metrics = self.app.state.storage.metrics("P01")
        self.assertEqual(1, metrics["total_inputs"])
        self.assertEqual(1.0, metrics["successful_registration_rate"])
        self.assertEqual(1.0, metrics["correction_rate"])

    def test_participant_isolation_for_sessions_history_and_audit(self):
        p01_token = self.access()
        p01_session = self.consent(p01_token)
        p01_headers = self.headers(p01_token, p01_session)
        proposal = self.client.post(
            "/pilot/interpret", headers=p01_headers,
            json={"text": "Ana me debe veinte"},
        ).json()
        confirmed = self.client.post(
            f"/pilot/proposals/{proposal['proposal_id']}/confirm",
            headers=p01_headers,
            json={"idempotency_key": "p01-debt-confirm"},
        ).json()
        operation_id = confirmed["persisted_operation"]["id"]

        p02_token = self.access("P02", "pilot-code-p02")
        p02_session = self.consent(p02_token)
        p02_headers = self.headers(p02_token, p02_session)
        self.assertEqual([], self.client.get("/pilot/operations", headers=p02_headers).json())
        self.assertEqual([], self.client.get("/pilot/receivables", headers=p02_headers).json())
        self.assertEqual(
            409,
            self.client.get(f"/pilot/operations/{operation_id}/audit", headers=p02_headers).status_code,
        )
        cross_session = self.client.get("/pilot/operations", headers={
            "Authorization": f"Bearer {p02_token}",
            "X-Pilot-Session": p01_session,
        })
        self.assertEqual(409, cross_session.status_code)

    def test_reject_cancel_feedback_end_and_deletion(self):
        token = self.access()
        session = self.consent(token)
        headers = self.headers(token, session)
        rejected_proposal = self.client.post(
            "/pilot/interpret", headers=headers,
            json={"text": "Gasté cuatro en transporte"},
        ).json()
        rejected = self.client.post(
            f"/pilot/proposals/{rejected_proposal['proposal_id']}/reject",
            headers=headers, json={"reason": "la propuesta no corresponde"},
        )
        self.assertEqual("REJECTED", rejected.json()["lifecycle_status"])
        cancelled_proposal = self.client.post(
            "/pilot/interpret", headers=headers,
            json={"text": "Vendí dos libras de tomate a tres dólares cada una"},
        ).json()
        cancelled = self.client.post(
            f"/pilot/proposals/{cancelled_proposal['proposal_id']}/cancel",
            headers=headers, json={"reason": "decidí no registrar"},
        )
        self.assertEqual("CANCELLED", cancelled.json()["lifecycle_status"])
        feedback = self.client.post(
            "/pilot/feedback", headers=headers,
            json={"annoying": "nada", "missing": "", "distrust": "", "faster": "sí"},
        )
        self.assertEqual(200, feedback.status_code)
        ended = self.client.post("/pilot/session/end", headers=headers)
        self.assertIsNotNone(ended.json()["ended_at"])
        self.assertEqual(409, self.client.get("/pilot/operations", headers=headers).status_code)
        deleted = self.app.state.storage.delete_participant("P01")
        self.assertEqual(1, deleted["sessions"])
        self.assertEqual(0, self.app.state.storage.counts()["participants"])

    def test_critical_financial_safety_and_annotation(self):
        token = self.access()
        session = self.consent(token)
        headers = self.headers(token, session)
        result = self.client.post(
            "/pilot/interpret", headers=headers,
            json={"text": "Hoy hice como cuarenta"},
        ).json()
        self.assertIsNone(result["operation"])
        self.assertEqual("AMBIGUOUS", result["status"])
        annotation = self.app.state.storage.annotate_input(
            input_id=result["input_id"], participant_id="P01",
            category="APPROXIMATION", critical_financial_error=False,
        )
        self.assertFalse(annotation["critical_financial_error"])
        self.assertEqual(0, self.app.state.storage.metrics("P01")["critical_financial_errors"])

    def test_nonconfirmable_proposal_is_rejected_by_api(self):
        token = self.access()
        session = self.consent(token)
        headers = self.headers(token, session)
        proposal = self.client.post(
            "/pilot/interpret", headers=headers,
            json={"text": "Me abonó cinco"},
        ).json()
        self.assertEqual("NEEDS_CONTEXT", proposal["interpretation_status"])
        response = self.client.post(
            f"/pilot/proposals/{proposal['proposal_id']}/confirm",
            headers=headers,
            json={"idempotency_key": "must-not-confirm-incomplete"},
        )
        self.assertEqual(409, response.status_code)
        self.assertIn("not confirmable", response.json()["detail"])
        self.assertEqual([], self.app.state.storage.list_operations(participant_id="P01"))

    def test_pilot_mode_hides_development_routes_and_docs(self):
        self.assertEqual(404, self.client.get("/docs").status_code)
        self.assertEqual(404, self.client.post("/interpret", json={"text": "hola"}).status_code)
        health = self.client.get("/health")
        self.assertEqual({"status": "ok", "database": "ok"}, health.json())
        self.assertEqual("nosniff", health.headers["x-content-type-options"])

    def test_confirmation_and_pilot_audit_roll_back_together(self):
        token = self.access()
        session = self.consent(token)
        headers = self.headers(token, session)
        proposal = self.client.post(
            "/pilot/interpret", headers=headers,
            json={"text": "Gasté cuatro en transporte"},
        ).json()
        storage = self.app.state.storage
        with patch.object(storage, "_insert_event", side_effect=RuntimeError("audit unavailable")):
            with self.assertRaises(RuntimeError):
                self.client.post(
                    f"/pilot/proposals/{proposal['proposal_id']}/confirm",
                    headers=headers,
                    json={"idempotency_key": "rollback-confirm-key"},
                )
        self.assertEqual([], storage.list_operations(participant_id="P01"))


if __name__ == "__main__":
    unittest.main()
