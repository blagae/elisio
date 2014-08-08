import unittest
from Elisio.engine import Word, Sound, Letter
from Elisio.exceptions import ScansionException

class Test_Sound(unittest.TestCase):
    def constructSound(self, *texts):
        letters = []
        for text in texts:
            letters.append(text)
        sound = Sound(*letters)
        return sound
    
    def test_SoundConstructRegular(self):
        self.assertTrue(isinstance(self.constructSound('a'), Sound))

    def test_SoundConstructObject(self):
        self.assertTrue(isinstance(self.constructSound(Letter('a')), Sound))
        
    def test_SoundConstructDiphthongRegular(self):
        self.assertTrue(isinstance(self.constructSound('a', 'e'), Sound))

    def test_SoundConstructDiphthongRegularString(self):
        self.assertTrue(isinstance(self.constructSound('ae'), Sound))
        
    def test_SoundConstructDiphthongObject(self):
        self.assertTrue(isinstance(self.constructSound(Letter('e'), Letter('U')), Sound))

    def test_SoundConstructDigraph(self):
        self.assertTrue(isinstance(self.constructSound(Letter('Q'), Letter('u')), Sound))
        
    def test_SoundFailConstructIllegal(self):
        with self.assertRaises(ScansionException):
            sound = self.constructSound('qi')

    def test_SoundFailConstructLength(self):
        with self.assertRaises(ScansionException):
            sound = self.constructSound(Letter('Q'), Letter('u'), Letter('o'))

    def test_SoundFailConstructSpace(self):
        with self.assertRaises(ScansionException):
            sound = self.constructSound(Letter(' '))
    
    def test_SoundConstructFromText(self):
        sound = Sound.createFromText('A')
        self.assertTrue(isinstance(sound, Sound))

    def test_SoundFailConstructFromTextLength(self):
        with self.assertRaises(ScansionException):
            sound = Sound.createFromText('aeu')
            
    def test_SoundFailConstructFromTextSpace(self):
        with self.assertRaises(ScansionException):
            sound = Sound.createFromText([' ', 'c'])
            
    def test_SoundFailConstructTooRare(self):
        sound = Sound.createFromText('ui')
        self.assertEqual(sound, Sound('u'))

    def test_SoundFailConstructNonExistent(self):
        sound = Sound.createFromText('ou')
        self.assertEqual(sound, Sound('o'))
    
            
    def test_SoundEqual(self):
        sound1 = Sound('r')
        sound2 = Sound('r')
        self.assertEqual(sound1, sound2)


    def test_SoundEqualCaseInsensitive(self):
        sound1 = Sound('a')
        sound2 = Sound('A')
        self.assertEqual(sound1, sound2)
        
    def test_SoundEqualSemivowel(self):
        sound1 = Sound('u')
        sound2 = Sound('v')
        self.assertEqual(sound1, sound2)

    def test_SoundEqualOtherSemivowel(self):
        sound1 = Sound('i')
        sound2 = Sound('j')
        self.assertEqual(sound1, sound2)

    def test_SoundFinder(self):
        sound1 = Sound('f')
        sound2 = Sound('o')
        sound3 = Sound('r')
        sound4 = Sound('s')
        expected_sounds = []
        expected_sounds.append(sound1)
        expected_sounds.append(sound2)
        expected_sounds.append(sound3)
        expected_sounds.append(sound4)
        sounds = Word.findSoundsForText('fors')
        self.assertEqual(sounds, expected_sounds)
        
    def test_SoundFinderDigraphs(self):
        sound1 = Sound('qu')
        sound2 = Sound('ae')
        expected_sounds = []
        expected_sounds.append(sound1)
        expected_sounds.append(sound2)
        sounds = Word.findSoundsForText('quae')
        self.assertEqual(sounds, expected_sounds)

if __name__ == '__main__':
    unittest.main()
