""" test module for Sound """
import unittest
from Elisio.engine.Letter import Letter, LetterType
from Elisio.engine.Sound import Sound, SoundFactory
from Elisio.exceptions import ScansionException

class TestSound(unittest.TestCase):
    """ test class for Sound """
    def construct_sound(self, *texts):
        """ convenience me  thod """
        letters = []
        for text in texts:
            letters.append(text)
        sound = SoundFactory.create(letters)
        return sound

    def test_sound_constr_regular(self):
        """ a valid Letter """
        self.assertTrue(isinstance(self.construct_sound('a'), Sound))

    def test_sound_constr_object(self):
        """ a valid Letter """
        self.assertTrue(isinstance(self.construct_sound(Letter('a')), Sound))

    def test_sound_constr_diph(self):
        """ a valid list of Letters """
        self.assertTrue(isinstance(self.construct_sound('a', 'e'), Sound))

    def test_sound_constr_diph_str(self):
        """ a valid list of Letters """
        self.assertTrue(isinstance(self.construct_sound('ae'), Sound))

    def test_sound_constr_diph_obj(self):
        """ a valid list of Letters """
        self.assertTrue(isinstance(
            self.construct_sound(Letter('a'), Letter('U')), Sound)
                       )

    def test_sound_constr_digraph(self):
        """ a valid list of Letters """
        self.assertTrue(isinstance(
            self.construct_sound(Letter('Q'), Letter('u')), Sound)
                       )

    def test_sound_fail_constr_illegal(self):
        """ not a valid list of Letters """
        with self.assertRaises(ScansionException):
            self.construct_sound('qi')

    def test_sound_fail_constr_length(self):
        """ not a valid list of Letters """
        with self.assertRaises(ScansionException):
            self.construct_sound(Letter('Q'), Letter('u'), Letter('o'))

    def test_sound_fail_constr_space(self):
        """ space is not a sound """
        with self.assertRaises(ScansionException):
            self.construct_sound(Letter(' '))

    def test_sound_constr_from_text(self):
        """ a regular sound should be created easily """
        sound = SoundFactory.create_sounds_from_text('A')
        self.assertTrue(isinstance(sound[0], Sound))
        self.assertEqual(len(sound), 1)

    def test_sound_fail_cstr_incl_space(self):
        """ a sound cannot contain spaces """
        with self.assertRaises(ScansionException):
            SoundFactory.create_sounds_from_text([' ', 'c'])

    def test_sound_fail_constr_too_rare(self):
        """ not a normally recognized diphthong """
        sound = SoundFactory.create_sounds_from_text('ui')
        self.assertEqual(sound[0], SoundFactory.create('u'))
        self.assertEqual(len(sound), 1)

    def test_sound_fail_constr_nonexist(self):
        """ creating sounds from text does not accept any input """
        sound = SoundFactory.create_sounds_from_text('ou')
        self.assertEqual(sound[0], SoundFactory.create('o'))
        self.assertEqual(len(sound), 1)

    def test_sound_equal(self):
        """ equality is on letter content """
        sound1 = SoundFactory.create('r')
        sound2 = SoundFactory.create('r')
        self.assertEqual(sound1, sound2)

    def test_sound_equal_case_insens(self):
        """ capitalization is wholly irrelevant """
        sound1 = SoundFactory.create('a')
        sound2 = SoundFactory.create('A')
        self.assertEqual(sound1, sound2)

    def test_sound_equal_u_v(self):
        """ semivowels have several graphemes """
        sound1 = SoundFactory.create('u')
        sound2 = SoundFactory.create('v')
        self.assertEqual(sound1, sound2)

    def test_sound_equal_i_j(self):
        """ semivowels have several graphemes """
        sound1 = SoundFactory.create('i')
        sound2 = SoundFactory.create('j')
        self.assertEqual(sound1, sound2)

if __name__ == '__main__':
    unittest.main()
