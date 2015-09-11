import unittest
from Elisio.engine.Letter import Letter, LetterType
from Elisio.engine.Sound import *
from Elisio.exceptions import SoundException, LetterException

class TestSoundFactory(unittest.TestCase):
    def construct_sound(self, *texts):
        """ convenience method """
        letters = []
        for text in texts:
            letters.append(text)
        sound = SoundFactory.create(letters)
        return sound

    def test_sound_constr_regular(self):
        """ a valid Letter """
        self.assertTrue(isinstance(self.construct_sound('a'), VowelSound))
        self.assertTrue(isinstance(self.construct_sound('e'), VowelSound))
        self.assertTrue(isinstance(self.construct_sound('y'), VowelSound))
        self.assertTrue(isinstance(self.construct_sound('o'), VowelSound))

    def test_sound_constr_object(self):
        """ a valid Letter """
        self.assertTrue(isinstance(self.construct_sound(Letter('i')), SemivowelSound))
        self.assertTrue(isinstance(self.construct_sound(Letter('u')), SemivowelSound))
        self.assertTrue(isinstance(self.construct_sound(Letter('x')), HeavyMakerSound))
        self.assertTrue(isinstance(self.construct_sound(Letter('z')), HeavyMakerSound))

    def test_sound_constr_diph(self):
        """ a valid list of Letters """
        self.assertTrue(isinstance(self.construct_sound('a', 'e'), Diphthong))
        self.assertTrue(isinstance(self.construct_sound('oe'), Diphthong))
        self.assertTrue(isinstance(
            self.construct_sound(Letter('a'), Letter('U')), Diphthong))

    def test_sound_constr_digraph(self):
        """ a valid list of Letters """
        self.assertTrue(isinstance(
            self.construct_sound(Letter('Q'), Letter('u')), ConsonantSound))
        self.assertTrue(isinstance(
            self.construct_sound(Letter('g'), Letter('U')), ConsonantSound))
        
    def test_sound_fail_constr_illegal(self):
        """ not a valid list of Letters """
        with self.assertRaises(SoundException):
            self.construct_sound('qi')

    def test_sound_fail_constr_illegal_digraph(self):
        """ not a valid list of Letters """
        with self.assertRaises(SoundException):
            self.construct_sound('gy')

    def test_sound_fail_constr_illegal(self):
        """ not a valid list of Letters """
        with self.assertRaises(SoundException):
            self.construct_sound('xr')

    def test_sound_fail_constr_length(self):
        """ not a valid list of Letters """
        with self.assertRaises(SoundException):
            self.construct_sound(Letter('Q'), Letter('u'), Letter('o'))

    def test_sound_fail_constr_space(self):
        """ space is not a sound """
        with self.assertRaises(LetterException):
            self.construct_sound(Letter(' '))

    def test_sound_constr_from_text(self):
        """ a regular sound should be created easily """
        sound = SoundFactory.create_sounds_from_text('A')
        self.assertTrue(isinstance(sound[0], Sound))
        self.assertEqual(len(sound), 1)

    def test_sound_fail_cstr_incl_space(self):
        """ a sound cannot contain spaces """
        with self.assertRaises(LetterException):
            SoundFactory.create_sounds_from_text([' ', 'c'])
            
    def test_sound_fail_constr_too_rare(self):
        """ not a normally recognized diphthong """
        sound = SoundFactory.create_sounds_from_text('ui')
        self.assertEqual(sound[0], SoundFactory.create('u'))
        self.assertEqual(len(sound), 1)

    def test_sound_fail_constr_no_diph(self):
        """ not a normally recognized diphthong """
        sound = SoundFactory.create_sounds_from_text('uu')
        self.assertEqual(sound[0], SoundFactory.create('u'))
        self.assertEqual(len(sound), 1)
        
    def test_sound_fail_constr_nonexist(self):
        """ creating sounds from text does not accept any input """
        sound = SoundFactory.create_sounds_from_text('ou')
        self.assertEqual(sound[0], SoundFactory.create('o'))
        self.assertEqual(len(sound), 1)
        
    def test_sound_constr_with_th(self):
        """ creating sounds from text does not accept any input """
        sound = SoundFactory.create_sounds_from_text('th')
        self.assertEqual(sound[0], SoundFactory.create('th'))
        self.assertEqual(len(sound), 1)

    def test_sound_constr_with_rh(self):
        """ creating sounds from text does not accept any input """
        sound = SoundFactory.create_sounds_from_text('rh')
        self.assertEqual(sound[0], SoundFactory.create('rh'))
        self.assertEqual(len(sound), 1)

    def test_sound_fail_constr_nonexist2(self):
        """ creating sounds from text does not accept any input """
        sound = SoundFactory.create_sounds_from_text('ea')
        self.assertEqual(sound[0], SoundFactory.create('e'))
        self.assertEqual(len(sound), 1)
        
    def test_sound_factory(self):
        """ integration test for finding sounds """
        expected_sounds = []
        expected_sounds.append(SoundFactory.create('f'))
        expected_sounds.append(SoundFactory.create('o'))
        expected_sounds.append(SoundFactory.create('r'))
        expected_sounds.append(SoundFactory.create('s'))
        sounds = SoundFactory.find_sounds_for_text('fors')
        self.assertEqual(sounds, expected_sounds)
        
    def test_sound_factory_digraphs(self):
        """ digraphs must work out well """
        expected_sounds = []
        expected_sounds.append(SoundFactory.create('qu'))
        expected_sounds.append(SoundFactory.create('ae'))
        sounds = SoundFactory.find_sounds_for_text('quae')
        self.assertEqual(sounds, expected_sounds)

    def test_sound_factory_no_diph(self):
        """ digraphs must work out well """
        expected_sounds = []
        expected_sounds.append(SoundFactory.create('th'))
        expected_sounds.append(SoundFactory.create('e'))
        expected_sounds.append(SoundFactory.create('a'))
        sounds = SoundFactory.find_sounds_for_text('thea')
        self.assertEqual(sounds, expected_sounds)
        
    def test_sound_factory_many_vowels(self):
        """ digraphs must work out well """
        expected_sounds = []
        expected_sounds.append(SoundFactory.create('ae'))
        expected_sounds.append(SoundFactory.create('u'))
        expected_sounds.append(SoundFactory.create('m'))
        sounds = SoundFactory.find_sounds_for_text('aeum')
        self.assertEqual(sounds, expected_sounds)

    def test_sound_factory_many_semivowels(self):
        """ digraphs must work out well """
        expected_sounds = []
        expected_sounds.append(SoundFactory.create('ae'))
        expected_sounds.append(SoundFactory.create('u'))
        expected_sounds.append(SoundFactory.create('u'))
        expected_sounds.append(SoundFactory.create('m'))
        sounds = SoundFactory.find_sounds_for_text('aevum')
        self.assertEqual(sounds, expected_sounds)