import unittest

from mercadovoz_core import MercadoVozEngine


class SafetyRegressionTests(unittest.TestCase):
    def setUp(self):
        self.engine = MercadoVozEngine()

    def test_numeric_coordination_is_not_collapsed_to_six(self):
        result = self.engine.interpret("Vendí cinco libras de papa y una quedó fiada")
        self.assertEqual("COMPOUND_OPERATION", result["status"])
        self.assertIsNone(result["operation"])
        self.assertNotEqual(6, result["fields_extracted"].get("quantity"))

    def test_income_and_expense_are_not_reduced_to_one_operation(self):
        result = self.engine.interpret("Me entraron treinta y gasté ocho en transporte")
        self.assertEqual("COMPOUND_OPERATION", result["status"])
        self.assertIsNone(result["operation"])

    def test_personal_withdrawal_is_not_stock(self):
        result = self.engine.interpret("Saqué cinco para la casa")
        self.assertEqual("OUT_OF_SCOPE", result["status"])
        self.assertIsNone(result["operation"])
        self.assertIn("owner_withdrawal_schema_gap", result["warnings"])
        variant = self.engine.interpret("Saqué cinco dólares para una cosa de la casa")
        self.assertEqual("OUT_OF_SCOPE", variant["status"])
        self.assertIsNone(variant["operation"])

    def test_implicit_sale_and_payment_compound_is_split(self):
        for phrase in (
            "Ana llevó ocho y pagó cinco nomás",
            "Ana llevó ocho y dejó cinco",
        ):
            with self.subTest(phrase=phrase):
                result = self.engine.interpret(phrase)
                self.assertEqual("COMPOUND_OPERATION", result["status"])
                self.assertIsNone(result["operation"])

    def test_existing_debt_state_does_not_create_receivable(self):
        result = self.engine.interpret("Ana todavía me debe lo de ayer")
        self.assertEqual("NEEDS_CONTEXT", result["status"])
        self.assertIsNone(result["operation"])
        self.assertIn("existing_receivable_state_not_event", result["warnings"])

    def test_approximate_amount_is_not_made_exact(self):
        result = self.engine.interpret("Gasté como diez dólares en transporte")
        self.assertEqual("AMBIGUOUS", result["status"])
        self.assertIsNone(result["operation"])

    def test_meal_expense_requires_business_scope_confirmation(self):
        result = self.engine.interpret("Gasté cuatro en el almuerzo")
        self.assertEqual("AMBIGUOUS", result["status"])
        self.assertIsNone(result["operation"])
        self.assertIn("personal_or_business_expense_ambiguous", result["warnings"])

    def test_price_basis_requires_explicit_unit_or_total(self):
        result = self.engine.interpret("Vendí cinco libras de tomate a dos dólares")
        self.assertEqual("AMBIGUOUS", result["status"])
        self.assertIsNone(result["operation"])
        explicit = self.engine.interpret("Vendí cinco libras de tomate a dos dólares cada una")
        self.assertEqual("COMPLETE", explicit["status"])
        self.assertEqual(10, explicit["operation"]["total"])


if __name__ == "__main__":
    unittest.main()
