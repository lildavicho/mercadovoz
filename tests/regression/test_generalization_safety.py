from __future__ import annotations

import math
import unittest
from decimal import Decimal

from mercadovoz_core import MercadoVozEngine, OperationWorkflow


SAFE_TERMINAL_STATUSES = {
    "COMPLETE", "NEEDS_CONFIRMATION", "NEEDS_CONTEXT", "AMBIGUOUS",
    "COMPOUND_OPERATION", "OUT_OF_SCOPE", "UNSAFE", "UNRECOGNIZED",
}
PRONOUNS = {"me", "te", "le", "lo", "la", "nos", "les", "se", "el", "ella"}


class AdversarialLanguageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = MercadoVozEngine()

    def test_negated_future_intended_and_hypothetical_events_abstain(self) -> None:
        phrases = (
            "Vendí 5 pero no vendí 5", "No gasté 10", "Pensé gastar 20",
            "Mañana venderé 5", "Quiero vender 3", "Si vendo 4 serían 8",
            "Voy a comprar 2 cajas", "Quería pagar 10",
        )
        for phrase in phrases:
            with self.subTest(phrase=phrase):
                result = self.engine.interpret(phrase)
                self.assertIn(result["status"], {"OUT_OF_SCOPE", "AMBIGUOUS", "UNRECOGNIZED"})
                self.assertIsNone(result["operation"])

    def test_non_financial_phrases_never_create_operations(self) -> None:
        for phrase in ("Está lloviendo", "Hola", "Qué caro está todo", "Mañana abro temprano", "Tengo hambre"):
            with self.subTest(phrase=phrase):
                self.assertIsNone(self.engine.interpret(phrase)["operation"])

    def test_multi_product_sale_abstains_while_schema_has_one_line(self) -> None:
        result = self.engine.interpret("Vendí dos chocolates y cuatro panes")
        self.assertEqual("COMPOUND_OPERATION", result["status"])
        self.assertIsNone(result["operation"])

    def test_noncomplete_interpretation_cannot_be_confirmed_even_if_shape_is_valid(self) -> None:
        interpretation = self.engine.interpret("Vendí dos libras de papa a tres dólares cada una")
        interpretation["status"] = "AMBIGUOUS"
        workflow = OperationWorkflow()
        proposal = workflow.propose(interpretation)
        with self.assertRaisesRegex(ValueError, "not confirmable"):
            workflow.confirm(proposal["proposal_id"], idempotency_key="must-not-save")


class DeterministicFuzzInvariantTests(unittest.TestCase):
    """Synthetic robustness matrix; it is not evidence of user accuracy."""

    def test_hundreds_of_generated_inputs_never_break_financial_invariants(self) -> None:
        engine = MercadoVozEngine()
        verbs = ("Vendí", "Se fueron", "Salieron")
        quantities = ("una", "dos", "3", "cuatro", "5")
        units = ("libra", "libras", "caja", "fundas", "unidad")
        products = ("tomate", "pan", "arroz", "leche")
        prices = ("1 dólar", "2 dólares", "50 centavos", "0,50 dólares")
        bases = ("cada una", "cada libra", "por unidad")
        checked = 0
        for verb in verbs:
            for quantity in quantities:
                for unit in units:
                    for product in products:
                        for price in prices:
                            for basis in bases:
                                phrase = f"{verb} {quantity} {unit} de {product} a {price} {basis}"
                                result = engine.interpret(phrase)
                                checked += 1
                                self.assertIn(result["status"], SAFE_TERMINAL_STATUSES)
                                operation = result["operation"]
                                if operation is None:
                                    continue
                                customer = str(operation.get("customer", "")).lower()
                                self.assertNotIn(customer, PRONOUNS)
                                for field in ("amount", "quantity", "unit_price", "total"):
                                    if operation.get(field) is None:
                                        continue
                                    number = Decimal(str(operation[field]))
                                    self.assertTrue(number.is_finite(), (phrase, field))
                                    self.assertGreater(number, 0, (phrase, field))
                                if operation.get("quantity") and operation.get("unit_price"):
                                    expected = Decimal(str(operation["quantity"])) * Decimal(str(operation["unit_price"]))
                                    self.assertEqual(expected, Decimal(str(operation["total"])), phrase)
        self.assertGreaterEqual(checked, 3000)


if __name__ == "__main__":
    unittest.main()
