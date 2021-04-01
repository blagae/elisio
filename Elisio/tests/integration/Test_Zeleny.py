import unittest

from elisio.engine.VerseFactory import VerseFactory
from elisio.engine.verse.VerseType import VerseType
from elisio.tests.unit.Test_Verse import TYPICAL_VERSE


class TestAccent(unittest.TestCase):
    def test_zeleny_armavirumque(self):
        verse = VerseFactory.create(TYPICAL_VERSE, classes=VerseType.HEXAMETER)
        verse.parse()
        correct = [4, 3, 3, 4, 2, 3, 1, 4]
        self.assertEqual(correct, verse.get_zeleny_score())

    def test_zeleny_lavinia(self):
        verse = VerseFactory.create("Italiam fato profugus Laviniaque venit", classes=VerseType.HEXAMETER)
        verse.parse()
        correct = [2, 4, 4, 6, 4, 4]
        self.assertEqual(correct, verse.get_zeleny_score())

    def test_zeleny_litora(self):
        verse = VerseFactory.create("litora, multum ille et terris iactatus et alto", classes=VerseType.HEXAMETER)
        verse.parse()
        correct = [4, 2, 2, 2, 6, 3, 1, 4]
        self.assertEqual(correct, verse.get_zeleny_score())