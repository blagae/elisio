import unittest

from Elisio.utils import set_django
set_django()

from Elisio.batchjob import scan_verses
from Elisio.engine.Verse import Verse, Foot
from Elisio.engine.Hexameter import Hexameter
from Elisio.engine.VerseType import VerseType
from Elisio.engine.VerseFactory import VerseFactory
from Elisio.tests.db.Test_Verse import TYPICAL_VERSE

from Elisio.engine.bridge.DatabaseBridge import DatabaseBridge

from Elisio.models.metadata import DatabaseVerse
from Elisio.models.scan import WordOccurrence


class TestHexameter(unittest.TestCase):
    """ testing specifically for the hexameter """
    @staticmethod
    def construct_hexameter(text=TYPICAL_VERSE):
        """ Construct a Hexameter object from a given text """
        constructed_verse = VerseFactory.create(text, classes=VerseType.HEXAMETER)
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
        verses = DatabaseVerse.objects.all()
        # verses = DatabaseVerse.objects.filter(id__lte=500)
        worked, failed, worked_wo_dict = scan_verses(verses, "test_hexameter_scan_all")
        # canary test: over 91% of verses must succeed
        result = str(worked_wo_dict) + " worked without dict, " + str(worked) + " worked, " + str(failed) + " failed"
        if worked / failed < threshold:
            self.fail(result)
        # canary test: if no verses fail, then we are probably too lax
        elif failed == 0:
            self.fail("improbable result: " + result)
        else:
            print(result)

    def test_hexameter_scan_for_debug(self):
        """
        12811: nascetur pulchra Troianus origine Caesar,
        """
        dbverse = DatabaseVerse.objects.get(pk=12811)
        VerseFactory.create(dbverse, DatabaseBridge(), classes=VerseType.HEXAMETER)
