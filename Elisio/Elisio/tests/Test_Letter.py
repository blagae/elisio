""" test module for class Letter """
import unittest
from Elisio.engine.Letter import Letter
from Elisio.exceptions import *

class TestLetter(unittest.TestCase):

    """ test class for Letter """
    def construct_letter(self, letter):
        """ Construct a letter object from a given text """
        constructed_letter = Letter(letter)
        return constructed_letter

    # random sample of correct letters
    def test_letter_construct1(self):
        """ normal construct works """
        self.assertIsInstance(self.construct_letter('a'), Letter)
        
    def test_letter_construct2(self):
        """ normal construct works """
        self.assertTrue(isinstance(self.construct_letter('D'), Letter))

    def test_letter_construct3(self):
        """ normal construct works """
        self.assertTrue(isinstance(self.construct_letter('Q'), Letter))

    def test_letter_construct4(self):
        """ normal construct works """
        self.assertTrue(isinstance(self.construct_letter('r'), Letter))

    # explicitly added letter
    def test_letter_construct_e_trema1(self):
        # may fail, if incorrect encoding ?
        self.assertTrue(isinstance(self.construct_letter('ë'), Letter))

    def test_letter_construct_e_trema2(self):
        self.assertTrue(isinstance(self.construct_letter('\u00EB'), Letter))

    def test_letter_construct_e_trema3(self):
        # may fail, if incorrect encoding ?
        self.assertTrue(isinstance(self.construct_letter('Ë'), Letter))

    def test_letter_construct_e_trema4(self):
        self.assertTrue(isinstance(self.construct_letter('\u00CB'), Letter))

    # argument too long or too short
    def test_letter_fail_too_long(self):
        """ argument must be 1 character """
        with self.assertRaises(LetterException):
            self.construct_letter('aa')

    def test_letter_fail_too_short(self):
        """ argument must have content """
        with self.assertRaises(LetterException):
            self.construct_letter('')

    # illegal letter
    def test_letter_fail_nonexist_w(self):
        """ W is an invalid letter """
        with self.assertRaises(LetterException):
            self.construct_letter('W')

    def test_letter_fail_nonexistent(self):
        """ w is an invalid letter """
        with self.assertRaises(LetterException):
            self.construct_letter('w')
            
    # spaces and punctuation
    def test_letter_fail_space(self):
        """ space is not a letter """
        with self.assertRaises(LetterException):
            self.construct_letter(' ')

    def test_letter_fail_tab(self):
        """ space is not a letter """
        with self.assertRaises(LetterException):
            self.construct_letter('\t')

    def test_letter_fail_non_alpha(self):
        """ letters are in [a-zA-Z] """
        with self.assertRaises(LetterException):
            self.construct_letter(',')
            
    def test_letter_fail_non_alpha2(self):
        """ letters are in [a-zA-Z] """
        with self.assertRaises(LetterException):
            self.construct_letter('"')
            
    def test_letter_fail_non_alpha3(self):
        """ letters are in [a-zA-Z] """
        with self.assertRaises(LetterException):
            self.construct_letter('!')

    def test_letter_fail_non_alpha4(self):
        """ letters are in [a-zA-Z] """
        with self.assertRaises(LetterException):
            self.construct_letter('2')
            
    def test_letter_fail_non_alpha5(self):
        """ letters are in [a-zA-Z] """
        with self.assertRaises(LetterException):
            self.construct_letter(8)
            
    # letters with accents
    def test_letter_fail_accent(self):
        """ letters are in [a-zA-Z] """
        with self.assertRaises(LetterException):
            self.construct_letter('\u00E9')

            
    def test_letter_fail_other_writing1(self):
        # Greek letter
        with self.assertRaises(LetterException):
            self.construct_letter(u'?')
        # Greek letter
    def test_letter_fail_other_writing2(self):
        with self.assertRaises(LetterException):
            self.construct_letter(u'\u0391')
    def test_letter_fail_other_writing3(self):
        # Hindi letter
        with self.assertRaises(LetterException):
            self.construct_letter(u'\u0917')
    def test_letter_fail_other_writing4(self):
        # Arabic letter
        with self.assertRaises(LetterException):
            self.construct_letter(u'\u063A')

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

    def test_letter_equal_case_semivowel(self):
        """ i == j """
        letter1 = self.construct_letter('J')
        letter2 = self.construct_letter('i')
        self.assertEqual(letter1, letter2)

    def test_letter_j_transformed(self):
        """ j == i """
        letter = self.construct_letter('j')
        self.assertEqual(letter.letter, 'i')

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
