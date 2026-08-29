import unittest

from mercadovoz.numbers import replace_number_words, to_decimal


class NumberTests(unittest.TestCase):
    def test_compound_spanish_number(self):
        self.assertEqual("31 libras", replace_number_words("treinta y una libras"))

    def test_decimal_comma(self):
        self.assertEqual(2.5, float(to_decimal("2,50")))


if __name__ == "__main__":
    unittest.main()
