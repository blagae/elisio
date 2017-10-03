""" Test classes for Verse scanning """
import unittest
from Elisio.engine.Verse import Verse
from Elisio.utils import set_django
from Elisio.engine.Word import Word
from Elisio.engine.VerseFactory import VerseFactory

set_django()

from Elisio.models.metadata import DatabaseVerse

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

    def test_verse_database(self):
        """ Checks to see if a database object exists
        Expects there to be a Database Verse object with primary key 1
        ==> PLEASE CHECK FIXTURES
        """
        db_verse = DatabaseVerse.objects.get(pk=1)
        verse = db_verse.get_verse()
        self.assertFalse(isinstance(verse, Verse))

    def test_verse_letter_frequencies(self):
        """ routine created for scanning optimizations """
        letterlist = {}
        # db_verses = DatabaseVerse.objects.all()
        db_verses = DatabaseVerse.objects.filter(id__lte=50)
        for db_verse in db_verses:
            verse = db_verse.get_verse()
            words = VerseFactory.split(verse)
            for wording in words:
                for letter in wording.text:
                    if letter not in letterlist:
                        letterlist[letter] = 0
                    else:
                        letterlist[letter] += 1
        letterlist.clear()
