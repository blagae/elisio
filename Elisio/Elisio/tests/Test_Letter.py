""" test module for class Letter """
import unittest
from Elisio.engine.wordProcessor import Letter
from Elisio.exceptions import ScansionException

class TestLetter(unittest.TestCase):
    """ test class for Letter """
    def construct_letter(self, letter):
        """ Construct a letter object from a given text """
        constructed_letter = Letter(letter)
        return constructed_letter

    def test_letter_construct(self):
        """ normal construct works """
        self.assertTrue(isinstance(self.construct_letter('a'), Letter))

    def test_letter_fail_too_long(self):
        """ argument must be 1 character """
        with self.assertRaises(ScansionException):
            self.construct_letter('aa')

    def test_letter_fail_too_short(self):
        """ argument must have content """
        with self.assertRaises(ScansionException):
            self.construct_letter('')

    def test_letter_fail_nonexist_W(self):
        """ W is an invalid letter """
        with self.assertRaises(ScansionException):
            self.construct_letter('W')

    def test_letter_fail_nonexistent(self):
        """ w is an invalid letter """
        with self.assertRaises(ScansionException):
            self.construct_letter('w')

    def test_letter_fail_space(self):
        """ space is not a letter """
        with self.assertRaises(ScansionException):
            self.construct_letter(' ')

    def test_letter_fail_non_alpha(self):
        """ letters are in [a-zA-Z] """
        with self.assertRaises(ScansionException):
            self.construct_letter(',')

    def test_letter_equal(self):
        """ a letter is equal to itself """
        letter1 = self.construct_letter('a')
        letter2 = self.construct_letter('a')
        self.assertEqual(letter1, letter2)

    def test_letter_not_equal(self):
        """ sanity check for false positives """
        letter1 = self.construct_letter('a')
        letter2 = self.construct_letter('c')
        self.assertNotEqual(letter1, letter2)

    def test_letter_equal_case_insens(self):
        """ letters are case insensitive """
        letter1 = self.construct_letter('a')
        letter2 = self.construct_letter('A')
        self.assertEqual(letter1, letter2)

    def test_letter_is_valid(self):
        """ tautological test ? """
        for letter in Letter.letters:
            obj = Letter(letter)
            self.assertTrue(obj.is_valid_letter())

    def test_letter_v_is_valid(self):
        """ v is a valid letter """
        obj = Letter('v')
        self.assertTrue(obj.is_valid_letter())

    def test_letter_j_is_valid(self):
        """ j is a valid letter """
        obj = Letter('J')
        self.assertTrue(obj.is_valid_letter())

if __name__ == '__main__':
    unittest.main()
