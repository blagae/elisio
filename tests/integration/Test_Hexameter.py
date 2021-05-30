import unittest

from elisio.parser.hexameter import Hexameter
from elisio.parser.verse import Foot, Verse
from elisio.parser.versefactory import VerseFactory, VerseType


def construct_hexameter(text="Arma virumque cano, Troiae qui primus ab oris"):
    """ Construct a Hexameter object from a given text """
    constructed_verse = VerseFactory.create(text, creators=VerseType.HEXAMETER)
    return constructed_verse


class TestHexameter(unittest.TestCase):
    """ testing specifically for the hexameter """

    def test_hexameter_construct(self):
        """ constructing a Hexameter must work """
        self.assertTrue(isinstance(construct_hexameter(), Verse))
        self.assertTrue(isinstance(construct_hexameter(), Hexameter))

    def test_hexameter_scan_basic_case(self):
        """ Aen. 1, 1 must scan correctly imo """
        expected_feet = [Foot.DACTYLUS, Foot.DACTYLUS,
                         Foot.SPONDAEUS, Foot.SPONDAEUS,
                         Foot.DACTYLUS, Foot.SPONDAEUS]
        verse = construct_hexameter()
        self.assertEqual(verse.feet, expected_feet)

    def test_hexameter_scan_diaeresis(self):
        """ Aen. 1, 1 must scan correctly imo """
        expected_feet = [Foot.SPONDAEUS, Foot.DACTYLUS,
                         Foot.SPONDAEUS, Foot.SPONDAEUS,
                         Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        verse = construct_hexameter('quae cuncta aërii discerpunt irrita venti.')
        self.assertEqual(verse.feet, expected_feet)
