import unittest
from Elisio.engine.Verse import set_django
from Elisio.engine.Word import Word
from Elisio.exceptions import WordException
set_django()
from Elisio.models import DeviantWord

class TestDeviantWord(unittest.TestCase):

    def test_aeneas(self):
        word = Word("aeneas")
        self.assertTrue(word.split_from_deviant_word())

    def test_aeneas_capital(self):
        word = Word("Aenei")
        self.assertTrue(word.split_from_deviant_word())

    def test_nonalphatic_fails(self):
        with self.assertRaises(WordException):
            word = Word("Aenei,")