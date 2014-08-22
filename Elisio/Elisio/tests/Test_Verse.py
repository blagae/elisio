import unittest
from Elisio.engine.verseProcessor import *
from Elisio.engine.wordProcessor import *

setDjango()

from Elisio.models import Db_Verse
from Elisio.exceptions import ScansionException


typical_verse = "Arma virumque cano, Troiae qui primus ab oris"
words = ['Arma', 'virumque', 'cano', 'Troiae', 'qui', 'primus', 'ab', 'oris']
expected_word_list = []
for word in words:
    expected_word_list.append(Word(word))


class Test_Verse(unittest.TestCase):
    """ Test_Verse class
    Unit tests for splitting a verse into words
    commit 1 (blagae): BLI 9
    reason: creation
    """
    def constructVerse(self, text = typical_verse):
        """ Construct a verse object from a given text """
        constructedVerse = Verse(text)
        return constructedVerse

    def test_VerseConstruct(self):
        """ constructing a Verse must work """
        self.assertTrue(isinstance(self.constructVerse(), Verse))
        self.assertTrue(isinstance(self.constructVerse(), Verse))

    def test_VerseFail(self):
        with self.assertRaises(ScansionException):
            self.constructVerse(7)

    def test_VerseEqual(self):
        """ Two separate verses are equal if they carry the exact same text
        even if one is split and the other isn't
        """
        verse1 = self.constructVerse()
        verse2 = self.constructVerse()
        verse1.split()
        self.assertEqual(verse1, verse2)

    def test_VerseNotEqual(self):
        """ Two separate verses are equal only if they carry the exact same text
        """
        verse1 = self.constructVerse()
        verse2 = self.constructVerse(typical_verse.replace('cano', 'cono'))
        self.assertNotEqual(verse1, verse2)

    def test_VerseSplit(self):
        """ A normal verse must be split into words correctly """
        verse = self.constructVerse()
        verse.split()
        self.assertEqual(verse.words, expected_word_list)

    def test_VerseSplitPunctuation(self):
        """ A verse with unusual and heavy punctuation must be split into words correctly """
        verse = self.constructVerse("""(Arma'virumque,%cano.!Troiae^$qui";primus/ab oris)""")
        verse.split()
        self.assertEqual(verse.words, expected_word_list)
        
    def test_VerseSplitSpaces(self):
        """ A verse with unusual and heavy spacing must be split into words correctly """
        verse = self.constructVerse("""      Arma\tvirumque\rcano\nTroiae\r\nqui\n\rprimus  \b \r   ab    oris.  """)
        verse.split()
        self.assertEqual(verse.words, expected_word_list)

        
    def test_VerseSplitUnusualCharacter(self):
        """ A verse with unusual characters (diacritics) must be split into words correctly """
        # TODO: aena should have a diaeresis
        """
        verse = self.constructVerse("litore aena locant alii flammasque ministrant.")
        verse.split()
        expected_list = ["litore","aena","locant","alii","flammasque","ministrant."]
        self.assertEqual(verse.words, expected_list)
        """
        
    def test_VerseScansionElisionRegular(self):
        verse = self.constructVerse('multo ille')
        expected_result = [[Weights.HEAVY, Weights.NONE],
                           [Weights.HEAVY, Weights.LIGHT]]
        verse.split()
        self.assertEqual(verse.getSyllableLengths(), expected_result)
        
    def test_VerseScansionElisionOnM(self):
        verse = self.constructVerse('multum ille')
        expected_result = [[Weights.HEAVY, Weights.NONE],
                           [Weights.HEAVY, Weights.LIGHT]]
        verse.split()
        self.assertEqual(verse.getSyllableLengths(), expected_result)
        
    def test_VerseScansionElisionWithH(self):
        verse = self.constructVerse('multo hille')
        expected_result = [[Weights.HEAVY, Weights.NONE],
                           [Weights.HEAVY, Weights.LIGHT]]
        verse.split()
        self.assertEqual(verse.getSyllableLengths(), expected_result)

    def test_VerseScansionElisionSemivowelWithH(self):
        verse = self.constructVerse('multu hille')
        expected_result = [[Weights.HEAVY, Weights.NONE],
                           [Weights.HEAVY, Weights.LIGHT]]
        verse.split()
        self.assertEqual(verse.getSyllableLengths(), expected_result)

    def test_VerseScansionElisionOnMWithH(self):
        verse = self.constructVerse('multum hille')
        expected_result = [[Weights.HEAVY, Weights.NONE],
                           [Weights.HEAVY, Weights.LIGHT]]
        verse.split()
        self.assertEqual(verse.getSyllableLengths(), expected_result)

    def test_VerseScansionFinalAnceps(self):
        verse = self.constructVerse('multus ille')
        expected_result = [[Weights.HEAVY, Weights.ANCEPS],
                           [Weights.HEAVY, Weights.LIGHT]]
        verse.split()
        self.assertEqual(verse.getSyllableLengths(), expected_result)
        
    def test_VerseScansionHeavyMaker(self):
        verse = self.constructVerse('esse Zephyrumque')
        expected_result = [[Weights.HEAVY, Weights.HEAVY],
                           [Weights.ANCEPS, Weights.ANCEPS, Weights.HEAVY, Weights.LIGHT]]
        verse.split()
        self.assertEqual(verse.getSyllableLengths(), expected_result)

    def test_VerseScansionHeavyMakingCluster(self):
        verse = self.constructVerse('esse strabo')
        expected_result = [[Weights.HEAVY, Weights.HEAVY],
                           [Weights.ANCEPS, Weights.HEAVY]]
        verse.split()
        self.assertEqual(verse.getSyllableLengths(), expected_result)

    def test_VerseScansionFull(self):
        """ A regular verse must get all relevant scansion information immediately
        Example:
        arma virumque cano troiae qui primus ab oris
        _  x  x _   u  x _   x _    _   x x  x  x _
        Note that this archetypical verse does not test for a lot
        """
        verse = self.constructVerse()
        expected_result = [[Weights.HEAVY, Weights.ANCEPS,],
                           [Weights.ANCEPS, Weights.HEAVY, Weights.LIGHT,],
                           [Weights.ANCEPS, Weights.HEAVY,],
                           [Weights.ANCEPS, Weights.HEAVY,],
                           [Weights.HEAVY,],
                           [Weights.ANCEPS, Weights.ANCEPS,],
                           [Weights.ANCEPS,],
                           [Weights.ANCEPS, Weights.HEAVY]]
        verse.split()
        self.assertEqual(verse.getSyllableLengths(), expected_result)


    def test_VerseDatabase(self):
        """ Checks to see if a database object exists
        Expects there to be a Database Verse object with primary key 1
        ==> PLEASE CHECK FIXTURES
        """
        db_verse = Db_Verse.objects.get(pk=1)
        verse = db_verse.getVerse()
        self.assertTrue(isinstance(verse, Verse))

    def test_VerseLetterFrequencies(self):
        letterList = {}
        db_verses = Db_Verse.objects.all()
        for db_verse in db_verses:
            verse = db_verse.getVerse()
            verse.split()
            for word in verse.words:
                for letter in word.text:
                    if not letter in letterList:
                        if not letter in Letter.validLetters:
                            letter = letter
                        letterList[letter] = 0
                    else:
                        letterList[letter] += 1
        letterList = None

class Test_Hexameter(unittest.TestCase):
    
    def constructHexameter(self, text = typical_verse):
        """ Construct a Hexameter object from a given text """
        constructedVerse = Hexameter(text)

        return constructedVerse

    
    def test_HexameterConstruct(self):
        """ constructing a Hexameter must work """
        self.assertTrue(isinstance(self.constructHexameter(), Verse))
        self.assertTrue(isinstance(self.constructHexameter(), Hexameter))

    def test_HexameterScanBasicCase(self):
        expected_feet = [Feet.DACTYLUS, Feet.DACTYLUS, Feet.SPONDAEUS, Feet.SPONDAEUS, Feet.DACTYLUS, Feet.SPONDAEUS]
        verse = self.constructHexameter()
        verse.split()
        verse.scan()
        self.assertEqual(verse.feet, expected_feet)

    def test_HexameterScanAllLolol(self):
        """ frivolous check to see how many verses work """
        dbverses = Db_Verse.objects.all()
        worked = 0
        failed = 0
        fails = ''
        for dbverse in dbverses:
            try:
                if dbverse.number == 777:
                    worked = worked
                verse = Hexameter(dbverse.contents)
                verse.split()
                verse.scan()
                worked += 1
            except ScansionException as se:
                failed += 1
                print("ScansionException({0}: {1}): {2}".format(dbverse.number, verse.text, se))
        self.fail(str(worked) + " worked, " + str(failed) + " failed")