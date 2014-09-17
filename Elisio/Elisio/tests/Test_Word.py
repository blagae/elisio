import unittest
from Elisio.engine.verseProcessor import Weights
from Elisio.engine.wordProcessor import Word, Syllable
from Elisio.exceptions import ScansionException

typical_word = "recentia"
syllables = ['re', 'cen', 'ti', 'a']
expected_syllable_list = []
expected_weights = [Weights.ANCEPS, Weights.HEAVY, Weights.LIGHT, Weights.ANCEPS]
for syllable in syllables:
    expected_syllable_list.append(Syllable(syllable))

class Test_word_(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        set_django()

    def construct_word_(self, word=typical_word):
        """ Construct a word object from a given text """
        constructed_word = Word(word)
        return constructed_word

    def test_word_Construct(self):
        self.assertTrue(isinstance(self.constructWord(), Word))

    def test_word_fail(self):
        with self.assertRaises(ScansionException):
            self.constructWord(7)

    def test_word_equal(self):
        word1 = self.constructWord()
        word2 = self.constructWord()
        self.assertEqual(word1, word2)

    def test_word_equal_case_insensitive(self):
        word1 = self.constructWord(typical_word.lower())
        word2 = self.constructWord(typical_word.upper())
        self.assertEqual(word1, word2)

    def test_word_fail_initial_space(self):
        with self.assertRaises(ScansionException):
            self.constructWord(' '.join(typical_word))

    def test_word_fail_final_space(self):
        with self.assertRaises(ScansionException):
            self.constructWord(typical_word.join(' '))

    def test_word_fail_internal_space(self):
        with self.assertRaises(ScansionException):
            self.constructWord(typical_word.replace(typical_word[4], ' '))

    def test_word_fail_non_alpha(self):
        with self.assertRaises(ScansionException):
            self.constructWord(typical_word.replace(typical_word[5], '%'))

    def test_word_split_regular(self):
        word = self.constructWord()
        word.split()
        self.assertEqual(word.syllables, expected_syllable_list)

    def test_word_scan_regular(self):
        word = self.constructWord()
        word.split()
        self.assertEqual(word.get_syllable_structure(), expected_weights)

    def test_word_scan_closed_semivowels(self):
        word = self.constructWord('iurgus')
        weights = [Weights.HEAVY, Weights.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_split_closed_semivowels(self):
        word = self.constructWord('iurgus')
        syllable_list = [Syllable('iur'), Syllable('gus')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_split_initial_clusters(self):
        word = self.constructWord('sphrostrurbs')
        syllable_list = [Syllable('sphros'), Syllable('trurbs', False)]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_scan_initial_clusters(self):
        word = self.constructWord('sphrostrurbs')
        weights = [Weights.HEAVY, Weights.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_split_open_semivowels(self):
        word = self.constructWord('imus')
        syllable_list = [Syllable('i'), Syllable('mus')]
        word.split()
        self.assertEqual(word.syllables, syllable_list, word.syllables)

    def test_word_scan_open_semivowels(self):
        word = self.constructWord('imus')
        weights = [Weights.ANCEPS, Weights.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_split_initial_semivowels(self):
        word = self.constructWord('uilis')
        syllable_list = [Syllable('ui'), Syllable('lis')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_scan_initial_semivowels(self):
        word = self.constructWord('uilis')
        weights = [Weights.ANCEPS, Weights.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_split_shortened_semivowels(self):
        word = self.constructWord('pius')
        syllable_list = [Syllable('pi'), Syllable('us')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_scan_shortened_semivowels(self):
        word = self.constructWord('pius')
        weights = [Weights.LIGHT, Weights.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_split_geminate(self):
        word = self.constructWord('eius')
        syllable_list = [Syllable('e'), Syllable('ius')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_split_geminate_or_rare_diphthong(self):
        word = self.constructWord('cuius')
        syllable_list = [Syllable('cu'), Syllable('ius')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_split_lexical_exception(self):
        word = self.constructWord('cui')
        syllable_list = [Syllable('cui', False)]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_split_lexical_exception_bis(self):
        word = self.constructWord('huic')
        syllable_list = [Syllable('huic', False)]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_split_weird_word(self):
        word = self.constructWord('troiae')
        syllable_list = [Syllable('tro'), Syllable('iae')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_scan_weird_word(self):
        word = self.constructWord('troiae')
        weights = [Weights.HEAVY, Weights.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_split_no_lexical_exception(self):
        word = self.constructWord('prout')
        syllable_list = [Syllable('pro'), Syllable('ut')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_split_same_vowels(self):
        word = self.constructWord('mortuus')
        syllable_list = [Syllable('mor'), Syllable('tu'), Syllable('us')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_scan_same_vowels(self):
        word = self.constructWord('mortuus')
        weights = [Weights.HEAVY, Weights.LIGHT, Weights.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_split_with_q(self):
        word = self.constructWord('antiquus')
        syllable_list = [Syllable('an'), Syllable('ti'), Syllable('quus')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_scan_with_q(self):
        word = self.constructWord('antiquus')
        weights = [Weights.HEAVY, Weights.ANCEPS, Weights.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_split_with_h(self):
        word = self.constructWord('pathos')
        syllable_list = [Syllable('pa'), Syllable('thos')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_scan_anceps_h(self):
        word = self.constructWord('pathos')
        weights = [Weights.ANCEPS, Weights.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_split_lots_of_consonants(self):
        word = self.constructWord('Urbs')
        syllable_list = [Syllable('urbs', False)]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_split_with_muta_cum_liquida(self):
        word = self.constructWord('patris')
        syllable_list = [Syllable('pa'), Syllable('tris')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_scan_muta_cum_liquida_anceps(self):
        word = self.constructWord('patris')
        weights = [Weights.ANCEPS, Weights.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_split_with_enclitic(self):
        word = self.constructWord('quidve')
        syllable_list = [Syllable('quid'), Syllable('ue')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_scan_semivowel_internal(self):
        word = self.constructWord('italiam')
        weights = [Weights.ANCEPS, Weights.ANCEPS, Weights.LIGHT, Weights.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_split_semivowel_internal_fake_diphthong(self):
        word = self.constructWord('lavus')
        syllable_list = [Syllable('la'), Syllable('vus')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_scan__semivowel_internal_fake_diphthong(self):
        word = self.constructWord('lavus')
        weights = [Weights.ANCEPS, Weights.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_split__semivowel_internal_consonantal(self):
        word = self.constructWord('civis')
        syllable_list = [Syllable('ci'), Syllable('vis')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_scan__semivowel_internal_consonantal(self):
        word = self.constructWord('civis')
        weights = [Weights.ANCEPS, Weights.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_split_multiple_identical_sounds(self):
        word = self.constructWord('memor')
        syllable_list = [Syllable('me'), Syllable('mor')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_scan_multiple_identical_sounds(self):
        word = self.constructWord('memor')
        weights = [Weights.ANCEPS, Weights.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_scan_with_h(self):
        word = self.constructWord('zephyrus')
        weights = [Weights.ANCEPS, Weights.ANCEPS, Weights.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_scan_weird_word_two(self):
        word = self.constructWord('troas')
        weights = [Weights.HEAVY, Weights.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_scan_initial_short_end_vowel_closed(self):
        word = self.constructWord('uiles')
        weights = [Weights.ANCEPS, Weights.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_scan_shortened_h(self):
        word = self.constructWord('maher')
        weights = [Weights.LIGHT, Weights.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_split_not_a_diphthong(self):
        word = self.constructWord('deum')
        syllable_list = [Syllable('de'), Syllable('um')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_scan_not_a_diphthong(self):
        word = self.constructWord('deum')
        weights = [Weights.LIGHT, Weights.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_split_monosyllabic(self):
        word = self.constructWord('iam')
        syllable_list = [Syllable('iam')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_scan_monosyllabic(self):
        word = self.constructWord('iam')
        weights = [Weights.HEAVY]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_split_with_gu(self):
        word = self.constructWord('sanguine')
        syllable_list = [Syllable('san'), Syllable('gui'), Syllable('ne')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_scan_with_gu(self):
        word = self.constructWord('sanguine')
        weights = [Weights.HEAVY, Weights.ANCEPS, Weights.LIGHT]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

    def test_word_split_with_internal_consonantal_semivowel(self):
        word = self.constructWord('volvere')
        syllable_list = [Syllable('vol'), Syllable('ve'), Syllable('re')]
        word.split()
        self.assertEqual(word.syllables, syllable_list)

    def test_word_scan_with_internal_consonantal_semivowel(self):
        word = self.constructWord('volvere')
        weights = [Weights.HEAVY, Weights.ANCEPS, Weights.LIGHT]
        word.split()
        self.assertEqual(word.get_syllable_structure(), weights)

if __name__ == '__main__':
    unittest.main()
