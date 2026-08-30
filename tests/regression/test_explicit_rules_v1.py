import unittest

from mercadovoz_core import MercadoVozEngine


class ExplicitRulesTests(unittest.TestCase):
    def setUp(self):
        self.engine = MercadoVozEngine()

    def assert_sale(self, phrase, product, quantity, unit, price):
        result = self.engine.interpret(phrase)
        self.assertEqual("COMPLETE", result["status"])
        self.assertEqual(
            {
                "type": "SALE",
                "product": product,
                "quantity": quantity,
                "unit": unit,
                "unit_price": price,
                "total": quantity * price,
            },
            result["operation"],
        )

    def test_explicit_sale_variants_share_one_grammar(self):
        examples = (
            ("Se fueron dos libras de tomate a tres la libra", "tomate", 2, "libra", 3),
            ("Di cuatro unidades de aguacate por cinco cada uno", "aguacate", 4, "unidad", 5),
            ("Dos pares de zapatos a ocho cada uno", "zapatos", 2, "par", 8),
            ("Tres vasos de jugo a uno cada uno", "jugo", 3, "vaso", 1),
        )
        for values in examples:
            with self.subTest(phrase=values[0]):
                self.assert_sale(*values)

    def test_malformed_generated_plural_is_not_added_as_vocabulary(self):
        result = self.engine.interpret("Dos unidads de tomate a tres cada una")
        self.assertEqual("UNRECOGNIZED", result["status"])

    def test_logistics_expense(self):
        result = self.engine.interpret("Pagué cuatro por traer la mercadería")
        self.assertEqual("COMPLETE", result["status"])
        self.assertEqual(
            {"type": "EXPENSE", "amount": 4, "category": "logistica"},
            result["operation"],
        )

    def test_new_receivable_extracts_named_customer_family(self):
        cases = {
            "María quedó debiendo 12 dólares": ("María", 12),
            "Rosa quedó debiendo 8": ("Rosa", 8),
            "Carlos me quedó debiendo diez": ("Carlos", 10),
            "Juan quedó debiendo 5 dólares": ("Juan", 5),
            "Ana quedó debiendo quince": ("Ana", 15),
        }
        for phrase, (customer, amount) in cases.items():
            with self.subTest(phrase=phrase):
                result = self.engine.interpret(phrase)
                self.assertEqual("COMPLETE", result["status"])
                self.assertEqual(
                    {"type": "RECEIVABLE", "customer": customer, "amount": amount},
                    result["operation"],
                )

    def test_explicit_sale_total_is_complete_without_invented_unit_price(self):
        result = self.engine.interpret("Vendí 5 naranjas por 3 dólares en total")
        self.assertEqual("COMPLETE", result["status"])
        self.assertEqual(3, result["operation"]["total"])
        self.assertIsNone(result["operation"]["unit_price"])
        self.assertNotIn("unit_price", result["missing_fields"])
        self.assertIn("explicit_total_without_unit_price", result["warnings"])

    def test_price_without_unit_basis_remains_ambiguous(self):
        result = self.engine.interpret("Vendí cinco libras de tomate a dos")
        self.assertEqual("AMBIGUOUS", result["status"])
        self.assertIsNone(result["operation"])

    def test_implicit_sale_verb_keeps_safe_fields_but_not_price_basis(self):
        result = self.engine.interpret("Salieron cuatro libras de tomate a ocho")
        self.assertEqual("NEEDS_CONFIRMATION", result["status"])
        self.assertEqual(
            {"type": "SALE", "product": "tomate", "quantity": 4, "unit": "libra"},
            result["operation"],
        )
        self.assertNotIn("unit_price", result["operation"])
        self.assertIn("price_basis_ambiguous", result["warnings"])


if __name__ == "__main__":
    unittest.main()
