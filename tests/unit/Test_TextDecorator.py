import unittest

from elisio.parser.versefactory import VerseFactory, VerseType
from elisio.utils.textdecorator import TextDecorator


class TestTextDecorator(unittest.TestCase):

    def test_dec_type_error(self):
        with self.assertRaises(TypeError):
            TextDecorator("Arma virumque cano, Troiae qui primus ab oris")

    def test_dec_basic(self):
        verse = VerseFactory.create("Arma virumque cano, Troiae qui primus ab oris", classes=VerseType.HEXAMETER)
        s = TextDecorator(verse).decorate()
        self.assertEqual(s, "A̱rma̯ vi̯ru̱mque̯ ca̯no̱, Tro̱iae̱ qui̱ pri̱mu̯s a̯b o̱ri̱s")

    def test_dec_bracket(self):
        verse = VerseFactory.create("Urbs antiqua fuit (Tyrii tenuere coloni)", classes=VerseType.HEXAMETER)
        s = TextDecorator(verse).decorate()
        self.assertEqual(s, "U̱rbs a̱nti̱qua̯ fu̯i̱t (Ty̯ri̯i̱ te̯nu̯e̱re̯ co̯lo̱ni̱)")

    def test_dec_ancepsfinal(self):
        verse = VerseFactory.create("nos patriae finis et dulcia linquimus arva.", classes=VerseType.HEXAMETER)
        s = TextDecorator(verse).decorate()
        self.assertEqual(s, "no̱s pa̯tri̯ae̱ fi̱ni̱s e̱t du̱lci̯a̯ li̱nqui̯mu̯s a̱rva.")
