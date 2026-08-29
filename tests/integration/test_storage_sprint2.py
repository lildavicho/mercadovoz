import tempfile
import unittest
from pathlib import Path

from mercadovoz_core import MercadoVozCore
from mercadovoz_core.storage import SQLiteLedger


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.storage = SQLiteLedger(Path(self.tempdir.name) / "test.db")
        self.core = MercadoVozCore(storage=self.storage)

    def tearDown(self):
        self.storage.close()
        self.tempdir.cleanup()

    def confirm(self, text: str, key: str):
        proposal = self.core.propose(text)
        return self.core.confirm(proposal["proposal_id"], key)

    def test_confirmed_operation_is_saved_once(self):
        first = self.confirm("Gasté cuatro en transporte", "expense-1")
        repeated = self.core.confirm(first["proposal_id"], "expense-1")
        self.assertEqual(
            first["persisted_operation"]["id"], repeated["persisted_operation"]["id"]
        )
        self.assertEqual(1, len(self.core.history()))

    def test_receivable_balance_changes_after_payment(self):
        self.confirm("Ana me debe veinte", "debt-1")
        self.confirm("Ana me pagó cinco", "payment-1")
        receivable = self.core.receivables()[0]
        self.assertEqual(15, receivable["balance"])
        self.assertEqual("OPEN", receivable["status"])


if __name__ == "__main__":
    unittest.main()
