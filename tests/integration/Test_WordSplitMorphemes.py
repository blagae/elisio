import unittest

from elisio.syllable import Weight
from elisio.word import split_morphemes, Word


class TestWordSplitMorphemes(unittest.TestCase):

    def test_undeclined_heavy(self):
        result = split_morphemes(Word("nunc"))
        self.assertEqual(1, len(result))
        self.assertEqual(result[0]["root"][0][1], [Weight.HEAVY])

    def test_undeclined_light(self):
        r = split_morphemes(Word("gradualiter"))
        self.assertEqual(1, len(r))
        # TODO word contact: last syllable should be anceps if followed by a word that starts with a consonant
        self.assertEqual(r[0]["root"][0][1], [Weight.ANCEPS, Weight.LIGHT, Weight.ANCEPS, Weight.ANCEPS, Weight.HEAVY])

    def test_declined_anceps(self):
        result = split_morphemes(Word("gravitati"))
        self.assertEqual(2, len(result))
        for struct in result:
            self.assertEqual(struct["root"][0][1], [Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS])
        for infl in struct["inflections"]:
            self.assertEqual(infl[1], [Weight.ANCEPS])

    def test_declined_heavy(self):
        result = split_morphemes(Word("gravitanti"))
        self.assertEqual(1, len(result))
        self.assertEqual(result[0]["root"][0][1], [Weight.ANCEPS, Weight.ANCEPS])
        for infl in result[0]["inflections"]:
            self.assertEqual(infl[1], [Weight.HEAVY, Weight.ANCEPS])

    def test_declined_heavy_final(self):
        result = split_morphemes(Word("monent"))
        self.assertEqual(1, len(result))
        self.assertEqual(result[0]["root"][0][1], [Weight.ANCEPS])
        for infl in result[0]["inflections"]:
            self.assertEqual(infl[1], [Weight.HEAVY])
