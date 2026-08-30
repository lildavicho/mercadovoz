from __future__ import annotations

import unittest

from mercadovoz_batch.segmenter import CommercialNarrativeSegmenter


class CommercialNarrativeSegmenterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.segmenter = CommercialNarrativeSegmenter()

    def assert_spans_round_trip(self, text: str) -> None:
        for segment in self.segmenter.segment(text):
            self.assertEqual(segment.text, text[segment.start : segment.end])

    def test_splits_distinct_operations_without_splitting_product_list(self) -> None:
        text = "Vendí dos tomates y cuatro lechugas, y gasté cinco en transporte."
        segments = self.segmenter.segment(text)
        self.assertEqual(2, len(segments))
        self.assertIn("cuatro lechugas", segments[0].text)
        self.assertTrue(segments[1].text.lower().startswith("gasté"))
        self.assert_spans_round_trip(text)

    def test_keeps_sale_settlement_group_together(self) -> None:
        text = "María llevó 8 dólares de producto y dejó 5. Después gasté 2."
        segments = self.segmenter.segment(text)
        self.assertEqual(2, len(segments))
        self.assertIn("dejó 5", segments[0].text)
        self.assertTrue(segments[1].text.lower().startswith("gasté"))
        self.assert_spans_round_trip(text)

    def test_preserves_order_across_newlines_semicolons_and_connectors(self) -> None:
        text = "A Rosa le fié 6; Juan pagó 3\nLuego vendí pan a un dólar cada uno."
        segments = self.segmenter.segment(text)
        self.assertEqual([1, 2, 3], [item.sequence for item in segments])
        self.assert_spans_round_trip(text)

    def test_limits_are_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "maximum input length"):
            self.segmenter.segment("x" * 2001)

    def test_accented_pague_starts_a_new_financial_clause(self) -> None:
        text = "Vendí cuatro jugos a uno cada uno. Pagué dos en hielo."
        segments = self.segmenter.segment(text)
        self.assertEqual(2, len(segments))
        self.assertEqual("Pagué dos en hielo", segments[1].text)
        self.assert_spans_round_trip(text)


if __name__ == "__main__":
    unittest.main()
