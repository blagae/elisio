import unittest
from Elisio.engine.TextDecorator import TextDecorator
from Elisio.utils import set_django
from Elisio.engine.Hexameter import HexameterCreator
from Elisio.engine.VerseFactory import VerseFactory

set_django()

class TestTextDecorator(unittest.TestCase):
    def test_dec(self):
        verse = VerseFactory.create("litora, multum ille et terris iactatus et alto", False, True, classes=HexameterCreator)
        s = TextDecorator(verse).decorate()
        text_file = open("output.txt", "w", encoding='UTF-8')
        text_file.write(s)
