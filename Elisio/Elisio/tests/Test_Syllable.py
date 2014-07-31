import unittest
from Elisio.engine import Syllable, Letter
from Elisio.exceptions import ScansionException

class Test_Syllable(unittest.TestCase):
    def constructSyllable(self, text):
        constructedSyllable = Syllable(text)
        return constructedSyllable
    
    def test_SyllableConstructInit(self):
        self.assertTrue(isinstance(self.constructSyllable('ti'), Syllable))

    def test_SyllableConstructFree(self):
        self.assertTrue(isinstance(self.constructSyllable('o'), Syllable))
        
    def test_SyllableConstructDiphthong(self):
        self.assertTrue(isinstance(self.constructSyllable('aen'), Syllable))
        
    def test_SyllableConstructSemivowel(self):
        self.assertTrue(isinstance(self.constructSyllable('iu'), Syllable))

    def test_SyllableConstructConsonantCluster(self):
        self.assertTrue(isinstance(self.constructSyllable('sphroc'), Syllable))

    def test_SyllableFailNonDiphthong(self):
        with self.assertRaises(ScansionException):
            self.constructSyllable('tia')

    def test_SyllableFailMultipleVowels(self):
        with self.assertRaises(ScansionException):
            self.constructSyllable('aeu')

    def test_SyllableFailMultipleSyll(self):
        with self.assertRaises(ScansionException):
            self.constructSyllable('inos')

if __name__ == '__main__':
    unittest.main()
