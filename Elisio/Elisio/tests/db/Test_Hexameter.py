import unittest

from Elisio.engine.VerseFactory import VerseFactory
from Elisio.engine.verse.VerseType import VerseType
from Elisio.utils import set_django

set_django()

from Elisio.batchjob import scan_verses
from Elisio.engine.bridge.DatabaseBridge import DatabaseBridge
from Elisio.models.metadata import DatabaseVerse
from Elisio.models.scan import WordOccurrence


class TestHexameter(unittest.TestCase):

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
