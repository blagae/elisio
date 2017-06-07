import unittest
from Elisio.engine.Hexameter import HexameterCreator
from Elisio.engine.Syllable import Weight
from Elisio.engine.VerseFactory import VerseFactory
from Elisio.tests.Test_Verse import TYPICAL_VERSE

class TestAccent(unittest.TestCase):
    def test_accent_armavirumque(self):
        verse = VerseFactory.create(TYPICAL_VERSE, classes=HexameterCreator)
        verse.parse()
        # arma
        self.assertEqual(verse.words[0].syllables[0].stressed, True)
        self.assertEqual(verse.words[0].syllables[1].stressed, False)
        # virumque
        self.assertEqual(verse.words[1].syllables[0].stressed, False)
        self.assertEqual(verse.words[1].syllables[1].stressed, True)
        self.assertEqual(verse.words[1].syllables[2].stressed, False)
        # cano
        self.assertEqual(verse.words[2].syllables[0].stressed, True)
        self.assertEqual(verse.words[2].syllables[1].stressed, False)
        # Troiae
        self.assertEqual(verse.words[3].syllables[0].stressed, True)
        self.assertEqual(verse.words[3].syllables[1].stressed, False)
        # qui
        self.assertEqual(verse.words[4].syllables[0].stressed, True)
        # primus
        self.assertEqual(verse.words[5].syllables[0].stressed, True)
        self.assertEqual(verse.words[5].syllables[1].stressed, False)
        # ab
        self.assertEqual(verse.words[6].syllables[0].stressed, True)
        # oris
        self.assertEqual(verse.words[7].syllables[0].stressed, True)
        self.assertEqual(verse.words[7].syllables[1].stressed, False)
        
    def test_accent_lavinia(self):
        verse = VerseFactory.create("Italiam fato profugus Laviniaque venit", classes=HexameterCreator)
        verse.parse()
        # italiam
        self.assertEqual(verse.words[0].syllables[0].stressed, False)
        self.assertEqual(verse.words[0].syllables[1].stressed, True)
        self.assertEqual(verse.words[0].syllables[2].stressed, False)
        self.assertEqual(verse.words[0].syllables[3].stressed, False)
        # fato
        self.assertEqual(verse.words[1].syllables[0].stressed, True)
        self.assertEqual(verse.words[1].syllables[1].stressed, False)
        # profugus
        self.assertEqual(verse.words[2].syllables[0].stressed, True)
        self.assertEqual(verse.words[2].syllables[1].stressed, False)
        # Laviniaque
        self.assertEqual(verse.words[3].syllables[0].stressed, False)
        self.assertEqual(verse.words[3].syllables[1].stressed, True)
        self.assertEqual(verse.words[3].syllables[2].stressed, False)
        self.assertEqual(verse.words[3].syllables[3].stressed, False)
        # venit
        self.assertEqual(verse.words[4].syllables[0].stressed, True)
        self.assertEqual(verse.words[4].syllables[1].stressed, False)
