import unittest

from mercadovoz import apply_correction, parse_text
from mercadovoz.models import validate_operation


class ParserTests(unittest.TestCase):
    def test_complete_sale(self):
        result = parse_text("Vendí cinco libras de tomate a dos dólares cada una")
        self.assertEqual("COMPLETE", result["status"])
        self.assertEqual(
            {
                "type": "SALE",
                "product": "tomate",
                "quantity": 5,
                "unit": "libra",
                "unit_price": 2,
                "total": 10,
            },
            result["operation"],
        )

    def test_ambiguous_sale_requests_confirmation(self):
        result = parse_text("Vendí tomate")
        self.assertEqual("NEEDS_CONFIRMATION", result["status"])
        self.assertIn("quantity", result["missing_fields"])
        self.assertIn("total", result["missing_fields"])

    def test_unrelated_text_is_not_invented(self):
        result = parse_text("Hoy hace mucho frío")
        self.assertEqual("UNRECOGNIZED", result["status"])
        self.assertIsNone(result["operation"])

    def test_compound_operation_abstains(self):
        result = parse_text("Vendí dos libras de papa a uno y gasté tres en transporte")
        self.assertEqual("NEEDS_CONFIRMATION", result["status"])
        self.assertIn("compound_operation_out_of_scope", result["warnings"])

    def test_quantity_correction_recalculates_total(self):
        result = parse_text("Vendí cinco libras de tomate a dos dólares")
        corrected = apply_correction(result, "No, eran seis libras")
        self.assertEqual(6, corrected["operation"]["quantity"])
        self.assertEqual(12, corrected["operation"]["total"])

    def test_amount_correction(self):
        result = parse_text("Gasté diez dólares en transporte")
        corrected = apply_correction(result, "No, fueron once dólares")
        self.assertEqual(11, corrected["operation"]["amount"])

    def test_inconsistent_total_is_rejected(self):
        errors = validate_operation(
            {
                "type": "SALE",
                "product": "tomate",
                "quantity": 3,
                "unit": "caja",
                "unit_price": 14,
                "total": 41,
            }
        )
        self.assertIn("inconsistent_total", errors)

    def test_unknown_correction_preserves_pending_operation(self):
        result = parse_text("Vendí cinco cajas de tomate a doce")
        corrected = apply_correction(result, "Eso no está bien")
        self.assertEqual(result["operation"], corrected["operation"])
        self.assertEqual("NEEDS_CONFIRMATION", corrected["status"])
        self.assertIn("correction_not_understood", corrected["warnings"])


if __name__ == "__main__":
    unittest.main()
