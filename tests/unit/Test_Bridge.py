import unittest

from elisio.bridge import Bridge
from elisio.exceptions import SyllableException
from elisio.syllable import Syllable
from elisio.word import Word


deviant_result = [Syllable("a"), Syllable("mat")]


class LocalDeviantBridge(Bridge):
    def split_from_deviant_word(self, lexeme: str) -> list[Syllable]:
        return deviant_result


class TestBridgeDeviant(unittest.TestCase):

    def test_bridge_deviant_full(self):
        word = Word("amat")
        word.split(LocalDeviantBridge())
        self.assertEqual(word.syllables, deviant_result)

    def test_bridge_deviant_partial(self):
        word = Word("amaturus")
        word.split(LocalDeviantBridge())
        self.assertEqual(word.syllables, deviant_result + [Syllable("u"), Syllable("rus")])

    def test_bridge_deviant_fail(self):
        result = [Syllable("a"), Syllable("mat")]
        word = Word("amatss")
        with self.assertRaises(SyllableException):
            word.split(LocalDeviantBridge())
