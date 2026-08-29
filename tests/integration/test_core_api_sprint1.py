import unittest
from datetime import timedelta

from mercadovoz_core import (
    Business,
    ContextSession,
    Expense,
    MercadoVozCore,
    Product,
    Sale,
)


class SprintOneCoreTests(unittest.TestCase):
    def test_minimal_domain_models_are_serializable(self):
        self.assertEqual("Negocio", Business("B-1", "Negocio").name)
        self.assertEqual("tomate", Product("P-1", "tomate", "libra").name)
        self.assertEqual(
            {"type": "EXPENSE", "category": "transporte", "amount": 4},
            Expense(category="transporte", amount=4).to_dict(),
        )
        self.assertEqual(6, Sale(product="tomate", quantity=2, unit="libra", unit_price=3, total=6).total)

    def test_context_v2_records_created_at_and_confidence(self):
        context = ContextSession()
        entry = context.set(
            "active_customer",
            "María",
            source="visible_selection",
            ttl=timedelta(minutes=5),
            confidence=1.0,
        )
        snapshot = entry.snapshot()
        self.assertEqual(snapshot["observed_at"], snapshot["created_at"])
        self.assertEqual(1.0, snapshot["confidence"])
        with self.assertRaises(ValueError):
            context.set("active_product", "papa", source="test", confidence=1.1)

    def test_internal_api_audits_versions_and_confirmation(self):
        core = MercadoVozCore()
        proposal = core.propose("Gasté cuatro en transporte")
        for field in (
            "original_text",
            "normalized_text",
            "parser_version",
            "engine_version",
            "schema_version",
            "context_version",
            "context_used",
            "safety_rules_triggered",
            "fields_extracted",
            "computed_fields",
            "warnings",
            "proposal",
            "confirmation",
            "corrections",
            "final_operation",
        ):
            self.assertIn(field, proposal)
        confirmed = core.confirm(proposal["proposal_id"], "api-confirm-1")
        self.assertEqual("CONFIRMED", confirmed["lifecycle_status"])

    def test_controlled_amount_product_and_customer_corrections(self):
        core = MercadoVozCore()
        expense = core.propose("Gasté diez en transporte")
        corrected_expense = core.correct(expense["proposal_id"], "eran doce dólares")
        self.assertEqual(12, corrected_expense["operation"]["amount"])

        sale = core.propose("Vendí dos libras de papa a tres dólares cada una")
        corrected_sale = core.correct(sale["proposal_id"], "era tomate")
        self.assertEqual("tomate", corrected_sale["operation"]["product"])

        context = ContextSession()
        context.set("active_customer", "María", source="visible_selection")
        payment = core.propose("Me pagó cinco", context)
        corrected_payment = core.correct(
            payment["proposal_id"], "no era María, era Rosa"
        )
        self.assertEqual("Rosa", corrected_payment["operation"]["customer"])


if __name__ == "__main__":
    unittest.main()
