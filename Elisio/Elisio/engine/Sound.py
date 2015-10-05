import re
from Elisio.engine.Letter import Letter, LetterType
from Elisio.exceptions import SoundException

class Sound(object):
    """
    Sound class
    A sound is composed of one or several Letters
    """
    def __init__(self, *letters):
        """ construct a Sound from a list of letters, or (a list of) text(s) """
        self.letters = []
        for letter in letters:
            if isinstance(letter, Letter):
                self.letters.append(letter)
            else:
                raise SoundException("invalid constructor "+str(self.letters))

    def get_text(self):
        """ get String representation for output purposes """
        result = ""
        for letter in self.letters:
            result += letter.__str__()
        return result

    def is_valid_sound(self):
        """ is a given sound a valid sound
        this is determined by the number of letters
        in case that number is 2, it must be
        one of a fixed list of combinations
        """
        raise NotImplementedError("Please Implement this method")

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.letters)


    def is_vowel(self):
        """ determine whether a sound is unambiguously vocalic """
        return False
    def is_semivowel(self):
        """ it is impossible to determine on the sound level
        whether or not a semivowel is vocalic or consonantal
        therefore we keep the semivowel category separate
        """
        return False
    def is_consonant(self):
        """
        does a sound contain a consonantal letter
        implicitly abstract
        """
        return False
    def is_diphthong(self):
        """
        implicitly abstract
        """
        return False
    def is_heavy_making(self):
        """
        does a sound contain a cluster-forming consonant letter
        implicitly abstract
        """
        return False
    def is_h(self):
        """
        implicitly abstract
        """
        return False
    def get_type(self):
        """ general API method for getting the type """
        return self.letters[0].get_type()

class VowelSound(Sound):
    """
    Vowels are syllable-bearing Sounds
    """
    def __init__(self, *letters):
        super(VowelSound, self).__init__(*letters)

    def is_vowel(self):
        """ override for type checking """
        return True

    def is_valid_sound(self):
        """
        double vowel sounds should be checked immediately as Diphthong instances
        """
        if len(self.letters) != 1:
            return False
        first = self.letters[0].letter
        return Letter.letters[first] == LetterType.VOWEL

class Diphthong(VowelSound):
    """
    Diphthongs are specific double Vowel Sounds
    """
    def __init__(self, *letters):
        super(Diphthong, self).__init__(*letters)

    def is_diphthong(self):
        """ override for type checking """
        return True

    def is_valid_sound(self):
        """
        the recognized diphthongs are AU, AE, and OE
        there are several more, but they are rare and lexically determined
        """
        if len(self.letters) == 1:
            return False
        first = self.letters[0].letter
        second = self.letters[1].letter
        return ((second == 'u' and first == 'a') or
                (second == 'e' and (first == 'a' or first == 'o')))

class SemivowelSound(Sound):
    """
    Semivowel Sounds can act both as Vowels and Consonants, depending on
    both phonetic and lexical circumstances
    They have no knowledge which they are at any given time
    """
    def __init__(self, *letters):
        super(SemivowelSound, self).__init__(*letters)

    def is_semivowel(self):
        """ override for type checking """
        return True

    def is_valid_sound(self):
        """
        Semivowel Sounds are always single Sounds
        """
        if len(self.letters) != 1:
            return False
        first = self.letters[0].letter
        return Letter.letters[first] == LetterType.SEMIVOWEL

class ConsonantSound(Sound):
    """
    ConsonantSounds are non-syllable-bearing Sounds with potential
    to make a previous Syllable heavy. They do so when clustered,
    unless (maybe) in specific double-Consonant combinations
    """
    def __init__(self, *letters):
        super(ConsonantSound, self).__init__(*letters)
    def is_consonant(self):
        """ override for type checking """
        return True
    def is_valid_sound(self):
        """
        the only valid double Sounds are listed below
        """
        if len(self.letters) != 1:
            return self.is_valid_double_sound()
        first = self.letters[0].letter
        return Letter.letters[first] == LetterType.CONSONANT

    def is_h(self):
        """
        method call avoids literal
        """
        return self.letters[0] == 'h'

    def is_muta_cum_liquida(self):
        """
        MCL is a sequence of a stop or f and a liquid sound
        """
        if len(self.letters) < 2:
            return False
        first = self.letters[0].letter
        second = self.letters[1]
        return ((second == 'r' or second == 'l') and
                (first == 't' or first == 'd' or
                 first == 'p' or first == 'b' or
                 first == 'c' or first == 'g' or
                 first == 'f')
               )

    def is_valid_double_sound(self):
        """
        the fixed list of combinations
        * QU
        * muta cum liquida
        * an aspirated consonant
        """
        if len(self.letters) != 2:
            return False
        first = self.letters[0].letter
        second = self.letters[1]
        return ((first == 'q' and second == 'u') or
                (first == 'g' and second == 'u') or
                self.is_muta_cum_liquida() or
                ((first == 't' or first == 'p' or first == 'c' or first == 'r')
                 and second == 'h') #or
                #(second == 'u' and (first == 'l' or first == 'g'))
                ## for future reference: this gives many false positives
                ## but maybe it will come in handy for a different method ?
               )

class HeavyMakerSound(ConsonantSound):
    """
    HeavyMakerSounds are ConsonantSounds that
    inherently make the previous Syllable heavy
    because they essentially are two Sounds in one Letter
    """
    def __init__(self, *letters):
        super(HeavyMakerSound, self).__init__(*letters)

    def is_heavy_making(self):
        """ override for type checking """
        return True

    def is_valid_sound(self):
        """
        a HeavyMaker is never part of a one-sound Consonant cluster
        """
        if len(self.letters) != 1:
            return False
        first = self.letters[0].letter
        return Letter.letters[first] == LetterType.HEAVYMAKER

    
class SoundFactory(object):
    # TODO: rename methods ?
    @classmethod
    def create(cls, *letters):
        """
        outward-facing factory which preparses its parameters
        and passes them to the internal factory method
        """
        letterlist = []
        for item in letters:
            if isinstance(item, Letter):
                letterlist.append(item)
            else:
                for stri in item:
                    if isinstance(stri, Letter):
                        letterlist.append(stri)
                    elif len(stri) > 1:
                        for char in stri:
                            letterlist.append(Letter(char))
                    else:
                        letterlist.append(Letter(stri))
        return SoundFactory.__factory(letterlist)

    @classmethod
    def __factory(cls, letterlist):
        """
        private factory method that will eventually create a sound
        from a list of letters
        """
        first = True
        for item in letterlist:
            if first:
                lettertype = Letter.letters[item.letter]

                if lettertype == LetterType.VOWEL:
                    sound = VowelSound(item)
                elif lettertype == LetterType.CONSONANT:
                    sound = ConsonantSound(item)
                elif lettertype == LetterType.SEMIVOWEL:
                    sound = SemivowelSound(item)
                elif lettertype == LetterType.HEAVYMAKER:
                    sound = HeavyMakerSound(item)
                else:
                    raise SoundException("not a valid letter"+str(item))
                # set looping consonant to False
                first = False
            else:
                if sound.is_vowel() or sound.is_semivowel():
                    sound = Diphthong(sound.letters[0], item)
                if sound.is_consonant():
                    sound.letters.append(item)
        if not sound.is_valid_sound():
            raise SoundException("not a valid sound given in factory method")
        return sound
    
    @classmethod
    def create_sounds_from_text(cls, text):
        """
        try to create a Sound from given text string of maximally 3 letters
        this is a classmethod because it acts as a (super-)Factory
        returns an array of sounds
        """
        if len(text) > 3:
            raise SoundException("too many letters in this text sample")
        elif len(text) == 3:
            # detect intervocalic semivowels
            if re.match("^[aeijouvy][ijuv][aeijouvy]$", text):
                sounds = []
                for i in text:
                    snd = SoundFactory.create(i)
                    sounds.append(snd)
                return sounds
        try:
            sound = SoundFactory.create(text[0:2]) # TODO: or 0:1 ??
        except SoundException:
            sound = SoundFactory.create(text[0])
        return [sound]

    @classmethod
    def find_sounds_for_text(cls, text):
        """ iteratively allocate all text to a sound """
        i = 0
        sounds = []
        while i < len(text):
            added_sounds = SoundFactory.create_sounds_from_text(text[i:i+3])
            for sound in added_sounds:
                # dirty hack to prevent 'novae' type of word from being analyzed as 'no-va-e'
                if len(sounds) > 0 and sound == SoundFactory.create('e') and sounds[-1] == SoundFactory.create('a'):
                    sound = SoundFactory.create('ae')
                    sounds.pop()
                sounds.append(sound)
                i += len(sound.letters)
        return sounds