""" test module for Sound """
import unittest
from Elisio.engine.Sound import SoundFactory


class TestSound(unittest.TestCase):
    """ test class for Sound """
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

    def test_sound_get_type_vw(self):
        sound = SoundFactory.create('y')
        self.assertTrue(sound.is_vowel())
        self.assertFalse(sound.is_diphthong())
        self.assertFalse(sound.is_semivowel())
        self.assertFalse(sound.is_consonant())
        self.assertFalse(sound.is_heavy_making())
        self.assertFalse(sound.is_h())

    def test_sound_get_type_di(self):
        sound = SoundFactory.create('oE')
        self.assertTrue(sound.is_vowel())
        self.assertTrue(sound.is_diphthong())
        self.assertFalse(sound.is_semivowel())
        self.assertFalse(sound.is_consonant())
        self.assertFalse(sound.is_heavy_making())
        self.assertFalse(sound.is_h())

    def test_sound_get_type_sv(self):
        sound = SoundFactory.create('i')
        self.assertFalse(sound.is_vowel())
        self.assertFalse(sound.is_diphthong())
        self.assertTrue(sound.is_semivowel())
        self.assertFalse(sound.is_consonant())
        self.assertFalse(sound.is_heavy_making())
        self.assertFalse(sound.is_h())

    def test_sound_get_type_cs(self):
        sound = SoundFactory.create('T')
        self.assertFalse(sound.is_vowel())
        self.assertFalse(sound.is_diphthong())
        self.assertFalse(sound.is_semivowel())
        self.assertTrue(sound.is_consonant())
        self.assertFalse(sound.is_heavy_making())
        self.assertFalse(sound.is_h())
        
    def test_sound_get_type_hm(self):
        sound = SoundFactory.create('x')
        self.assertFalse(sound.is_vowel())
        self.assertFalse(sound.is_diphthong())
        self.assertFalse(sound.is_semivowel())
        self.assertTrue(sound.is_consonant())
        self.assertTrue(sound.is_heavy_making())
        self.assertFalse(sound.is_h())

    def test_sound_get_type_h(self):
        sound = SoundFactory.create('h')
        self.assertFalse(sound.is_vowel())
        self.assertFalse(sound.is_diphthong())
        self.assertFalse(sound.is_semivowel())
        self.assertTrue(sound.is_consonant())
        self.assertFalse(sound.is_heavy_making())
        self.assertTrue(sound.is_h())
