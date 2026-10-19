import unittest

from converter import Converter


class TestConverter(unittest.TestCase):
    def test_values_at_or_above_positive_threshold_return_1000(self):
        for value in (100.7, 100.8, 150.0):
            with self.subTest(value=value):
                self.assertEqual(Converter.do(value), 1000)

    def test_positive_values_below_threshold_are_truncated(self):
        cases = ((0.1, 0), (1.9, 1), (65.7, 65), (100.6, 100))
        for value, expected in cases:
            with self.subTest(value=value):
                self.assertEqual(Converter.do(value), expected)

    def test_zero_raises_value_error(self):
        with self.assertRaises(ValueError):
            Converter.do(0.0)

    def test_negative_values_from_minus_30_4_to_zero_are_truncated_then_decreased(self):
        cases = ((-0.1, -5), (-1.9, -6), (-30.3, -35), (-30.4, -35))
        for value, expected in cases:
            with self.subTest(value=value):
                self.assertEqual(Converter.do(value), expected)

    def test_values_at_or_below_negative_threshold_return_minus_2000(self):
        for value in (-30.5, -30.6, -94.5):
            with self.subTest(value=value):
                self.assertEqual(Converter.do(value), -2000)


if __name__ == "__main__":
    unittest.main()
