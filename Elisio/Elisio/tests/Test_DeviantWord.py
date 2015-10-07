import unittest
from Elisio.engine.Verse import set_django
from Elisio.engine.Syllable import Syllable
from Elisio.engine.Word import Word, Weight
from Elisio.exceptions import WordException
set_django()
from Elisio.models import DeviantWord

class TestDeviantWord(unittest.TestCase):
    # TODO: build tests for words that are actually deviant (i.e. not names)
    # ----
    # this test class requires that a DeviantWord named aene[ai].*
    # be present in the database. If not, run syncdb or migrate
    """
    # unit tests
    def test_table(self):
        self.assertIsInstance(DeviantWord.find("aenean"), DeviantWord)

    def test_table_fail(self):
        self.assertIsNone(DeviantWord.find("aeneo"))
    def test_list(self):
        # TODO: not sure if this will always succeed
        lst = DeviantWord.words
        self.assertTrue(len(lst) == 0)
        DeviantWord.get_list()
        lst = DeviantWord.words
        self.assertTrue(len(lst)>0)


    # component tests
    def test_aeneas_works(self):
        word = Word("aeneas")
        self.assertTrue(word.split_from_deviant_word())

    def test_aeneas_capital_works(self):
        word = Word("Aenei")
        self.assertTrue(word.split_from_deviant_word())
    
    def test_aeneas_is_correct(self):
        word = Word("aeneas")
        expected = [Weight.HEAVY, Weight.HEAVY, Weight.HEAVY]
        self.assertEqual(expected, word.get_syllable_structure())

    def test_aenea_is_correct(self):
        word = Word("aenea")
        weights = [Weight.HEAVY, Weight.HEAVY, Weight.ANCEPS]
        sylls = [Syllable("ae"), Syllable("ne"), Syllable("a")]
        self.assertEqual(weights, word.get_syllable_structure())
        self.assertEqual(sylls, word.syllables)

    def test_nonalphatic_fails(self):
        with self.assertRaises(WordException):
            word = Word("Aenei,")
    #"""