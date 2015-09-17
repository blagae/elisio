import unittest
from Elisio.engine.Verse import Foot
from Elisio.engine.Syllable import Weight
from Elisio.exceptions import ScansionException

class TestFoot(unittest.TestCase):
    def test_unknown_struc_fails(self):
        with self.assertRaises(ScansionException):
            Foot.UNKNOWN.get_structure()

    def test_unknown_len_fails(self):
        with self.assertRaises(ScansionException):
            Foot.UNKNOWN.get_length()
            
    def test_dactylus(self):
        foot = Foot.DACTYLUS
        self.assertEquals(foot.get_length(), 3)
        self.assertEquals(foot.get_structure(), [Weight.HEAVY, Weight.LIGHT, Weight.LIGHT])
        
    def test_spondaeus(self):
        foot = Foot.SPONDAEUS
        self.assertEquals(foot.get_length(), 2)
        self.assertEquals(foot.get_structure(), [Weight.HEAVY, Weight.HEAVY])

    def test_trochaeus(self):
        foot = Foot.TROCHAEUS
        self.assertEquals(foot.get_length(), 2)
        self.assertEquals(foot.get_structure(), [Weight.HEAVY, Weight.LIGHT])