import unittest

from elisio.exceptions import VerseException
from elisio.parser.verse import Foot
from elisio.parser.versefactory import VerseFactory, VerseType


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
            VerseFactory.create("tres sumus hoc illi praetullit auctor opus", classes=VerseType.PENTAMETER)

    def test_pentameter_scan_incorrect_heavy_in_fifth(self):
        with self.assertRaises(VerseException):
            VerseFactory.create("tres sumus hoc illi praetulit auctor copus", classes=VerseType.PENTAMETER)

    def test_pentameter_scan_incorrect_light_in_fourth(self):
        with self.assertRaises(VerseException):
            VerseFactory.create("tres sumus hoc illi praetul ataor opus", classes=VerseType.PENTAMETER)

    def test_pentameter_scan_incorrect_light_in_fifth(self):
        with self.assertRaises(VerseException):
            VerseFactory.create("tres sumus hoc illi praotul auctor opus", classes=VerseType.PENTAMETER)
