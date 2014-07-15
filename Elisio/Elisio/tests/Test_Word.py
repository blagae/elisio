import unittest
from Elisio.models import Word, Syllable
from Elisio.exceptions import ScansionException

typical_word = "recentia"
syllables = ['re', 'cen', 'ti', 'a']
expected_syllable_list = []
for syllable in syllables:
    expected_syllable_list.append(Syllable(syllable))

class Test_Word(unittest.TestCase):
    def constructWord(self, word = typical_word):
        """ Construct a word object from a given text """
        constructedWord = Word(word)
        return constructedWord

    def test_constructWord(self):
        self.assertTrue(isinstance(self.constructWord(), Word))

    def test_eqWord(self):
        word1 = self.constructWord()
        word2 = self.constructWord()
        self.assertEqual(word1, word2)

    def test_splitWord(self):
        word = self.constructWord()
        word.split()
        self.assertEqual(word.syllables, expected_syllable_list)
        
    def test_failWordInitialSpace(self):
        with self.assertRaises(ScansionException):
            self.constructWord(' '.join(typical_word))
    
    def test_failWordFinalSpace(self):
        with self.assertRaises(ScansionException):
            self.constructWord(typical_word.join(' '))

    def test_failWordInternalSpace(self):
        with self.assertRaises(ScansionException):
            self.constructWord(typical_word.replace(typical_word[4], ' '))
        
    def test_failWordNonAlpha(self):
        with self.assertRaises(ScansionException):
            self.constructWord(typical_word.replace(typical_word[5], '%'))

if __name__ == '__main__':
    unittest.main()
