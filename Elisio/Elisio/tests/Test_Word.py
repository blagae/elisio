""" unit tests for Word """

import unittest
from Elisio.engine.Verse import Weight
from Elisio.utils import set_django
from Elisio.engine.Syllable import Syllable
from Elisio.engine.Word import Word
from Elisio.exceptions import WordException

TYPICAL_WORD = "recentia"
SYLLABLES = ['re', 'cen', 'ti', 'a']
EXPECTED_SYLLABLE_LIST = []
EXPECTED_WEIGHTS = [Weight.ANCEPS, Weight.HEAVY,
                    Weight.LIGHT, Weight.ANCEPS]

for syllable in SYLLABLES:
    EXPECTED_SYLLABLE_LIST.append(Syllable(syllable))

class TestWord(unittest.TestCase):
    """ class for integration tests of Word """
    @classmethod
    def setUpClass(cls):
        """ we need django for this class """
        set_django()

    def construct_word(self, word=TYPICAL_WORD):
        """ Construct a word object from a given text """
        constructed_word = Word(word)
        return constructed_word

    def test_word_construct(self):
        """ typical word """
        self.assertTrue(isinstance(self.construct_word(), Word))
        
    def test_word_fail_object(self):
        """ incorrect input breaks word """
        with self.assertRaises(WordException):
            self.construct_word(7)

    def test_word_fail_space(self):
        """ incorrect input breaks word """
        with self.assertRaises(WordException):
            self.construct_word("multum ille")

    def test_word_equal(self):
        """ equality operator"""
        word1 = self.construct_word()
        word2 = self.construct_word()
        self.assertEqual(word1, word2)

    def test_word_equal_case_insens(self):
        """ equality operator"""
        word1 = self.construct_word(TYPICAL_WORD.lower())
        word2 = self.construct_word(TYPICAL_WORD.upper())
        self.assertEqual(word1, word2)

    def test_word_fail_initial_space(self):
        """ incorrect character breaks word """
        with self.assertRaises(WordException):
            self.construct_word(' '.join(TYPICAL_WORD))

    def test_word_fail_final_space(self):
        """ incorrect character breaks word """
        with self.assertRaises(WordException):
            self.construct_word(TYPICAL_WORD.join(' '))

    def test_word_fail_internal_space(self):
        """ incorrect character breaks word """
        with self.assertRaises(WordException):
            self.construct_word(TYPICAL_WORD.replace(TYPICAL_WORD[4], ' '))

    def test_word_fail_non_alpha(self):
        """ incorrect character breaks word """
        with self.assertRaises(WordException):
            self.construct_word(TYPICAL_WORD.replace(TYPICAL_WORD[5], '%'))

    def test_word_split_regular(self):
        """ archetypical word is split correctly """
        word = self.construct_word()
        word.split()
        self.assertEqual(word.syllables, EXPECTED_SYLLABLE_LIST)
        
    def test_word_create_deviant(self):
        word = self.construct_word('lavinia')
        word.split()
        expected = []
        expected.append(Syllable('la'))
        expected.append(Syllable('vin'))
        expected.append(Syllable('ia'))
        self.assertEqual(word.syllables, expected)

    def test_word_create_deviant_smvl(self):
        word = self.construct_word('lauinja')
        word.split()
        expected = []
        expected.append(Syllable('la'))
        expected.append(Syllable('vin'))
        expected.append(Syllable('ia'))
        self.assertEqual(word.syllables, expected)

    def test_word_has_enclitic(self):
        word1 = self.construct_word()
        self.assertFalse(word1.ends_in_enclitic())
        word2 = self.construct_word(TYPICAL_WORD + 've')
        self.assertTrue(word2.ends_in_enclitic())
        self.assertEqual(word1.without_enclitic(), word2.without_enclitic())

    def test_word_scan_regular(self):
        """ archetypical word is scanned correctly """
        word = self.construct_word()
        word.split()
        self.assertEqual(word.get_syllable_structure(), EXPECTED_WEIGHTS)

    def test_word_scan_closed_semivwl(self):
        """ semivowel is correctly scanned as vocalic """
        word = self.construct_word('iurgus')
        weights = [Weight.HEAVY, Weight.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_split_closed_semivwl(self):
        """ semivowel is correctly scanned as vocalic """
        word = self.construct_word('iurgus')
        syllable_list = [Syllable('iur'), Syllable('gus')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_split_initial_cluster(self):
        """ clusters are not a problem """
        word = self.construct_word('sphrostrurbs')
        syllable_list = [Syllable('sphros'), Syllable('trurbs', False)]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_scan_initial_clusters(self):
        """ clusters are not a problem """
        word = self.construct_word('sphrostrurbs')
        weights = [Weight.HEAVY, Weight.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_split_open_semivwl(self):
        """ initial semivowel is correctly (not) split """
        word = self.construct_word('imus')
        syllable_list = [Syllable('i'), Syllable('mus')]
        word.split()
        self.assertEqual(word.syllables, syllable_list, word.syllables)

    def test_word_scan_open_semivwl(self):
        """ initial semivowel is correctly scanned """
        word = self.construct_word('imus')
        weights = [Weight.ANCEPS, Weight.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_split_initial_semivwl(self):
        """ initial semivowel is correctly (not) split """
        word = self.construct_word('uilis')
        syllable_list = [Syllable('ui'), Syllable('lis')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_scan_init_semivwl(self):
        """ initial semivowel is correctly scanned as vocalic """
        word = self.construct_word('uilis')
        weights = [Weight.ANCEPS, Weight.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_split_short_semivwl(self):
        """ semivowel is correctly scanned as vocalic """
        word = self.construct_word('pius')
        syllable_list = [Syllable('pi'), Syllable('us')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_scan_short_semivwl(self):
        """ semivowel is also light when corripitur """
        word = self.construct_word('pius')
        weights = [Weight.LIGHT, Weight.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_split_geminate(self):
        """ common word must be in the dictionary """
        word = self.construct_word('eius')
        syllable_list = [Syllable('e'), Syllable('ius')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_split_geminate_two(self):
        """ common word must be in the dictionary """
        word = self.construct_word('cuius')
        syllable_list = [Syllable('cu'), Syllable('ius')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)
        
    def test_word_split_intervoc_v(self):
        word = self.construct_word('achivis')
        syllable_list = [Syllable('a'), Syllable('chi'), Syllable('vis')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_split_velivolum(self):
        word = self.construct_word('velivolum')
        syllable_list = [Syllable('ve'), Syllable('li'), Syllable('vo'), Syllable('lum')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_split_iit(self):
        word = self.construct_word('iit')
        syllable_list = [Syllable('i'), Syllable('it')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_split_lexical(self):
        """ common word must be in the dictionary """
        word = self.construct_word('cui')
        syllable_list = [Syllable('cui', False)]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_split_lexical_exc(self):
        """ common word must be in the dictionary """
        word = self.construct_word('huic')
        syllable_list = [Syllable('huic', False)]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_split_weird_word(self):
        """ common name must be in the dictionary """
        word = self.construct_word('troiae')
        syllable_list = [Syllable('tro'), Syllable('iae')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_scan_weird_word(self):
        """ common name must be in the dictionary """
        word = self.construct_word('troiae')
        weights = [Weight.HEAVY, Weight.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)
        
    def test_word_split_no_lexical_exc(self):
        """ diphthong way too rare for a rule """
        word = self.construct_word('prout')
        syllable_list = [Syllable('pro'), Syllable('ut')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_split_semiv_diphthong(self):
        """ diphthong must not be split """
        word = self.construct_word('novae')
        syllable_list = [Syllable('no'), Syllable('vae')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_split_same_vowels(self):
        """ semivowels should be analyzed correctly """
        word = self.construct_word('mortuus')
        syllable_list = [Syllable('mor'), Syllable('tu'), Syllable('us')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_scan_same_vowels(self):
        """ semivowels should be analyzed correctly """
        word = self.construct_word('mortuus')
        weights = [Weight.HEAVY, Weight.LIGHT, Weight.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_split_q(self):
        """ Q is always followed by inconsequential u """
        word = self.construct_word('antiquus')
        syllable_list = [Syllable('an'), Syllable('ti'), Syllable('quus')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_scan_q(self):
        """ Q is always followed by inconsequential u """
        word = self.construct_word('antiquus')
        weights = [Weight.HEAVY, Weight.ANCEPS, Weight.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_split_h(self):
        """ H has no impact on splitting """
        word = self.construct_word('pathos')
        syllable_list = [Syllable('pa'), Syllable('thos')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_scan_anceps_h(self):
        """ H has no impact """
        word = self.construct_word('pathos')
        weights = [Weight.ANCEPS, Weight.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_split_multiconsonant(self):
        """ several final consonants do not invalidate a syllable """
        word = self.construct_word('Urbs')
        syllable_list = [Syllable('urbs', False)]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_split_muta_cum_liquid(self):
        """ muta cum liquida does not have impact """
        word = self.construct_word('patris')
        syllable_list = [Syllable('pa'), Syllable('tris')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_scan_muta_cum_liquid(self):
        """ muta cum liquida does not have impact """
        word = self.construct_word('patris')
        weights = [Weight.ANCEPS, Weight.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_split_enclitic(self):
        """ enclitic -ve must always be monosyllabic """
        word = self.construct_word('quidve')
        syllable_list = [Syllable('quid'), Syllable('ue')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_scan_semivwl_internal(self):
        """ intervocalic semivowel is light """
        word = self.construct_word('italiam')
        weights = [Weight.ANCEPS, Weight.ANCEPS, Weight.LIGHT, Weight.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_split_fake_diphthong(self):
        """ intervocalic semivowel takes precedence over diphthong """
        word = self.construct_word('lavus')
        syllable_list = [Syllable('la'), Syllable('vus')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_scan_fake_diphthong(self):
        """ intervocalic semivowel takes precedence over diphthong """
        word = self.construct_word('lavus')
        weights = [Weight.ANCEPS, Weight.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_split_intvoc_semivwl(self):
        """ intervocalic semivowel must be consonantal """
        word = self.construct_word('civis')
        syllable_list = [Syllable('ci'), Syllable('vis')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_scan_intvoc_semivwl(self):
        """ intervocalic semivowel must be consonantal """
        word = self.construct_word('civis')
        weights = [Weight.ANCEPS, Weight.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_split_identical_sound(self):
        """ check reworking of word-internal sounds """
        word = self.construct_word('memor')
        syllable_list = [Syllable('me'), Syllable('mor')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_scan_identical_sound(self):
        """ check reworking of word-internal sounds """
        word = self.construct_word('memor')
        weights = [Weight.ANCEPS, Weight.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_scan_h(self):
        """ H must have no impact on weights """
        word = self.construct_word('zephyrus')
        weights = [Weight.ANCEPS, Weight.ANCEPS, Weight.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_scan_internal_nh(self):
        word = self.construct_word('inhumati')
        weights = [Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS, Weight.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)


    def test_word_scan_weird_word_two(self):
        """ proper name scanning """
        word = self.construct_word('troas')
        weights = [Weight.HEAVY, Weight.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_scan_endvowel_closed(self):
        """ any closed final syllable is scanned as heavy in isolation """
        word = self.construct_word('uiles')
        weights = [Weight.ANCEPS, Weight.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_scan_shortened_h(self):
        """ H has no impact on vowel reduction """
        word = self.construct_word('maher')
        weights = [Weight.LIGHT, Weight.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_split_not_a_diphthong(self):
        """ make sure EU is not scanned as a diphthong """
        word = self.construct_word('deum')
        syllable_list = [Syllable('de'), Syllable('um')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_scan_not_a_diphthong(self):
        """ make sure EU is not scanned as a diphthong """
        word = self.construct_word('deum')
        weights = [Weight.LIGHT, Weight.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_split_monosyllabic(self):
        """ make sure initial semivowel is scanned correctly """
        word = self.construct_word('iam')
        syllable_list = [Syllable('iam')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_scan_monosyllabic(self):
        """ make sure initial semivowel is scanned correctly """
        word = self.construct_word('iam')
        weights = [Weight.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_split_gu(self):
        """ make sure internal GU is not analyzed as a syllable """
        word = self.construct_word('sanguine')
        syllable_list = [Syllable('san'), Syllable('gui'), Syllable('ne')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_scan_gu(self):
        """ make sure internal GU is not analyzed as a syllable """
        word = self.construct_word('sanguine')
        weights = [Weight.HEAVY, Weight.ANCEPS, Weight.ANCEPS]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_split_cons_sv(self):
        """ split words with internal consonantal semivowels """
        word = self.construct_word('volvere')
        syllable_list = [Syllable('vol'), Syllable('ve'), Syllable('re')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)
        
    def test_word_scan_cons_sv(self):
        """ scan words with internal consonantal semivowels """
        word = self.construct_word('volvere')
        weights = [Weight.HEAVY, Weight.ANCEPS, Weight.ANCEPS]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_scan_failing_sv(self):
        word = self.construct_word('arva')
        syllable_list = [Syllable('ar'), Syllable('va')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)
        
    def test_word_scan_debug(self):
        """ scan words with internal consonantal semivowels """
        word = self.construct_word('pinguis')
        weights = [Weight.HEAVY, Weight.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_scan_debug_more(self):
        """ scan words with internal consonantal semivowels """
        word = self.construct_word('profugus')
        weights = [Weight.ANCEPS, Weight.ANCEPS, Weight.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_scan_final_e(self):
        """ scan word with final -e as anceps """
        word = self.construct_word('late')
        weights = [Weight.ANCEPS, Weight.ANCEPS]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)
