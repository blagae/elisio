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

    # while it is technically possible to make this sound a diphthong,
    # is exceedingly rare and must be seen as a lexical exception
    def test_SyllableFailTooRare(self):
        with self.assertRaises(ScansionException):
            self.constructSyllable('prout')

    # ui is not usually a diphthong but it is attested in the forms cui and huic
    # which are consistently monosyllabic. these should be considered lexical exceptions
    # this is not typical of the Syllable, so these syllables must fail
    def test_SyllableLexicalException(self):
        with self.assertRaises(ScansionException):
            self.constructSyllable('cui')

if __name__ == '__main__':
    unittest.main()
