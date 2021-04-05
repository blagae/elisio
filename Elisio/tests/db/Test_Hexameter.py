import unittest

from elisio.engine.VerseFactory import VerseFactory
from elisio.engine.verse.VerseType import VerseType
from elisio.util.utils import set_django

set_django()

from elisio.util.batchutils import scan_verses
from elisio.engine.bridge.DatabaseBridge import DatabaseBridge
from elisio.models.metadata import DatabaseVerse
from elisio.models.scan import WordOccurrence


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
        dbverse = DatabaseVerse.objects.get(pk=3306)
        VerseFactory.create(dbverse, DatabaseBridge(), classes=VerseType.HEXAMETER)
