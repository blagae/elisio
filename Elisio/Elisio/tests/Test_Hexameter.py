import unittest
from Elisio.engine.Verse import Verse, Foot, set_django
from Elisio.engine.Hexameter import Hexameter
from Elisio.tests.Test_Verse import TYPICAL_VERSE
from Elisio.exceptions import HexameterException, VerseException

set_django()

from Elisio.models import DatabaseVerse

class TestHexameter(unittest.TestCase):
    """ testing specifically for the hexameter """
    def construct_hexameter(self, text=TYPICAL_VERSE):
        """ Construct a Hexameter object from a given text """
        constructed_verse = Hexameter(text)

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
        verse.split()
        verse.scan()
        self.assertEqual(verse.feet, expected_feet)

    def test_hexameter_scan_all(self):
        """ frivolous check to see how many verses work """
        dbverses = DatabaseVerse.objects.all()
        worked = 0
        failed = 0
        for dbverse in dbverses:
            try:
                if dbverse.number == 18:
                    worked = worked # for debugging
                verse = Hexameter(dbverse.contents)
                verse.split()
                verse.scan()
            except VerseException as exc:
                failed += 1
                print("{3}({0}: {1}): {2}"
                      .format(dbverse.number, verse.get_split_syllables(), exc, type(exc)))
            else:
                worked += 1
        # canary test: over 66% of verses must succeed
        result = str(worked) + " worked, " + str(failed) + " failed"
        if worked / failed < 3:
            self.fail(result)
        else:
            print(result)
