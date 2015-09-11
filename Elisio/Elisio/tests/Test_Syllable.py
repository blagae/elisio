""" Test classes for Syllable """
import unittest
from Elisio.engine.Syllable import Syllable
from Elisio.engine.Sound import SoundFactory
from Elisio.exceptions import SyllableException

class TestSyllable(unittest.TestCase):
    """ Test class for Syllable """
    def construct_syllable(self, text):
        """ convenience method """
        constructed_syllable = Syllable(text)
        return constructed_syllable
    
    def test_syll_constr_init(self):
        """ regular syllable """
        self.assertTrue(isinstance(self.construct_syllable('ti'), Syllable))
    def test_syll_constr_final(self):
        """ regular syllable """
        self.assertTrue(isinstance(self.construct_syllable('it'), Syllable))
        
    def test_syll_constr_free(self):
        """ regular syllable """
        self.assertTrue(isinstance(self.construct_syllable('o'), Syllable))

    def test_syll_constr_free_diph(self):
        """ regular syllable """
        self.assertTrue(isinstance(self.construct_syllable('oe'), Syllable))
        
    def test_syll_constr_diph(self):
        """ regular syllable with diphthong """
        self.assertTrue(isinstance(self.construct_syllable('aen'), Syllable))

    def test_syll_constr_diph_final(self):
        """ regular syllable with diphthong """
        self.assertTrue(isinstance(self.construct_syllable('sau'), Syllable))

    def test_syll_constr_semivwl(self):
        """ regular syllable with initial semivowel """
        self.assertTrue(isinstance(self.construct_syllable('iu'), Syllable))
        
    def test_syll_constr_cons_cluster_h(self):
        """ regular syllable with initial consonant cluster """
        self.assertTrue(isinstance(self.construct_syllable('thy'), Syllable))
        
    def test_syll_constr_cons_init_h(self):
        """ regular syllable with initial consonant cluster """
        self.assertTrue(isinstance(self.construct_syllable('hos'), Syllable))
        
    def test_syll_constr_cons_init_mcl(self):
        """ regular syllable with initial consonant cluster """
        self.assertTrue(isinstance(self.construct_syllable('trux'), Syllable))

    def test_syll_constr_cons_init_clstr_diph(self):
        """ regular syllable with initial consonant cluster """
        self.assertTrue(isinstance(self.construct_syllable('sprau'), Syllable))
        
    def test_syll_constr_cons_full(self):
        """ regular syllable with initial consonant cluster """
        self.assertTrue(isinstance(self.construct_syllable('sphroc'), Syllable))
        self.assertTrue(isinstance(self.construct_syllable('urbs'), Syllable))
        
    def test_syll_constr_semiv(self):
        """ regular syllable with initial consonant cluster """
        self.assertTrue(isinstance(self.construct_syllable('vos'), Syllable))
        self.assertTrue(isinstance(self.construct_syllable('vis'), Syllable))
        self.assertTrue(isinstance(self.construct_syllable('uus'), Syllable))
        self.assertTrue(isinstance(self.construct_syllable('iam'), Syllable))

    def test_syll_constr_digraph(self):
        """ regular syllable with initial consonant cluster """
        self.assertTrue(isinstance(self.construct_syllable('qui'), Syllable))
        self.assertTrue(isinstance(self.construct_syllable('quod'), Syllable))
        self.assertTrue(isinstance(self.construct_syllable('quae'), Syllable))
        
    def test_syll_constr_heavymaker(self):
        """ regular syllable with initial consonant cluster """
        self.assertTrue(isinstance(self.construct_syllable('zeph'), Syllable))
        self.assertTrue(isinstance(self.construct_syllable('xoe'), Syllable))
        self.assertTrue(isinstance(self.construct_syllable('hux'), Syllable))
        
    def test_syll_fail_non_diph(self):
        """ this is not a single syllable """
        with self.assertRaises(SyllableException):
            self.construct_syllable('tia')

    def test_syll_fail_mult_vwl(self):
        """ this is not a single syllable """
        with self.assertRaises(SyllableException):
            self.construct_syllable('oa')
            
    def test_syll_fail_mult_vwl_diph(self):
        """ this is not a single syllable """
        with self.assertRaises(SyllableException):
            self.construct_syllable('aeu')

    def test_syll_fail_h_diph(self):
        """ this is not a single syllable """
        with self.assertRaises(SyllableException):
            self.construct_syllable('ahe')
            
    def test_syll_fail_mult_syll(self):
        """ this is not a single syllable """
        with self.assertRaises(SyllableException):
            self.construct_syllable('inos')
            
    def test_syll_fail_mult_syll_init(self):
        """ this is not a single syllable """
        with self.assertRaises(SyllableException):
            self.construct_syllable('sepa')
    
    # TODO: fix incorrect success: there can be no syllable 'ji'
    def test_syll_fail_mult_ii(self):
        """ this is not a single syllable """
        with self.assertRaises(SyllableException):
            self.construct_syllable('iit')
            
    def test_syll_fail_mult_digraph(self):
        """ this is not a single syllable """
        with self.assertRaises(SyllableException):
            self.construct_syllable('quia')

    def test_syll_fail_only_cons_clstr(self):
        """ this is not a single syllable """
        with self.assertRaises(SyllableException):
            self.construct_syllable('lt')

    def test_syll_fail_only_cons(self):
        """ this is not a single syllable """
        with self.assertRaises(SyllableException):
            self.construct_syllable('b')
    def test_syll_fail_only_cons_h(self):
        """ this is not a single syllable """
        with self.assertRaises(SyllableException):
            self.construct_syllable('rh')
    def test_syll_fail_only_cons_digraph(self):
        """ this is not a single syllable """
        with self.assertRaises(SyllableException):
            self.construct_syllable('qu')

    def test_syll_fail_too_rare(self):
        """
        while it is technically possible to make this sound a diphthong,
        is exceedingly rare and must be seen as a lexical exception
        """
        with self.assertRaises(SyllableException):
            self.construct_syllable('prout')

    def test_syll_lexical_exception(self):
        """ ui is not usually a diphthong but it is attested in the forms
        cui and huic, which are consistently monosyllabic.
        these should be considered lexical exceptions
        this is not typical of the Syllable, so these syllables must fail
        """
        with self.assertRaises(SyllableException):
            self.construct_syllable('cui')


if __name__ == '__main__':
    unittest.main()
