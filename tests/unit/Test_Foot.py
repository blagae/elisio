import unittest

from elisio.exceptions import IllegalFootException
from elisio.parser.verse import Foot
from elisio.syllable import Weight


class TestFoot(unittest.TestCase):
    def test_unknown_struc_fails(self):
        with self.assertRaises(IllegalFootException):
            Foot.UNKNOWN.get_structure()

    def test_unknown_len_fails(self):
        with self.assertRaises(IllegalFootException):
            len(Foot.UNKNOWN)

    def test_dactylus(self):
        foot = Foot.DACTYLUS
        self.assertEqual(len(foot), 3)
        self.assertEqual(foot.get_structure(), [Weight.HEAVY, Weight.LIGHT, Weight.LIGHT])

    def test_spondaeus(self):
        foot = Foot.SPONDAEUS
        self.assertEqual(len(foot), 2)
        self.assertEqual(foot.get_structure(), [Weight.HEAVY, Weight.HEAVY])

    def test_trochaeus(self):
        foot = Foot.TROCHAEUS
        self.assertEqual(len(foot), 2)
        self.assertEqual(foot.get_structure(), [Weight.HEAVY, Weight.LIGHT])
