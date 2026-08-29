import unittest

from mercadovoz_core import MercadoVozEngine, OperationWorkflow


class ConfirmationWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.engine = MercadoVozEngine()
        self.workflow = OperationWorkflow()
        interpretation = self.engine.interpret(
            "Vendí cinco libras de tomate a dos dólares cada una"
        )
        self.proposal = self.workflow.propose(interpretation)

    def test_operation_stays_proposed_until_explicit_confirmation(self):
        self.assertEqual("PROPOSED", self.proposal["lifecycle_status"])
        self.assertIsNone(self.proposal["final_operation"])
        confirmed = self.workflow.confirm(
            self.proposal["proposal_id"], idempotency_key="confirm-001"
        )
        self.assertEqual("CONFIRMED", confirmed["lifecycle_status"])
        self.assertEqual(confirmed["operation"], confirmed["final_operation"])

    def test_confirmation_is_idempotent_and_does_not_duplicate(self):
        first = self.workflow.confirm(
            self.proposal["proposal_id"], idempotency_key="same-key"
        )
        second = self.workflow.confirm(
            self.proposal["proposal_id"], idempotency_key="same-key"
        )
        self.assertEqual(first, second)
        self.assertEqual(
            1,
            sum(event["action"] == "CONFIRMED" for event in second["audit_events"]),
        )
        with self.assertRaises(ValueError):
            self.workflow.confirm(
                self.proposal["proposal_id"], idempotency_key="different-key"
            )

    def test_correction_recalculates_and_requires_confirmation_again(self):
        corrected = self.workflow.correct(self.proposal["proposal_id"], "No, eran seis")
        self.assertEqual("CORRECTED", corrected["lifecycle_status"])
        self.assertEqual(6, corrected["operation"]["quantity"])
        self.assertEqual(12, corrected["operation"]["total"])
        self.assertIn("6", corrected["question"])
        self.assertIn("12", corrected["question"])
        self.assertIsNone(corrected["final_operation"])
        confirmed = self.workflow.confirm(
            self.proposal["proposal_id"], idempotency_key="corrected-confirm"
        )
        self.assertEqual(6, confirmed["final_operation"]["quantity"])

    def test_rejected_or_cancelled_proposal_is_terminal(self):
        rejected = self.workflow.reject(self.proposal["proposal_id"], reason="usuario dijo no")
        self.assertEqual("REJECTED", rejected["lifecycle_status"])
        with self.assertRaises(ValueError):
            self.workflow.correct(self.proposal["proposal_id"], "eran seis")

        second = self.workflow.propose(
            self.engine.interpret("Gasté diez dólares en transporte")
        )
        cancelled = self.workflow.cancel(second["proposal_id"], reason="sesión cerrada")
        self.assertEqual("CANCELLED", cancelled["lifecycle_status"])
        with self.assertRaises(ValueError):
            self.workflow.confirm(second["proposal_id"], idempotency_key="late")


if __name__ == "__main__":
    unittest.main()
