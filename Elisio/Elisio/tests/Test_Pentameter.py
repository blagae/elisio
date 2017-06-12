import unittest
from Elisio.engine.Verse import Verse, Foot
from Elisio.utils import set_django
from Elisio.engine.Pentameter import Pentameter
from Elisio.engine.VerseFactory import VerseFactory, VerseType
from Elisio.exceptions import PentameterException, VerseException

set_django()

from Elisio.models import DatabaseVerse, WordOccurrence

class TestPentameter(unittest.TestCase):
    """ testing specifically for the pentameter """
    def test_pentameter_scan_basic_case(self):
        """ Ov., Am., Ep. Ips., 2 must scan correctly imo """
        expected_feet = [Foot.DACTYLUS, Foot.SPONDAEUS,
                         Foot.MACRON, Foot.DACTYLUS,
                         Foot.DACTYLUS, Foot.MACRON]
        verse = VerseFactory.create("tres sumus; hoc illi praetulit auctor opus", classes=VerseType.PENTAMETER)
        self.assertEqual(verse.feet, expected_feet)
        
    def test_pentameter_scan_incorrect_heavy_in_fourth(self):
        with self.assertRaises(VerseException):
            verse = VerseFactory.create("tres sumus hoc illi praetullit auctor opus", classes=VerseType.PENTAMETER)

    def test_pentameter_scan_incorrect_heavy_in_fifth(self):
        with self.assertRaises(VerseException):
            verse = VerseFactory.create("tres sumus hoc illi praetulit auctor copus", classes=VerseType.PENTAMETER)

    def test_pentameter_scan_incorrect_light_in_fourth(self):
        with self.assertRaises(VerseException):
            verse = VerseFactory.create("tres sumus hoc illi praetul ataor opus", classes=VerseType.PENTAMETER)

    def test_pentameter_scan_incorrect_light_in_fifth(self):
        with self.assertRaises(VerseException):
            verse = VerseFactory.create("tres sumus hoc illi praotul auctor opus", classes=VerseType.PENTAMETER)
