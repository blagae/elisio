import unittest
from Elisio.engine.TextDecorator import TextDecorator
from Elisio.utils import set_django
from Elisio.engine.Hexameter import HexameterCreator
from Elisio.engine.VerseFactory import VerseFactory

set_django()

class TestTextDecorator(unittest.TestCase):
    def test_dec(self):
        verse = VerseFactory.create("Arma virumque cano, Troiae qui primus ab oris", False, True, classes=HexameterCreator)
        s = TextDecorator(verse).decorate()
        self.assertEquals(s, "A̱rma̯ vi̯ru̱mque̯ ca̯no̱, Tro̱iae̱ qui̱ pri̱mu̯s a̯b o̱ri̱s ")