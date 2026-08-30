from __future__ import annotations

import unittest

from mercadovoz_core import MercadoVozCore


class CorrectionGeneralizationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.core = MercadoVozCore()

    def test_negated_quantity_replacement_uses_new_value_only(self) -> None:
        proposal = self.core.propose("Vendí cinco libras de tomate a dos dólares cada una")
        corrected = self.core.correct(proposal["proposal_id"], "no eran 5 eran 6")
        self.assertEqual(6, corrected["operation"]["quantity"])
        self.assertEqual(12, corrected["operation"]["total"])

    def test_centavos_correction_updates_unit_price_and_total(self) -> None:
        proposal = self.core.propose("Vendí cuatro panes a dos dólares cada uno")
        corrected = self.core.correct(proposal["proposal_id"], "eran 50 centavos")
        self.assertEqual(0.5, corrected["operation"]["unit_price"])
        self.assertEqual(2, corrected["operation"]["total"])

    def test_explicit_total_correction_is_not_overwritten(self) -> None:
        proposal = self.core.propose("Vendí cuatro panes a dos dólares cada uno")
        corrected = self.core.correct(proposal["proposal_id"], "el total era 12")
        self.assertEqual(12, corrected["operation"]["total"])
        self.assertEqual("NEEDS_CONFIRMATION", corrected["interpretation_status"])
        with self.assertRaises(ValueError):
            self.core.confirm(proposal["proposal_id"], "inconsistent-total")


if __name__ == "__main__":
    unittest.main()
