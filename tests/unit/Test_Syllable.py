""" Test classes for Syllable """
import unittest

from elisio.exceptions import SyllableException
from elisio.sound import SoundFactory
from elisio.syllable import Syllable


class TestSyllable(unittest.TestCase):
    def test_syll_constr_init(self):
        """ regular syllable """
        self.assertTrue(isinstance(Syllable('ti'), Syllable))

    def test_syll_constr_final(self):
        """ regular syllable """
        self.assertTrue(isinstance(Syllable('it'), Syllable))

    def test_syll_constr_free(self):
        """ regular syllable """
        self.assertTrue(isinstance(Syllable('o'), Syllable))

    def test_syll_constr_free_diph(self):
        """ regular syllable """
        self.assertTrue(isinstance(Syllable('oe'), Syllable))

    def test_syll_constr_diph(self):
        """ regular syllable with diphthong """
        self.assertTrue(isinstance(Syllable('aen'), Syllable))

    def test_syll_constr_diph_final(self):
        """ regular syllable with diphthong """
        self.assertTrue(isinstance(Syllable('sau'), Syllable))

    def test_syll_constr_semivwl(self):
        """ regular syllable with initial semivowel """
        self.assertTrue(isinstance(Syllable('iu'), Syllable))

    def test_syll_constr_cons_cluster_h(self):
        """ regular syllable with initial consonant cluster """
        self.assertTrue(isinstance(Syllable('thy'), Syllable))

    def test_syll_constr_cons_init_h(self):
        """ regular syllable with initial consonant cluster """
        self.assertTrue(isinstance(Syllable('hos'), Syllable))

    def test_syll_constr_cons_init_mcl(self):
        """ regular syllable with initial consonant cluster """
        self.assertTrue(isinstance(Syllable('trux'), Syllable))

    def test_syll_constr_cons_init_clstr_diph(self):
        """ regular syllable with initial consonant cluster """
        self.assertTrue(isinstance(Syllable('sprau'), Syllable))

    def test_syll_constr_cons_full(self):
        """ regular syllable with initial consonant cluster """
        self.assertTrue(isinstance(Syllable('sphroc'), Syllable))
        self.assertTrue(isinstance(Syllable('urbs'), Syllable))

    def test_syll_constr_semiv(self):
        """ regular syllable with initial consonant cluster """
        self.assertTrue(isinstance(Syllable('vos'), Syllable))
        self.assertTrue(isinstance(Syllable('vis'), Syllable))
        self.assertTrue(isinstance(Syllable('uus'), Syllable))
        self.assertTrue(isinstance(Syllable('iam'), Syllable))

    def test_syll_constr_digraph(self):
        """ regular syllable with initial consonant cluster """
        self.assertTrue(isinstance(Syllable('qui'), Syllable))
        self.assertTrue(isinstance(Syllable('quod'), Syllable))
        self.assertTrue(isinstance(Syllable('quae'), Syllable))

    def test_syll_constr_heavymaker(self):
        """ regular syllable with initial consonant cluster """
        self.assertTrue(isinstance(Syllable('zeph'), Syllable))
        self.assertTrue(isinstance(Syllable('xoe'), Syllable))
        self.assertTrue(isinstance(Syllable('hux'), Syllable))

    def test_syll_constr_gu_vowel(self):
        """ regular syllable with initial consonant cluster """
        self.assertTrue(isinstance(Syllable('guis'), Syllable))
        self.assertTrue(isinstance(Syllable('gui'), Syllable))
        self.assertTrue(isinstance(Syllable('guo'), Syllable))

    def test_syll_constr_gu_cons(self):
        self.assertTrue(isinstance(Syllable('gus'), Syllable))

    def test_syll_fail_non_diph(self):
        """ this is not a single syllable """
        with self.assertRaises(SyllableException):
            Syllable('tia')

    def test_syll_fail_ii(self):
        """ this is not a single syllable """
        with self.assertRaises(SyllableException):
            Syllable('tii')

    def test_syll_fail_mult_vwl(self):
        """ this is not a single syllable """
        with self.assertRaises(SyllableException):
            Syllable('oa')

    def test_syll_fail_mult_vwl_diph(self):
        """ this is not a single syllable """
        with self.assertRaises(SyllableException):
            Syllable('aeu')

    def test_syll_fail_h_diph(self):
        """ this is not a single syllable """
        with self.assertRaises(SyllableException):
            Syllable('ahe')

    def test_syll_fail_mult_syll(self):
        """ this is not a single syllable """
        with self.assertRaises(SyllableException):
            Syllable('inos')

    def test_syll_fail_mult_syll_init(self):
        """ this is not a single syllable """
        with self.assertRaises(SyllableException):
            Syllable('sepa')

    def test_syll_fail_mult_ii(self):
        """ this is not a single syllable """
        with self.assertRaises(SyllableException):
            Syllable('iit')

    def test_syll_fail_mult_digraph(self):
        """ this is not a single syllable """
        with self.assertRaises(SyllableException):
            Syllable('quia')

    def test_syll_fail_mult_gui(self):
        """ this is not a single syllable """
        with self.assertRaises(SyllableException):
            Syllable('guia')

    def test_syll_fail_mult_syll_gui(self):
        """ this is not a single syllable """
        with self.assertRaises(SyllableException):
            Syllable('guisa')

    def test_syll_fail_only_cons_clstr(self):
        """ this is not a single syllable """
        with self.assertRaises(SyllableException):
            Syllable('lt')

    def test_syll_fail_only_cons(self):
        """ this is not a single syllable """
        with self.assertRaises(SyllableException):
            Syllable('b')

    def test_syll_fail_only_cons_h(self):
        """ this is not a single syllable """
        with self.assertRaises(SyllableException):
            Syllable('rh')

    def test_syll_fail_only_cons_digraph(self):
        """ this is not a single syllable """
        with self.assertRaises(SyllableException):
            Syllable('qu')

    def test_syll_fail_too_rare(self):
        """
        while it is technically possible to make this sound a diphthong,
        is exceedingly rare and must be seen as a lexical exception
        """
        with self.assertRaises(SyllableException):
            Syllable('prout')

    def test_syll_lexical_exception(self):
        """ ui is not usually a diphthong but it is attested in the forms
        cui and huic, which are consistently monosyllabic.
        these should be considered lexical exceptions
        this is not typical of the Syllable, so these syllables must fail
        """
        with self.assertRaises(SyllableException):
            Syllable('cui')

    def test_syll_equal(self):
        self.assertEqual(Syllable('aes'), Syllable('aes'))
        self.assertEqual(Syllable('quo'), Syllable('qvo'))
        self.assertEqual(Syllable('vjs'), Syllable('uis'))

    def test_syll_unequal(self):
        self.assertNotEqual(Syllable('ash'), Syllable('as'))
        self.assertNotEqual(Syllable('quo'), Syllable('qvu'))
        self.assertNotEqual(Syllable('tis'), Syllable('this'))

    def test_syll_ends_in_consonant(self):
        self.assertTrue(Syllable('ex').ends_with_consonant())
        self.assertTrue(Syllable('tum').ends_with_consonant())
        self.assertFalse(Syllable('tu').ends_with_consonant())
        self.assertFalse(Syllable('rau').ends_with_consonant())

    def test_syll_ends_in_vowel(self):
        self.assertFalse(Syllable('ex').ends_with_vowel())
        self.assertFalse(Syllable('tum').ends_with_vowel())
        self.assertTrue(Syllable('tu').ends_with_vowel())
        self.assertTrue(Syllable('rau').ends_with_vowel())

    def test_syll_elides(self):
        self.assertFalse(Syllable('ex').can_elide_if_final())
        self.assertFalse(Syllable('tus').can_elide_if_final())
        self.assertTrue(Syllable('tum').can_elide_if_final())
        self.assertTrue(Syllable('rau').can_elide_if_final())

    # not sure if testing the right things here !
    def test_syll_noninitial_starts_vowel(self):
        self.assertTrue(Syllable('a').starts_with_vowel(False))
        self.assertTrue(Syllable('ha').starts_with_vowel(False))
        self.assertTrue(Syllable('hu').starts_with_vowel(False))
        self.assertFalse(Syllable('hra').starts_with_vowel(False))

        self.assertTrue(Syllable('ius').starts_with_vowel(False))
        self.assertTrue(Syllable('i').starts_with_vowel(False))
        self.assertTrue(Syllable('ix').starts_with_vowel(False))
        self.assertTrue(Syllable('uos').starts_with_vowel(False))
        self.assertTrue(Syllable('vi').starts_with_vowel(False))

        self.assertFalse(Syllable('bo').starts_with_vowel(False))
        self.assertFalse(Syllable('tus').starts_with_vowel(False))
        self.assertFalse(Syllable('tum').starts_with_vowel(False))
        self.assertFalse(Syllable('rau').starts_with_vowel(False))

    # not sure if testing the right things here !
    def test_syll_initial_starts_vowel(self):
        self.assertTrue(Syllable('a').starts_with_vowel())
        self.assertTrue(Syllable('ha').starts_with_vowel())
        self.assertTrue(Syllable('hu').starts_with_vowel())
        self.assertFalse(Syllable('hra').starts_with_vowel())

        self.assertFalse(Syllable('ius').starts_with_vowel())
        self.assertTrue(Syllable('i').starts_with_vowel())
        self.assertTrue(Syllable('ix').starts_with_vowel())
        self.assertFalse(Syllable('uus').starts_with_vowel())
        self.assertFalse(Syllable('vi').starts_with_vowel())

        self.assertFalse(Syllable('bo').starts_with_vowel())
        self.assertFalse(Syllable('tus').starts_with_vowel())
        self.assertFalse(Syllable('tum').starts_with_vowel())
        self.assertFalse(Syllable('rau').starts_with_vowel())

    # not sure if testing the right things here !
    def test_syll_noninitial_starts_cons(self):
        self.assertFalse(Syllable('a').starts_with_consonant(False))
        self.assertFalse(Syllable('ha').starts_with_consonant(False))
        self.assertFalse(Syllable('hu').starts_with_consonant(False))
        self.assertTrue(Syllable('hra').starts_with_consonant(False))

        self.assertFalse(Syllable('ius').starts_with_consonant(False))
        self.assertFalse(Syllable('i').starts_with_consonant(False))
        self.assertFalse(Syllable('ix').starts_with_consonant(False))
        self.assertFalse(Syllable('uos').starts_with_consonant(False))
        self.assertFalse(Syllable('vi').starts_with_consonant(False))

        self.assertTrue(Syllable('bo').starts_with_consonant(False))
        self.assertTrue(Syllable('tus').starts_with_consonant(False))
        self.assertTrue(Syllable('tum').starts_with_consonant(False))
        self.assertTrue(Syllable('rau').starts_with_consonant(False))

    # not sure if testing the right things here !
    def test_syll_initial_starts_cons(self):
        self.assertFalse(Syllable('a').starts_with_consonant())
        self.assertFalse(Syllable('ha').starts_with_consonant())
        self.assertFalse(Syllable('hu').starts_with_consonant())
        self.assertTrue(Syllable('hra').starts_with_consonant())

        self.assertFalse(Syllable('i').starts_with_consonant())
        self.assertFalse(Syllable('ix').starts_with_consonant())
        self.assertTrue(Syllable('ius').starts_with_consonant())
        self.assertTrue(Syllable('uus').starts_with_consonant())
        self.assertTrue(Syllable('vi').starts_with_consonant())

        self.assertTrue(Syllable('bo').starts_with_consonant())
        self.assertTrue(Syllable('tus').starts_with_consonant())
        self.assertTrue(Syllable('tum').starts_with_consonant())
        self.assertTrue(Syllable('rau').starts_with_consonant())

    def test_syll_starts_cons_clst(self):
        self.assertTrue(Syllable('spi').starts_with_consonant_cluster())
        self.assertTrue(Syllable('xe').starts_with_consonant_cluster())
        self.assertTrue(Syllable('spru').starts_with_consonant_cluster())
        self.assertFalse(Syllable('pro').starts_with_consonant_cluster())
        self.assertFalse(Syllable('pa').starts_with_consonant_cluster())
        self.assertFalse(Syllable('pha').starts_with_consonant_cluster())
        self.assertFalse(Syllable('u').starts_with_consonant_cluster())

    def test_syll_makes_prev_heavy(self):
        self.assertTrue(Syllable('xe').makes_previous_heavy())
        self.assertFalse(Syllable('spre').makes_previous_heavy())
        self.assertFalse(Syllable('rau').makes_previous_heavy())

    def test_syll_get_vowel(self):
        self.assertEqual(Syllable('quu').get_vowel(), SoundFactory.create('u'))
        self.assertEqual(Syllable('io').get_vowel(), SoundFactory.create('o'))
        self.assertEqual(Syllable('sprau').get_vowel(), SoundFactory.create('au'))

    def test_syll_add_sound(self):
        syll = Syllable('tho')
        syll.add_sound(SoundFactory.create('c'))
        with self.assertRaises(SyllableException):
            syll.add_sound(SoundFactory.create('u'))

    def test_syll_get_vowel_loc_easy(self):
        self.assertEqual(Syllable('a').get_vowel_location(), 0)
        self.assertEqual(Syllable('am').get_vowel_location(), 0)
        self.assertEqual(Syllable('u').get_vowel_location(), 0)
        self.assertEqual(Syllable('um').get_vowel_location(), 0)
        self.assertEqual(Syllable('tu').get_vowel_location(), 1)
        self.assertEqual(Syllable('tum').get_vowel_location(), 1)

    def test_syll_get_vowel_loc_counterint(self):
        # s-pr-au
        self.assertEqual(Syllable('sprau').get_vowel_location(), 2)
        self.assertEqual(Syllable('spraux').get_vowel_location(), 2)
        # qu-a
        self.assertEqual(Syllable('qua').get_vowel_location(), 1)
        self.assertEqual(Syllable('quam').get_vowel_location(), 1)

    def test_syll_get_vowel_loc_svwl(self):
        self.assertEqual(Syllable('ua').get_vowel_location(), 1)
        self.assertEqual(Syllable('ui').get_vowel_location(), 1)
        self.assertEqual(Syllable('ia').get_vowel_location(), 1)
        self.assertEqual(Syllable('iu').get_vowel_location(), 1)
