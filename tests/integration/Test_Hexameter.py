import unittest

from elisio.parser.hexameter import Hexameter
from elisio.parser.verse import Foot, Verse
from elisio.parser.versefactory import VerseFactory, VerseType


class TestHexameter(unittest.TestCase):
    """ testing specifically for the hexameter """

    @staticmethod
    def construct_hexameter(text="Arma virumque cano, Troiae qui primus ab oris"):
        """ Construct a Hexameter object from a given text """
        constructed_verse = VerseFactory.create(text, classes=VerseType.HEXAMETER)
        return constructed_verse

    def test_hexameter_construct(self):
        """ constructing a Hexameter must work """
        self.assertTrue(isinstance(self.construct_hexameter(), Verse))
        self.assertTrue(isinstance(self.construct_hexameter(), Hexameter))

    def test_hexameter_scan_basic_case(self):
        """ Aen. 1, 1 must scan correctly imo """
        expected_feet = [Foot.DACTYLUS, Foot.DACTYLUS,
                         Foot.SPONDAEUS, Foot.SPONDAEUS,
                         Foot.DACTYLUS, Foot.SPONDAEUS]
        verse = self.construct_hexameter()
        self.assertEqual(verse.feet, expected_feet)
