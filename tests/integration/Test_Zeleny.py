import unittest

from elisio.parser.versefactory import VerseFactory, VerseType


class TestAccent(unittest.TestCase):
    def test_zeleny_armavirumque(self):
        verse = VerseFactory.create("Arma virumque cano, Troiae qui primus ab oris", classes=VerseType.HEXAMETER)
        verse.parse()
        correct = [4, 3, 3, 4, 2, 3, 1, 4]
        self.assertEqual(correct, verse.get_zeleny_score())

    def test_zeleny_litora(self):
        verse = VerseFactory.create("litora, multum ille et terris iactatus et alto", classes=VerseType.HEXAMETER)
        verse.parse()
        correct = [4, 2, 2, 2, 6, 3, 1, 4]
        self.assertEqual(correct, verse.get_zeleny_score())
