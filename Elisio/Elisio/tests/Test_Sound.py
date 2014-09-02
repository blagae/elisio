import unittest
from Elisio.engine.wordProcessor import Word, Sound, Letter
from Elisio.exceptions import ScansionException

class Test_Sound(unittest.TestCase):
    def constructSound(self, *texts):
        letters = []
        for text in texts:
            letters.append(text)
        sound = Sound.create(*letters)
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
        self.assertTrue(isinstance(self.constructSound(Letter('a'), Letter('U')), Sound))

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
        self.assertTrue(isinstance(sound[0], Sound))
        self.assertEqual(len(sound), 1)
            
    def test_SoundFailConstructFromTextSpace(self):
        with self.assertRaises(ScansionException):
            sound = Sound.createFromText([' ', 'c'])
            
    def test_SoundFailConstructTooRare(self):
        sound = Sound.createFromText('ui')
        self.assertEqual(sound[0], Sound.create('u'))
        self.assertEqual(len(sound), 1)

    def test_SoundFailConstructNonExistent(self):
        sound = Sound.createFromText('ou')
        self.assertEqual(sound[0], Sound.create('o'))
        self.assertEqual(len(sound), 1)
    
            
    def test_SoundEqual(self):
        sound1 = Sound.create('r')
        sound2 = Sound.create('r')
        self.assertEqual(sound1, sound2)


    def test_SoundEqualCaseInsensitive(self):
        sound1 = Sound.create('a')
        sound2 = Sound.create('A')
        self.assertEqual(sound1, sound2)
        
    def test_SoundEqualSemivowel(self):
        sound1 = Sound.create('u')
        sound2 = Sound.create('v')
        self.assertEqual(sound1, sound2)

    def test_SoundEqualOtherSemivowel(self):
        sound1 = Sound.create('i')
        sound2 = Sound.create('j')
        self.assertEqual(sound1, sound2)

    def test_SoundFinder(self):
        sound1 = Sound.create('f')
        sound2 = Sound.create('o')
        sound3 = Sound.create('r')
        sound4 = Sound.create('s')
        expected_sounds = []
        expected_sounds.append(sound1)
        expected_sounds.append(sound2)
        expected_sounds.append(sound3)
        expected_sounds.append(sound4)
        sounds = Word.findSoundsForText('fors')
        self.assertEqual(sounds, expected_sounds)
        
    def test_SoundFinderDigraphs(self):
        sound1 = Sound.create('qu')
        sound2 = Sound.create('ae')
        expected_sounds = []
        expected_sounds.append(sound1)
        expected_sounds.append(sound2)
        sounds = Word.findSoundsForText('quae')
        self.assertEqual(sounds, expected_sounds)

if __name__ == '__main__':
    unittest.main()
