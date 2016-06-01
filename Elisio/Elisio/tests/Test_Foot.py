import unittest
from Elisio.engine.Verse import Foot
from Elisio.engine.Syllable import Weight
from Elisio.exceptions import IllegalFootException

class TestFoot(unittest.TestCase):
    def test_unknown_struc_fails(self):
        with self.assertRaises(IllegalFootException):
            Foot.UNKNOWN.get_structure()

    def test_unknown_len_fails(self):
        with self.assertRaises(IllegalFootException):
            Foot.UNKNOWN.get_length()
            
    def test_dactylus(self):
        foot = Foot.DACTYLUS
        self.assertEqual(foot.get_length(), 3)
        self.assertEqual(foot.get_structure(), [Weight.HEAVY, Weight.LIGHT, Weight.LIGHT])
        
    def test_spondaeus(self):
        foot = Foot.SPONDAEUS
        self.assertEqual(foot.get_length(), 2)
        self.assertEqual(foot.get_structure(), [Weight.HEAVY, Weight.HEAVY])

    def test_trochaeus(self):
        foot = Foot.TROCHAEUS
        self.assertEqual(foot.get_length(), 2)
        self.assertEqual(foot.get_structure(), [Weight.HEAVY, Weight.LIGHT])