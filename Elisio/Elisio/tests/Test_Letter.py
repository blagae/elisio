import unittest
from Elisio.engine import Letter
from Elisio.exceptions import ScansionException

class Test_Letter(unittest.TestCase):

    def constructLetter(self, letter):
        """ Construct a letter object from a given text """
        constructedLetter = Letter(letter)
        return constructedLetter
    
    def test_LetterConstruct(self):
        self.assertTrue(isinstance(self.constructLetter('a'), Letter))
        
    def test_LetterFailTooLong(self):
        with self.assertRaises(ScansionException):
            self.constructLetter('aa')
            
    def test_LetterFailTooShort(self):
        with self.assertRaises(ScansionException):
            self.constructLetter('')
            
    def test_LetterFailNonExistentUpperCase(self):
        with self.assertRaises(ScansionException):
            self.constructLetter('W')

    def test_LetterFailNonExistent(self):
        with self.assertRaises(ScansionException):
            self.constructLetter('w')
            
    def test_LetterFailSpace(self):
        with self.assertRaises(ScansionException):
            self.constructLetter(' ')

    def test_LetterFailNonAlpha(self):
        with self.assertRaises(ScansionException):
            self.constructLetter(',')

    def test_LetterEqual(self):
        letter1 = self.constructLetter('a')
        letter2 = self.constructLetter('a')
        self.assertEqual(letter1, letter2)
        
    def test_LetterNotEqual(self):
        letter1 = self.constructLetter('a')
        letter2 = self.constructLetter('c')
        self.assertNotEqual(letter1, letter2)

    def test_LetterEqualCaseInsensitive(self):
        letter1 = self.constructLetter('a')
        letter2 = self.constructLetter('A')
        self.assertEqual(letter1, letter2)
        
    def test_LetterIsVowel(self):
        from Elisio.engine import vowels
        for vowel in vowels:
            letter = Letter(vowel)
            self.assertTrue(letter.isVowel())

    def test_LetterIsSemivowel(self):
        from Elisio.engine import semivowels
        for semivowel in semivowels:
            letter = Letter(semivowel)
            self.assertTrue(letter.isSemivowel())
            
    def test_LetterIsConsonant(self):
        from Elisio.engine import consonants
        for consonant in consonants:
            letter = Letter(consonant)
            self.assertTrue(letter.isConsonant())
            
    def test_LetterIsHeavyMaker(self):
        from Elisio.engine import heavyMakers
        for heavyMaker in heavyMakers:
            letter = Letter(heavyMaker)
            self.assertTrue(letter.isHeavyMaking())

    def test_LetterHeavyMakerIsConsonant(self):
        from Elisio.engine import heavyMakers
        for heavyMaker in heavyMakers:
            letter = Letter(heavyMaker)
            self.assertTrue(letter.isConsonant())

if __name__ == '__main__':
    unittest.main()
