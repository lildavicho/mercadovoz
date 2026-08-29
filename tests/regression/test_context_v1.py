import unittest
from datetime import datetime, timedelta, timezone

from mercadovoz_core import ContextSession, MercadoVozEngine


class ContextLayerTests(unittest.TestCase):
    def setUp(self):
        self.engine = MercadoVozEngine()
        self.now = datetime(2026, 8, 29, 12, 0, tzinfo=timezone.utc)

    def test_context_requires_supported_key_source_and_expiry(self):
        context = ContextSession()
        with self.assertRaises(KeyError):
            context.set("secret_customer", "Ana", source="selection")
        with self.assertRaises(ValueError):
            context.set("active_customer", "Ana", source="")
        with self.assertRaises(ValueError):
            context.set("active_customer", "Ana", source="selection", ttl=timedelta(0))

    def test_context_expires_and_can_be_invalidated(self):
        context = ContextSession()
        context.set(
            "active_customer",
            "Ana",
            source="user_selection",
            observed_at=self.now,
            ttl=timedelta(minutes=5),
        )
        self.assertIsNotNone(context.get("active_customer", now=self.now + timedelta(minutes=4)))
        self.assertIsNone(context.get("active_customer", now=self.now + timedelta(minutes=5)))
        context.set("active_product", "tomate", source="user_selection")
        context.invalidate("active_product")
        self.assertIsNone(context.get("active_product"))

    def test_payment_uses_explicit_receivable_context_and_computes_balance(self):
        context = ContextSession()
        context.set(
            "active_receivable",
            {"receivable_id": "R-17", "customer": "Ana", "balance": 25},
            source="user_selected_receivable",
        )
        result = self.engine.interpret("Me pagó diez", context)
        self.assertEqual("COMPLETE", result["status"])
        self.assertEqual(
            {"type": "PAYMENT_RECEIVED", "customer": "Ana", "amount": 10},
            result["operation"],
        )
        self.assertEqual(15, result["computed_fields"]["remaining_balance"])
        self.assertEqual("R-17", result["computed_fields"]["receivable_id"])
        self.assertEqual("active_receivable", result["context_used"][0]["key"])
        self.assertEqual("user_selected_receivable", result["context_used"][0]["source"])

    def test_missing_customer_is_reported_as_context_gap(self):
        result = self.engine.interpret("Me pagó diez")
        self.assertEqual("NEEDS_CONTEXT", result["status"])
        self.assertIn("customer", result["missing_fields"])


if __name__ == "__main__":
    unittest.main()
