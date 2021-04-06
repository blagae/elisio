import unittest

from elisio.bridge.Bridge import LocalDictionaryBridge
from elisio.verse.Verse import Weight
from elisio.Word import Word


class TestWordOccurrence(unittest.TestCase):

    def test_se_dict_anceps(self):
        cache = {'se': ['3', '2']}
        word = Word("se")
        word.split(LocalDictionaryBridge(cache))
        weights = [Weight.HEAVY]
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_se_dict_elided(self):
        cache = {'se': ['0', '2']}
        word = Word("se")
        word.split(LocalDictionaryBridge(cache))
        weights = [Weight.HEAVY]
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_se_dict_heavy(self):
        cache = {'se': ['2']}
        word = Word("se")
        word.split(LocalDictionaryBridge(cache))
        weights = [Weight.HEAVY]
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_se_dict_order1(self):
        cache = {'se': ['2', '3']}
        word = Word("se")
        word.split(LocalDictionaryBridge(cache))
        weights = [Weight.HEAVY]
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_se_dict_order2(self):
        cache = {'se': ['3', '2']}
        word = Word("se")
        word.split(LocalDictionaryBridge(cache))
        weights = [Weight.HEAVY]
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_ait_dict(self):
        cache = {'ait': ['11', '13']}
        word = Word("ait")
        word.split(LocalDictionaryBridge(cache))
        weights = [Weight.LIGHT, Weight.LIGHT]
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_et_dict(self):
        cache = {'et': ['1', '3', '2']}
        word = Word("et")
        word.split(LocalDictionaryBridge(cache))
        weights = [Weight.ANCEPS]
        self.assertEqual(word.get_syllable_structure(), weights)
