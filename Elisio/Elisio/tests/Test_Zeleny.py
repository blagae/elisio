import unittest
from Elisio.engine.Hexameter import HexameterCreator
from Elisio.engine.VerseFactory import VerseFactory
from Elisio.tests.Test_Verse import TYPICAL_VERSE

class TestAccent(unittest.TestCase):
    def test_zeleny_armavirumque(self):
        verse = VerseFactory.create(TYPICAL_VERSE, classes=HexameterCreator)
        verse.parse()
        correct = [4,3,3,4,2,3,1,4]
        score = verse.get_zeleny_score()
        self.assertEqual(correct, score)

    def test_zeleny_lavinia(self):
        verse = VerseFactory.create("Italiam fato profugus Laviniaque venit", classes=HexameterCreator)
        verse.parse()
        correct = [2,4,4,6,4,4]
        score = verse.get_zeleny_score()
        self.assertEqual(correct, score)
