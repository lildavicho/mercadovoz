from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mercadovoz_batch.interpreter import BatchInterpreter
from mercadovoz_batch.storage import BatchLedger
from mercadovoz_batch.versioning import ENGINE_VERSION
from mercadovoz_core.storage import SQLiteLedger


class BatchStorageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.ledger = SQLiteLedger(Path(self.directory.name) / "batch.db")
        self.store = BatchLedger(self.ledger)
        self.engine = BatchInterpreter()
        self.session = self.ledger.begin_pilot_session(
            participant_id="P01",
            consent_version="pilot-consent-v1",
            versions={
                "pilot_version": "pilot-v0",
                "engine_version": ENGINE_VERSION,
                "parser_version": "batch-v1+engine-1.1",
                "schema_version": "batch-operation-v1",
                "ui_version": "batch-ui-v1",
                "round_id": "SYNTHETIC_QA",
            },
        )

    def tearDown(self) -> None:
        self.ledger.close()
        self.directory.cleanup()

    def register(self, text: str):
        batch = self.engine.interpret(text)
        self.store.register(batch, participant_id="P01", session_id=self.session["id"])
        return batch

    def confirm(self, batch, key="stable-batch-key"):
        return self.store.confirm(
            batch,
            item_ids=batch["confirmable_item_ids"],
            idempotency_key=key,
            participant_id="P01",
            session_id=self.session["id"],
        )

    def test_migration_is_forward_only_and_legacy_schema_remains_readable(self) -> None:
        self.assertEqual(
            ["001_initial", "002_pilot_v0", "003_pilot_round_id", "004_batch_transaction_groups"],
            self.ledger.schema_versions(),
        )

    def test_batch_confirmation_is_atomic_and_durably_idempotent(self) -> None:
        batch = self.register("Gasté 4 en taxi y vendí 2 panes a 50 centavos cada uno")
        first = self.confirm(batch)
        repeated = self.confirm(batch)
        self.assertEqual(first, repeated)
        self.assertEqual(2, len(first["operations"]))
        self.assertEqual(2, len(self.ledger.list_operations(participant_id="P01")))

        reconstructed = BatchLedger(self.ledger)
        self.assertEqual(first, reconstructed.result_for_key("P01", "stable-batch-key"))

    def test_injected_second_write_failure_rolls_back_every_batch_write(self) -> None:
        batch = self.register("Gasté 4 en taxi y vendí 2 panes a 50 centavos cada uno")
        original_insert = self.store._insert_operation
        calls = 0

        def fail_on_second(*args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise RuntimeError("injected storage failure")
            return original_insert(*args, **kwargs)

        self.store._insert_operation = fail_on_second  # type: ignore[method-assign]
        with self.assertRaisesRegex(RuntimeError, "injected storage failure"):
            self.confirm(batch, "atomic-failure-key")
        self.assertEqual([], self.ledger.list_operations(participant_id="P01"))
        self.assertIsNone(self.store.result_for_key("P01", "atomic-failure-key"))
        confirmed_items = self.ledger._connection.execute(
            "SELECT COUNT(*) FROM batch_items WHERE lifecycle_status = 'CONFIRMED'"
        ).fetchone()[0]
        self.assertEqual(0, confirmed_items)

    def test_same_idempotency_key_cannot_confirm_different_selection(self) -> None:
        batch = self.register("Gasté 4 en taxi y vendí 2 panes a 50 centavos cada uno")
        self.confirm(batch)
        with self.assertRaisesRegex(ValueError, "different request"):
            self.store.confirm(
                batch,
                item_ids=[batch["confirmable_item_ids"][0]],
                idempotency_key="stable-batch-key",
                participant_id="P01",
                session_id=self.session["id"],
            )

    def test_partial_full_and_multiple_payments_preserve_history(self) -> None:
        debt = self.register("María quedó debiendo 12 dólares")
        self.confirm(debt, "create-debt-key")
        payment_one = self.register("María me pagó 5")
        self.confirm(payment_one, "first-payment-key")
        payment_two = self.register("María me pagó 7")
        self.confirm(payment_two, "second-payment-key")
        receivable = self.ledger.list_receivables("P01")[0]
        self.assertEqual(0, receivable["balance"])
        self.assertEqual("PAID", receivable["status"])
        movements = self.ledger._connection.execute(
            "SELECT movement_type, amount_minor FROM receivable_movements ORDER BY rowid"
        ).fetchall()
        self.assertEqual([("CREATED", 1200), ("PAYMENT", 500), ("PAYMENT", 700)], [tuple(row) for row in movements])

    def test_overpayment_is_blocked_without_changing_balance(self) -> None:
        debt = self.register("María quedó debiendo 5 dólares")
        self.confirm(debt, "create-small-debt")
        payment = self.register("María me pagó 8")
        with self.assertRaisesRegex(ValueError, "exceeds"):
            self.confirm(payment, "overpayment-key")
        self.assertEqual(5, self.ledger.list_receivables("P01")[0]["balance"])
        self.assertEqual(1, len(self.ledger.list_operations(participant_id="P01")))

    def test_multiple_open_debts_require_explicit_receivable(self) -> None:
        for index, amount in enumerate((5, 7), start=1):
            debt = self.register(f"María quedó debiendo {amount} dólares")
            self.confirm(debt, f"debt-key-{index}")
        payment = self.register("María me pagó 3")
        with self.assertRaisesRegex(ValueError, "explicit receivable"):
            self.confirm(payment, "ambiguous-payment")

    def test_payment_cannot_cross_customer_or_reopen_closed_debt(self) -> None:
        debt = self.register("María quedó debiendo 5 dólares")
        self.confirm(debt, "customer-debt")
        receivable_id = self.ledger.list_receivables("P01")[0]["id"]

        wrong_customer = self.register("Rosa me pagó 2")
        wrong_customer["segments"][0]["operation"]["receivable_id"] = receivable_id
        with self.assertRaisesRegex(ValueError, "customer does not match"):
            self.confirm(wrong_customer, "wrong-customer")

        payment = self.register("María me pagó 5")
        self.confirm(payment, "close-debt")
        after_close = self.register("María me pagó 1")
        with self.assertRaisesRegex(ValueError, "open receivable"):
            self.confirm(after_close, "closed-debt")

    def test_transaction_group_and_line_items_are_auditable(self) -> None:
        group_batch = self.register("María llevó 8 dólares de producto y dejó 5")
        group_result = self.confirm(group_batch, "settlement-group")
        self.assertEqual(3, len(group_result["operations"]))
        self.assertEqual(1, len(self.store.list_groups("P01")))

        sale = self.register("Vendí dos panes a 50 centavos cada uno y tres colas a un dólar cada una")
        self.confirm(sale, "line-item-sale")
        line_count = self.ledger._connection.execute("SELECT COUNT(*) FROM operation_line_items").fetchone()[0]
        self.assertEqual(2, line_count)


if __name__ == "__main__":
    unittest.main()
