from __future__ import annotations

import unittest

from mercadovoz_batch.interpreter import BatchInterpreter


class BatchInterpreterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = BatchInterpreter()

    def test_partial_success_keeps_safe_items(self) -> None:
        result = self.engine.interpret(
            "Vendí 3 panes a 50 centavos cada uno, María llevó algo y gasté 4 en taxi."
        )
        self.assertEqual("PARTIALLY_READY", result["status"])
        self.assertEqual(3, len(result["segments"]))
        self.assertEqual([True, False, True], [item["confirmable"] for item in result["segments"]])
        self.assertEqual(["SALE", None, "EXPENSE"], [
            item.get("operation", {}).get("type") if item.get("operation") else None
            for item in result["segments"]
        ])

    def test_explicit_new_debt_keeps_customer_and_amount(self) -> None:
        result = self.engine.interpret("María quedó debiendo 12 dólares")
        item = result["segments"][0]
        self.assertEqual("COMPLETE", item["state"])
        self.assertEqual({"type": "RECEIVABLE", "customer": "María", "amount": 12}, item["operation"])

    def test_explicit_sale_total_does_not_require_or_invent_unit_price(self) -> None:
        result = self.engine.interpret("Vendí 5 naranjas por 3 dólares en total")
        operation = result["segments"][0]["operation"]
        self.assertEqual("COMPLETE", result["segments"][0]["state"])
        self.assertEqual(3, operation["total"])
        self.assertIsNone(operation["unit_price"])
        self.assertEqual("EXPLICIT", result["segments"][0]["field_provenance"]["total"]["source"])

    def test_line_items_are_one_sale_with_derived_total(self) -> None:
        result = self.engine.interpret(
            "Vendí dos panes a 50 centavos cada uno y tres colas a un dólar cada una"
        )
        item = result["segments"][0]
        self.assertEqual("COMPLETE", item["state"])
        self.assertEqual(2, len(item["operation"]["line_items"]))
        self.assertEqual(4, item["operation"]["total"])
        self.assertTrue(item["field_provenance"]["total"]["derived"])

    def test_sale_settlement_creates_auditable_group(self) -> None:
        result = self.engine.interpret("María llevó 8 dólares de producto y dejó 5")
        self.assertEqual("READY", result["status"])
        self.assertEqual(1, len(result["groups"]))
        group = result["groups"][0]
        self.assertEqual("SALE_SETTLEMENT", group["type"])
        self.assertEqual("María", group["customer"])
        operations = [item["operation"] for item in result["segments"]]
        self.assertEqual(["SALE", "PAYMENT_RECEIVED", "RECEIVABLE"], [item["type"] for item in operations])
        self.assertEqual(3, operations[2]["amount"])
        self.assertTrue(result["segments"][2]["field_provenance"]["amount"]["derived"])

    def test_adversarial_correction_is_not_promoted(self) -> None:
        result = self.engine.interpret("Vendí 5 y no, mentira, fueron 4")
        self.assertFalse(any(item["confirmable"] for item in result["segments"]))
        self.assertEqual("BLOCKED", result["status"])

    def test_empty_and_oversized_inputs_fail_closed(self) -> None:
        self.assertEqual("BLOCKED", self.engine.interpret("   ")["status"])
        self.assertEqual("BLOCKED", self.engine.interpret("a" * 2001)["status"])


if __name__ == "__main__":
    unittest.main()
