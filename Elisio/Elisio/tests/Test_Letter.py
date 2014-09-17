import unittest
from Elisio.engine.wordProcessor import Letter
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
        
    def test_LetterIsValid(self):
        for letter in Letter.letters:
            obj = Letter(letter)
            self.assertTrue(obj.is_valid_letter())
            
    def test_LetterVIsValid(self):
        obj = Letter('v')
        self.assertTrue(obj.is_valid_letter())

    def test_LetterJIsValid(self):
        obj = Letter('J')
        self.assertTrue(obj.is_valid_letter())
            
if __name__ == '__main__':
    unittest.main()
