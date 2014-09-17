import unittest
from Elisio.engine.verseProcessor import Verse, Hexameter, Feet, set_django
from Elisio.engine.wordProcessor import Weights, Word
from Elisio.exceptions import ScansionException

set_django()

from Elisio.models import Db_Verse

typical_verse = "Arma virumque cano, Troiae qui primus ab oris"
words = ['Arma', 'virumque', 'cano', 'Troiae', 'qui', 'primus', 'ab', 'oris']
expected_word_list = []
for word in words:
    expected_word_list.append(Word(word))


class Test_verse(unittest.TestCase):
    """ Test_verse class
    Unit tests for splitting a verse into words
    commit 1 (blagae): BLI 9
    reason: creation
    """

    def construct_verse(self, text=typical_verse):
        """ Construct a verse object from a given text """
        constructed_verse = Verse(text)
        return constructed_verse

    def test_verse_construct(self):
        """ constructing a Verse must work """
        self.assertTrue(isinstance(self.construct_verse(), Verse))
        self.assertTrue(isinstance(self.construct_verse(), Verse))

    def test_verse_fail(self):
        with self.assertRaises(ScansionException):
            self.construct_verse(7)

    def test_verse_equal(self):
        """ Two separate verses are equal if they carry the exact same text
        even if one is split and the other isn't
        """
        verse1 = self.construct_verse()
        verse2 = self.construct_verse()
        verse1.split()
        self.assertEqual(verse1, verse2)

    def test_verse_not_equal(self):
        """ Two separate verses are equal only if they carry the exact same text
        """
        verse1 = self.construct_verse()
        verse2 = self.construct_verse(typical_verse.replace('cano', 'cono'))
        self.assertNotEqual(verse1, verse2)

    def test_verse_split(self):
        """ A normal verse must be split into words correctly """
        verse = self.construct_verse()
        verse.split()
        self.assertEqual(verse.words, expected_word_list)

    def test_verse_split_punctuation(self):
        """ A verse with unusual and heavy punctuation must be split into words correctly """
        verse = self.construct_verse("""(Arma'virumque,%cano.!Troiae^$qui";primus/ab oris)""")
        verse.split()
        self.assertEqual(verse.words, expected_word_list)
        
    def test_verse_split_spaces(self):
        """ A verse with unusual and heavy spacing must be split into words correctly """
        verse = self.construct_verse("""      Arma\tvirumque\rcano\nTroiae\r\nqui\n\rprimus  \b \r   ab    oris.  """)
        verse.split()
        self.assertEqual(verse.words, expected_word_list)

        
    def test_verse_split_unusual_char(self):
        """ A verse with unusual characters (diacritics) must be split into words correctly """
        # TODO: aena should have a diaeresis
        """
        verse = self.constructVerse("litore aena locant alii flammasque ministrant.")
        verse.split()
        expected_list = ["litore","aena","locant","alii","flammasque","ministrant."]
        self.assertEqual(verse.words, expected_list)
        """
        
    def test_verse_scan_elis_reg(self):
        verse = self.construct_verse('multo ille')
        expected_result = [[Weights.HEAVY, Weights.NONE],
                           [Weights.HEAVY, Weights.LIGHT]]
        verse.split()
        self.assertEqual(verse.get_syllable_weights(), expected_result)
        
    def test_verse_scan_elis_on_m(self):
        verse = self.construct_verse('multum ille')
        expected_result = [[Weights.HEAVY, Weights.NONE],
                           [Weights.HEAVY, Weights.LIGHT]]
        verse.split()
        self.assertEqual(verse.get_syllable_weights(), expected_result)
        
    def test_verse_scan_elis_with_h(self):
        verse = self.construct_verse('multo hille')
        expected_result = [[Weights.HEAVY, Weights.NONE],
                           [Weights.HEAVY, Weights.LIGHT]]
        verse.split()
        self.assertEqual(verse.get_syllable_weights(), expected_result)

    def test_verse_scan_elis_semivowel_with_h(self):
        verse = self.construct_verse('multu hille')
        expected_result = [[Weights.HEAVY, Weights.NONE],
                           [Weights.HEAVY, Weights.LIGHT]]
        verse.split()
        self.assertEqual(verse.get_syllable_weights(), expected_result)

    def test_verse_scan_elis_on_m_with_h(self):
        verse = self.construct_verse('multum hille')
        expected_result = [[Weights.HEAVY, Weights.NONE],
                           [Weights.HEAVY, Weights.LIGHT]]
        verse.split()
        self.assertEqual(verse.get_syllable_weights(), expected_result)

    def test_verse_scan_final_anceps(self):
        verse = self.construct_verse('multus ille')
        expected_result = [[Weights.HEAVY, Weights.ANCEPS],
                           [Weights.HEAVY, Weights.LIGHT]]
        verse.split()
        self.assertEqual(verse.get_syllable_weights(), expected_result)
        
    def test_verse_scan_heavy_maker(self):
        verse = self.construct_verse('esse Zephyrumque')
        expected_result = [[Weights.HEAVY, Weights.HEAVY],
                           [Weights.ANCEPS, Weights.ANCEPS, Weights.HEAVY, Weights.LIGHT]]
        verse.split()
        self.assertEqual(verse.get_syllable_weights(), expected_result)

    def test_verse_scan_heavy_making_cluster(self):
        verse = self.construct_verse('esse strabo')
        expected_result = [[Weights.HEAVY, Weights.HEAVY],
                           [Weights.ANCEPS, Weights.HEAVY]]
        verse.split()
        self.assertEqual(verse.get_syllable_weights(), expected_result)

    def test_verse_scan_full(self):
        """ A regular verse must get all relevant scansion information immediately
        Example:
        arma virumque cano troiae qui primus ab oris
        _  x  x _   u  x _   _ _    _   x x  x  x _
        Note that this archetypical verse does not test for a lot
        """
        verse = self.construct_verse()
        expected_result = [[Weights.HEAVY, Weights.ANCEPS,],
                           [Weights.ANCEPS, Weights.HEAVY, Weights.LIGHT,],
                           [Weights.ANCEPS, Weights.HEAVY,],
                           [Weights.HEAVY, Weights.HEAVY,],
                           [Weights.HEAVY,],
                           [Weights.ANCEPS, Weights.ANCEPS,],
                           [Weights.ANCEPS,],
                           [Weights.ANCEPS, Weights.HEAVY]]
        verse.split()
        self.assertEqual(verse.get_syllable_weights(), expected_result)


    def test_verse_database(self):
        """ Checks to see if a database object exists
        Expects there to be a Database Verse object with primary key 1
        ==> PLEASE CHECK FIXTURES
        """
        db_verse = Db_Verse.objects.get(pk=1)
        verse = db_verse.getVerse()
        self.assertTrue(isinstance(verse, Verse))

    def test_verse_letter_frequencies(self):
        letterList = {}
        db_verses = Db_Verse.objects.all()
        for db_verse in db_verses:
            verse = db_verse.getVerse()
            verse.split()
            for word in verse.words:
                for letter in word.text:
                    if not letter in letterList:
                        letterList[letter] = 0
                    else:
                        letterList[letter] += 1
        letterList = None

class Test_Hexameter(unittest.TestCase):
    
    def construct_hexameter(self, text=typical_verse):
        """ Construct a Hexameter object from a given text """
        constructed_verse = Hexameter(text)

        return constructed_verse

    
    def test_hexameter_construct(self):
        """ constructing a Hexameter must work """
        self.assertTrue(isinstance(self.construct_hexameter(), Verse))
        self.assertTrue(isinstance(self.construct_hexameter(), Hexameter))

    def test_hexameter_scan_basic_case(self):
        expected_feet = [Feet.DACTYLUS, Feet.DACTYLUS, Feet.SPONDAEUS, Feet.SPONDAEUS, Feet.DACTYLUS, Feet.SPONDAEUS]
        verse = self.construct_hexameter()
        verse.split()
        verse.scan()
        self.assertEqual(verse.feet, expected_feet)

    def test_hexameter_scan_all(self):
        """ frivolous check to see how many verses work """
        dbverses = Db_Verse.objects.all()
        worked = 0
        failed = 0
        fails = ''
        for dbverse in dbverses:
            try:
                if dbverse.number == 29:
                    worked = worked
                verse = Hexameter(dbverse.contents)
                verse.split()
                verse.scan()
            except ScansionException as se:
                failed += 1
                print("{3}({0}: {1}): {2}".format(dbverse.number, verse.text, se, type(se)))
            else:
                worked += 1
        self.fail(str(worked) + " worked, " + str(failed) + " failed")
