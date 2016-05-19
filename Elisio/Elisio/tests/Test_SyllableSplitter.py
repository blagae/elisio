import unittest
from Elisio.engine.Syllable import SyllableSplitter, Syllable, SoundFactory

class Test_SyllableSplitter(unittest.TestCase):
    
    def test_syllsplit_basic(self):
        txt = SoundFactory.find_sounds_for_text('athos')
        syll = SyllableSplitter.join_into_syllables(txt)
        expected = []
        expected.append(Syllable('ath'))
        expected.append(Syllable('os'))
        self.assertEquals(syll, expected)
        syll = SyllableSplitter.redistribute(syll)
        expected = []
        expected.append(Syllable('a'))
        expected.append(Syllable('thos'))
        self.assertEquals(syll, expected)

    def test_syllsplit_enclitic(self):
        txt = SoundFactory.find_sounds_for_text('athosve')
        syll = SyllableSplitter.join_into_syllables(txt)
        expected = []
        expected.append(Syllable('ath'))
        expected.append(Syllable('os'))
        expected.append(Syllable('ve'))
        self.assertEquals(syll, expected)
        syll = SyllableSplitter.redistribute(syll)
        expected = []
        expected.append(Syllable('a'))
        expected.append(Syllable('thos'))
        expected.append(Syllable('ve'))
        self.assertEquals(syll, expected)
