""" Test classes for Verse scanning """
import unittest
from Elisio.engine.Verse import Verse
from Elisio.engine.Word import Word
from Elisio.exceptions import VerseException

TYPICAL_VERSE = "Arma virumque cano, Troiae qui primus ab oris"
WORDS = ['Arma', 'virumque', 'cano', 'Troiae', 'qui', 'primus', 'ab', 'oris']
EXPECTED_WORD_LIST = []
for word in WORDS:
    EXPECTED_WORD_LIST.append(Word(word))


class TestVerse(unittest.TestCase):
    """ Test_verse class
    Unit tests for splitting a verse into words
    commit 1 (blagae): BLI 9
    reason: creation
    """

    def construct_verse(self, text=TYPICAL_VERSE):
        """ Construct a verse object from a given text """
        constructed_verse = Verse(text)
        return constructed_verse

    def test_verse_construct(self):
        """ constructing a Verse must work """
        self.assertTrue(isinstance(self.construct_verse(), Verse))
        self.assertTrue(isinstance(self.construct_verse(), Verse))

    def test_verse_fail(self):
        """ fail on invalid input """
        with self.assertRaises(VerseException):
            self.construct_verse(7)

    def test_verse_equal(self):
        """ Two separate verses are equal if they carry the exact same text
        even if one is split and the other isn't
        """
        verse1 = self.construct_verse()
        verse2 = self.construct_verse()
        verse1.words = []
        self.assertEqual(verse1, verse2)

    def test_verse_not_equal(self):
        """ Two separate verses are equal only if they carry the exact same text
        """
        verse1 = self.construct_verse()
        verse2 = self.construct_verse(TYPICAL_VERSE.replace('cano', 'cono'))
        self.assertNotEqual(verse1, verse2)
