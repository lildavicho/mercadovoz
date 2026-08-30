from __future__ import annotations

import random
import unittest

from mercadovoz_batch.interpreter import BatchInterpreter


class BatchFuzzInvariantTests(unittest.TestCase):
    def test_thousands_of_adversarial_batches_fail_closed_without_crashing(self) -> None:
        randomizer = random.Random(12012026)
        engine = BatchInterpreter()
        subjects = ("María", "Rosa", "el vecino", "yo", "nadie")
        predicates = (
            "vendí 5 panes a 2 dólares cada uno",
            "quizá venda 13 panes mañana",
            "no gasté 15 dólares",
            "me quedan 50 dólares",
            "pagó aproximadamente 60",
            "gasté 5.50 en taxi",
            "vendí 2 cosas por 12 o 50 dólares",
            "anota lo de ayer",
        )
        connectors = ("; ", ". ", " y ", ", luego ", "\n")
        for _ in range(2_000):
            count = randomizer.choice((1, 2, 5, 10, 20))
            clauses = [f"{randomizer.choice(subjects)} {randomizer.choice(predicates)}" for _ in range(count)]
            text = randomizer.choice(connectors).join(clauses)
            result = engine.interpret(text)
            self.assertLessEqual(len(result["segments"]), 20)
            for item in result["segments"]:
                span = item["source_span"]
                self.assertEqual(text[span["start"]:span["end"]], item["source_text"])
                if item["confirmable"]:
                    operation = item["operation"]
                    self.assertIn(operation["type"], {"SALE", "EXPENSE", "RECEIVABLE", "PAYMENT_RECEIVED"})
                    monetary = operation.get("total", operation.get("amount"))
                    self.assertIsNotNone(monetary)
                    self.assertGreater(monetary, 0)


if __name__ == "__main__":
    unittest.main()
