import unittest
from elisio.util.numerals import roman_to_int, int_to_roman


class TestNumerals(unittest.TestCase):
    def test_basic_itr(self):
        self.assertEqual(int_to_roman(12), "XII")

    def test_basic_higher_itr(self):
        self.assertEqual(int_to_roman(127), "CXXVII")

    def test_zero_itr(self):
        with self.assertRaises(ValueError):
            int_to_roman(0)

    def test_invalid_type_str_itr(self):
        with self.assertRaises(TypeError):
            int_to_roman("abc")

    def test_invalid_type_float_itr(self):
        with self.assertRaises(TypeError):
            int_to_roman(320.5)

    def test_out_of_range_itr(self):
        with self.assertRaises(ValueError):
            int_to_roman(4000)

    def test_basic_rti(self):
        self.assertEqual(roman_to_int("XII"), 12)

    def test_basic_higher_rti(self):
        self.assertEqual(roman_to_int("CXXVII"), 127)

    def test_invalid_rti(self):
        with self.assertRaises(ValueError):
            roman_to_int("abc")

    def test_invalid_type_rti(self):
        with self.assertRaises(TypeError):
            roman_to_int(0)

    def test_out_of_range_rti(self):
        with self.assertRaises(ValueError):
            roman_to_int("MMMM")
