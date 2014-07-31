import unittest
from Elisio.engine import Word, Syllable, WEIGHTS
from Elisio.exceptions import ScansionException

typical_word = "recentia"
syllables = ['re', 'cen', 'ti', 'a']
expected_syllable_list = []
expected_weights = [WEIGHTS.Anceps, WEIGHTS.Heavy, WEIGHTS.Light, WEIGHTS.Light]
for syllable in syllables:
    expected_syllable_list.append(Syllable(syllable))

class Test_Word(unittest.TestCase):

    def constructWord(self, word = typical_word):
        """ Construct a word object from a given text """
        constructedWord = Word(word)
        return constructedWord

    def test_WordConstruct(self):
        self.assertTrue(isinstance(self.constructWord(), Word))

    def test_WordFail(self):
        with self.assertRaises(ScansionException):
            self.constructWord(7)

    def test_WordEqual(self):
        word1 = self.constructWord()
        word2 = self.constructWord()
        self.assertEqual(word1, word2)

    def test_WordEqualCaseInsensitive(self):
        word1 = self.constructWord(typical_word.lower())
        word2 = self.constructWord(typical_word.upper())
        self.assertEqual(word1, word2)

    def test_WordFailInitialSpace(self):
        with self.assertRaises(ScansionException):
            self.constructWord(' '.join(typical_word))

    def test_WordFailFinalSpace(self):
        with self.assertRaises(ScansionException):
            self.constructWord(typical_word.join(' '))

    def test_WordFailInternalSpace(self):
        with self.assertRaises(ScansionException):
            self.constructWord(typical_word.replace(typical_word[4], ' '))

    def test_WordFailNonAlpha(self):
        with self.assertRaises(ScansionException):
            self.constructWord(typical_word.replace(typical_word[5], '%'))

    def test_WordSplitRegular(self):
        word = self.constructWord()
        word.split()
        self.assertEqual(word.syllables, expected_syllable_list)
        
    def test_WordSplitClosedSemivowels(self):
        word = self.constructWord('iurgus')
        syllable_list = [Syllable('iur'), Syllable('gus')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)
        
    def test_WordSplitInitialClusters(self):
        word = self.constructWord('sphrostrum')
        syllable_list = [Syllable('sphros'), Syllable('trum')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)
    
    def test_WordSplitOpenSemivowels(self):
        word = self.constructWord('imus')
        syllable_list = [Syllable('i'), Syllable('mus')]
        word.split()
        self.assertEqual(word.syllables, syllable_list, word.syllables)
        
    def test_WordSplitInitialSemivowels(self):
        word = self.constructWord('uilis')
        syllable_list = [Syllable('vi'), Syllable('lis')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_WordSplitShortenedSemivowels(self):
        word = self.constructWord('pius')
        syllable_list = [Syllable('pi'), Syllable('us')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)
    
    def test_WordSplitGeminateOrDiphthong(self):
        word = self.constructWord('eius')
        syllable_list = [Syllable('ei'), Syllable('us')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)
        
    def test_WordSplitGeminateOrRareDiphthong(self):
        word = self.constructWord('cuius')
        syllable_list = [Syllable('cui'), Syllable('us')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)
        
    def test_WordSplitSamevowels(self):
        word = self.constructWord('mortuus')
        syllable_list = [Syllable('mor'), Syllable('tu'), Syllable('us')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_WordSplitWithQ(self):
        word = self.constructWord('antiquus')
        syllable_list = [Syllable('an'), Syllable('ti'), Syllable('quus')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)
        
    def test_WordScansion(self):
        word = self.constructWord()
        word.split()
        self.assertEqual(word.getSyllableStructure(), expected_weights)

    def test_WordScansionClosedSemivowels(self):
        word = self.constructWord('iurgus')
        weights = [WEIGHTS.Heavy, WEIGHTS.Heavy]
        word.split()
        self.assertEqual(word.getSyllableStructure(), weights)
        
    def test_WordScansionInitialClusters(self):
        word = self.constructWord('sphrostrum')
        weights = [WEIGHTS.Heavy, WEIGHTS.Heavy]
        word.split()
        self.assertEqual(word.getSyllableStructure(), weights)
    
    def test_WordScansionOpenSemivowels(self):
        word = self.constructWord('imus')
        weights = [WEIGHTS.Anceps, WEIGHTS.Heavy]
        word.split()
        self.assertEqual(word.getSyllableStructure(), weights)
        
    def test_WordScansionInitialSemivowels(self):
        word = self.constructWord('uilis')
        weights = [WEIGHTS.Anceps, WEIGHTS.Heavy]
        word.split()
        self.assertEqual(word.getSyllableStructure(), weights)

    def test_WordScansionShortenedSemivowels(self):
        word = self.constructWord('pius')
        weights = [WEIGHTS.Light, WEIGHTS.Heavy]
        word.split()
        self.assertEqual(word.getSyllableStructure(), weights)

    def test_WordScansionSamevowels(self):
        word = self.constructWord('mortuus')
        weights = [WEIGHTS.Heavy, WEIGHTS.Light, WEIGHTS.Heavy]
        word.split()
        self.assertEqual(word.getSyllableStructure(), weights)

    def test_WordScansionWithQ(self):
        word = self.constructWord('antiquus')
        weights = [WEIGHTS.Heavy, WEIGHTS.Anceps, WEIGHTS.Heavy]
        word.split()
        self.assertEqual(word.getSyllableStructure(), weights)
        
    

if __name__ == '__main__':
    unittest.main()
