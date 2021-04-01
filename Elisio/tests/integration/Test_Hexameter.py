import unittest

from elisio.engine.Verse import Foot, Verse
from elisio.engine.VerseFactory import VerseFactory
from elisio.engine.verse.Hexameter import Hexameter
from elisio.engine.verse.VerseType import VerseType
from elisio.tests.unit.Test_Verse import TYPICAL_VERSE


class TestHexameter(unittest.TestCase):
    """ testing specifically for the hexameter """

    @staticmethod
    def construct_hexameter(text=TYPICAL_VERSE):
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
