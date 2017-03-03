import unittest
from Elisio.engine.TextDecorator import TextDecorator
from Elisio.utils import set_django
from Elisio.engine.Hexameter import HexameterCreator
from Elisio.engine.VerseFactory import VerseFactory

set_django()

class TestTextDecorator(unittest.TestCase):
    def test_dec(self):
        verse = VerseFactory.create("Arma virumque cano, Troiae qui primus ab oris", False, False, classes=HexameterCreator)
        s = TextDecorator(verse).decorate()
        self.assertEqual(s, "A̱rma̯ vi̯ru̱mque̯ ca̯no̱, Tro̱iae̱ qui̱ pri̱mu̯s a̯b o̱ri̱s ")

    def test_bracket(self):
        verse = VerseFactory.create("Urbs antiqua fuit (Tyrii tenuere coloni)", False, False, classes=HexameterCreator)
        s = TextDecorator(verse).decorate()
        self.assertEqual(s, "U̱rbs a̱nti̱qua̯ fu̯i̱t (Ty̯ri̯i̱ te̱nue̱re̯ co̯lo̱ni̱) ")
