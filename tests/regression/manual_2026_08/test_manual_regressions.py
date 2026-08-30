from __future__ import annotations

import unittest

from mercadovoz_core import MercadoVozEngine


class ManualRegressionDevelopmentTests(unittest.TestCase):
    """Independent development evidence; never REAL_HELDOUT or field accuracy."""

    def setUp(self) -> None:
        self.engine = MercadoVozEngine()

    def assert_operation(
        self,
        text: str,
        *,
        status: str,
        operation_type: str | None,
        fields: dict[str, object] | None = None,
        forbidden_fields: tuple[str, ...] = (),
        forbidden_product_fragments: tuple[str, ...] = (),
    ) -> dict[str, object]:
        result = self.engine.interpret(text)
        self.assertEqual(result["status"], status, text)
        operation = result["operation"]
        if operation_type is None:
            self.assertIsNone(operation, text)
            return result
        self.assertIsNotNone(operation, text)
        self.assertEqual(operation["type"], operation_type, text)
        for field, expected in (fields or {}).items():
            self.assertEqual(operation.get(field), expected, f"{text}: {field}")
        for field in forbidden_fields:
            self.assertNotIn(field, operation, f"{text}: {field}")
        product = str(operation.get("product", "")).lower()
        for fragment in forbidden_product_fragments:
            self.assertNotIn(fragment, product, text)
        return result

    def test_sale_separates_product_from_explicit_unit_price(self) -> None:
        self.assert_operation(
            "Vendí 3 libras de tomate a 2 dólares cada libra",
            status="COMPLETE",
            operation_type="SALE",
            fields={
                "product": "tomate",
                "quantity": 3,
                "unit": "libra",
                "unit_price": 2,
                "total": 6,
            },
            forbidden_product_fragments=("a 2", "cada libra"),
        )

    def test_sale_normalizes_centavos_as_unit_price(self) -> None:
        self.assert_operation(
            "Vendí 4 panes a 50 centavos cada uno",
            status="COMPLETE",
            operation_type="SALE",
            fields={
                "product": "panes",
                "quantity": 4,
                "unit": "unidad",
                "unit_price": 0.5,
                "total": 2,
            },
            forbidden_product_fragments=("50 centavos", "cada uno"),
        )

    def test_sale_preserves_explicit_total_without_inventing_unit_price(self) -> None:
        self.assert_operation(
            "Vendí 5 naranjas por 3 dólares en total",
            status="COMPLETE",
            operation_type="SALE",
            fields={"product": "naranjas", "quantity": 5, "unit": "unidad", "total": 3, "unit_price": None},
            forbidden_product_fragments=("por 3", "en total"),
        )

    def test_payment_pronoun_is_not_a_customer(self) -> None:
        result = self.assert_operation(
            "Me abonó cinco",
            status="NEEDS_CONTEXT",
            operation_type="PAYMENT_RECEIVED",
            fields={"amount": 5},
            forbidden_fields=("customer",),
        )
        self.assertIn("customer", result["missing_fields"])

    def test_repeated_sale_predicate_is_compound(self) -> None:
        result = self.assert_operation(
            "Vendí dos chocolates a 1 dólar cada uno y también vendí 4 lechugas a 50 centavos cada una",
            status="COMPOUND_OPERATION",
            operation_type=None,
        )
        self.assertIn("compound_operation_requires_split", result["warnings"])


if __name__ == "__main__":
    unittest.main()
