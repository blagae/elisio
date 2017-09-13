from django.test import TestCase
from Elisio.engine.Word import Word
from Elisio.engine.Verse import Weight
from Elisio.utils import set_django

set_django()

from Elisio.models import WordOccurrence


class TestWordOccurrence(TestCase):
    def test_se_dict_anceps(self):
        WordOccurrence.objects.create(word="se", struct="3")
        WordOccurrence.objects.create(word="se", struct="2")
        word = Word("se", True)
        word.split()
        weights = [Weight.HEAVY]
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_se_dict_elided(self):
        WordOccurrence.objects.create(word="se", struct="0")
        WordOccurrence.objects.create(word="se", struct="2")
        word = Word("se", True)
        word.split()
        weights = [Weight.HEAVY]
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_se_dict_heavy(self):
        WordOccurrence.objects.create(word="se", struct="2")
        word = Word("se", True)
        word.split()
        weights = [Weight.HEAVY]
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_se_dict_heavy(self):
        WordOccurrence.objects.create(word="se", struct="2")
        word = Word("se", True)
        word.split()
        weights = [Weight.HEAVY]
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_se_dict_order1(self):
        WordOccurrence.objects.create(word="se", struct="2")
        WordOccurrence.objects.create(word="se", struct="3")
        word = Word("se", True)
        word.split()
        weights = [Weight.HEAVY]
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_se_dict_order2(self):
        WordOccurrence.objects.create(word="se", struct="3")
        WordOccurrence.objects.create(word="se", struct="2")
        word = Word("se", True)
        word.split()
        weights = [Weight.HEAVY]
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_ait_dict(self):
        WordOccurrence.objects.create(word="ait", struct="11")
        WordOccurrence.objects.create(word="ait", struct="13")
        word = Word("ait", True)
        word.split()
        weights = [Weight.LIGHT, Weight.LIGHT]
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_et_dict(self):
        WordOccurrence.objects.create(word="et", struct="1")
        WordOccurrence.objects.create(word="et", struct="3")
        WordOccurrence.objects.create(word="et", struct="2")
        word = Word("et", True)
        word.split()
        weights = [Weight.ANCEPS]
        self.assertEqual(word.get_syllable_structure(), weights)
