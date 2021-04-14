import unittest

from elisio.syllable import Syllable


class TestSyllableWeight(unittest.TestCase):
    def test_syllw_heavy_isolated(self):
        self.assertTrue(Syllable('as').is_heavy())
        self.assertTrue(Syllable('ax').is_heavy())
        self.assertTrue(Syllable('ae').is_heavy())
        self.assertTrue(Syllable('ras').is_heavy())
        self.assertTrue(Syllable('dax').is_heavy())
        self.assertTrue(Syllable('tae').is_heavy())
        self.assertFalse(Syllable('u').is_heavy())
        self.assertFalse(Syllable('o').is_heavy())
        self.assertFalse(Syllable('i').is_heavy())
        self.assertFalse(Syllable('e').is_heavy())
        self.assertFalse(Syllable('a').is_heavy())

    def test_syllw_light_isolated(self):
        self.assertFalse(Syllable('e').is_light())
        self.assertFalse(Syllable('i').is_light())
        self.assertFalse(Syllable('a').is_light())

    def test_syllw_light_syntax(self):
        self.assertTrue(Syllable('re').is_light(Syllable('ac')))
        self.assertTrue(Syllable('rae').is_light(Syllable('ac')))
        self.assertFalse(Syllable('re').is_light(Syllable('dac')))
        self.assertFalse(Syllable('rec').is_light(Syllable('ac')))
        self.assertFalse(Syllable('rec').is_light(Syllable('tac')))

    def test_syllw_heavy_syntax(self):
        self.assertTrue(Syllable('re').is_heavy(Syllable('xac')))
        self.assertTrue(Syllable('res').is_heavy(Syllable('sac')))
        self.assertTrue(Syllable('rae').is_heavy(Syllable('bac')))
        self.assertFalse(Syllable('re').is_heavy(Syllable('prac')))
