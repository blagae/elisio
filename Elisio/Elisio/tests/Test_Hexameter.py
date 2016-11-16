import unittest
from Elisio.engine.Verse import Verse, Foot
from Elisio.engine.Syllable import Weight
from Elisio.utils import set_django
from Elisio.engine.Hexameter import Hexameter, HexameterCreator
from Elisio.engine.VerseFactory import VerseFactory
from Elisio.tests.Test_Verse import TYPICAL_VERSE
from Elisio.exceptions import HexameterException, VerseException

set_django()

from Elisio.models import DatabaseVerse, WordOccurrence

class TestHexameter(unittest.TestCase):
    """ testing specifically for the hexameter """
    def construct_hexameter(self, text=TYPICAL_VERSE):
        """ Construct a Hexameter object from a given text """
        constructed_verse = VerseFactory.create(text, classes=HexameterCreator)

        return constructed_verse

    def test_hexameter_construct(self):
        """ constructing a Hexameter must work """
        self.assertTrue(isinstance(self.construct_hexameter(), Verse))
        self.assertTrue(isinstance(self.construct_hexameter(), Hexameter))

    def test_hexameter_scan_basic_case(self):
        """ Aen. 1, 1 must scan correctly imo """
        expected_feet = [Foot.DACTYLUS, Foot.DACTYLUS,
                         Foot.SPONDAEUS, Foot.SPONDAEUS,
                         Foot.DACTYLUS, Foot.SPONDAEUS]
        verse = self.construct_hexameter()
        self.assertEqual(verse.feet, expected_feet)

    def test_hexameter_scan_all(self):
        """ frivolous check to see how many verses work """
        save = WordOccurrence.objects.count() > 0
        threshold = 14 if save else 12
        dbverses = DatabaseVerse.objects.all()
        worked = 0
        failed = 0
        for dbverse in dbverses:
            verse_saved = dbverse.saved
            try:
                verse = VerseFactory.create(dbverse.contents, not dbverse.saved, False, dbverse, classes=HexameterCreator)
                dbverse.saved = True
                dbverse.structure = verse.structure
            except VerseException:
                try:
                    verse = VerseFactory.create(dbverse.contents, not dbverse.saved, True, dbverse, classes=HexameterCreator)
                    dbverse.saved = True
                    dbverse.structure = verse.structure
                except VerseException as exc:
                    failed += 1
                    verse = VerseFactory.get_split_syllables(dbverse.contents)
                    dbverse.saved = False
                    try:
                        dbverse.failure = exc.exceptions[0][0].message[:69]
                    except IndexError:
                        dbverse.failure = exc.message[:69]
                    dbverse.structure = ""
                else:
                    worked += 1
            else:
                worked += 1
            if verse_saved != dbverse.saved or dbverse.failure:
                dbverse.save()
        # canary test: over 91% of verses must succeed
        result = str(worked) + " worked, " + str(failed) + " failed"
        if worked / failed < threshold:
            self.fail(result)
        # canary test: if no verses fail, then we are probably too lax
        elif failed == 0:
            self.fail("improbable result: " + result)
        else:
            print(result)

    def test_hexameter_scan_for_debug(self):
        """
        21: hinc populum late regem belloque superbum
        """
        dbverse = DatabaseVerse.objects.get(pk=128)
        verse = VerseFactory.create(dbverse.contents, False, True, classes=HexameterCreator)

    def test_hexameter_structure(self):
        lst = [Weight.HEAVY, Weight.LIGHT, Weight.LIGHT,
                         Weight.HEAVY, Weight.LIGHT, Weight.LIGHT,
                         Weight.HEAVY, Weight.LIGHT, Weight.LIGHT,
                         Weight.HEAVY, Weight.LIGHT, Weight.LIGHT,
                         Weight.HEAVY, Weight.LIGHT, Weight.LIGHT,
                         Weight.HEAVY, Weight.LIGHT]
        hex_creator = HexameterCreator(lst)
        hex_class = hex_creator.get_subtype()
        hex = hex_class('')
        hex.flat_list = lst
        hex.parse()
