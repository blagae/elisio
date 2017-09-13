import unittest
from Elisio.engine.Syllable import SyllableSplitter, Syllable, SoundFactory


class TestSyllableSplitter(unittest.TestCase):
    
    def test_syllsplit_basic(self):
        txt = SoundFactory.find_sounds_for_text('athos')
        syll = SyllableSplitter.join_into_syllables(txt)
        expected = [Syllable('ath'), Syllable('os')]
        self.assertEqual(syll, expected)
        syll = SyllableSplitter.redistribute(syll)
        expected = [Syllable('a'), Syllable('thos')]
        self.assertEqual(syll, expected)

    def test_syllsplit_enclitic(self):
        txt = SoundFactory.find_sounds_for_text('athosve')
        syll = SyllableSplitter.join_into_syllables(txt)
        expected = [Syllable('ath'), Syllable('os'), Syllable('ve')]
        self.assertEqual(syll, expected)
        syll = SyllableSplitter.redistribute(syll)
        expected = [Syllable('a'), Syllable('thos'), Syllable('ve')]
        self.assertEqual(syll, expected)
