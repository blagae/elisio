import re
from enum import Enum

from elisio.exceptions import SoundException


class LetterType(Enum):
    """
    The possible types of letters
    """
    VOWEL = 0
    CONSONANT = 1
    SEMIVOWEL = 2
    HEAVYMAKER = 3


latin_letters = {
    'e': LetterType.VOWEL,
    'a': LetterType.VOWEL,
    'i': LetterType.SEMIVOWEL,
    'u': LetterType.SEMIVOWEL,
    't': LetterType.CONSONANT,
    's': LetterType.CONSONANT,
    'r': LetterType.CONSONANT,
    'n': LetterType.CONSONANT,
    'o': LetterType.VOWEL,
    'm': LetterType.CONSONANT,
    'c': LetterType.CONSONANT,
    'l': LetterType.CONSONANT,
    'p': LetterType.CONSONANT,
    'd': LetterType.CONSONANT,
    'q': LetterType.CONSONANT,
    'b': LetterType.CONSONANT,
    'g': LetterType.CONSONANT,
    'f': LetterType.CONSONANT,
    'h': LetterType.CONSONANT,
    'x': LetterType.HEAVYMAKER,
    'y': LetterType.VOWEL,
    'k': LetterType.CONSONANT,
    'z': LetterType.HEAVYMAKER,
    'ë': LetterType.VOWEL
}

liquida = ['r', 'l']
hard_muta = ['p', 't', 'c']
muta = ['b', 'd', 'g', 'f'] + hard_muta


class Sound:
    """
    Sound class
    A sound is composed of one or several Letters
    """

    def __init__(self, *letters: str):
        """ construct a Sound from a list of letters, or (a list of) text(s) """
        self.letters = []
        for letter in letters:
            if letter in latin_letters:
                self.letters.append(letter)
            else:
                raise SoundException("invalid constructor: " + str(self.letters))

    def get_text(self) -> str:
        """ get String representation for output purposes """
        return ''.join(self.letters)

    def is_valid_sound(self) -> bool:
        """ is a given sound a valid sound
        this is determined by the number of letters
        in case that number is 2, it must be
        one of a fixed list of combinations
        """
        raise NotImplementedError("Please implement this method")

    def __eq__(self, other: object) -> bool:
        return self.__dict__ == other.__dict__

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return str(self.letters)

    def is_vowel(self) -> bool:
        """ determine whether a sound is unambiguously vocalic """
        return False

    def is_semivowel(self) -> bool:
        """ it is impossible to determine on the sound level
        whether or not a semivowel is vocalic or consonantal
        therefore we keep the semivowel category separate
        """
        return False

    def is_consonant(self) -> bool:
        """
        does a sound contain a consonantal letter
        implicitly abstract
        """
        return False

    def is_diphthong(self) -> bool:
        """
        implicitly abstract
        """
        return False

    def is_heavy_making(self) -> bool:
        """
        does a sound contain a cluster-forming consonant letter
        implicitly abstract
        """
        return False

    def is_h(self) -> bool:
        """
        implicitly abstract
        """
        return False

    def get_type(self) -> LetterType:
        """ general API method for getting the type """
        return latin_letters[self.letters[0]]


class VowelSound(Sound):
    """
    Vowels are syllable-bearing Sounds
    """

    def __init__(self, *letters: str):
        super().__init__(*letters)

    def is_vowel(self) -> bool:
        """ override for type checking """
        return True

    def is_valid_sound(self) -> bool:
        """
        double vowel sounds should be checked immediately as Diphthong instances
        """
        if len(self.letters) != 1:
            return False
        return latin_letters[self.letters[0]] == LetterType.VOWEL


class Diphthong(VowelSound):
    """
    Diphthongs are specific double Vowel Sounds
    """

    def __init__(self, *letters: str):
        super().__init__(*letters)

    def is_diphthong(self) -> bool:
        """ override for type checking """
        return True

    def is_valid_sound(self) -> bool:
        """
        the recognized diphthongs are AU, AE, and OE
        there are several more, but they are rare and lexically determined
        """
        if len(self.letters) == 1:
            return False
        first = self.letters[0]
        second = self.letters[1]
        return ((first == 'a' and second == 'u') or
                # lazy and: second is more likely to fail
                (second == 'e' and (first == 'a' or first == 'o')))


class SemivowelSound(Sound):
    """
    Semivowel Sounds can act both as Vowels and Consonants, depending on
    both phonetic and lexical circumstances
    They have no knowledge which they are at any given time
    """

    def __init__(self, *letters: str):
        super().__init__(*letters)

    def is_semivowel(self) -> bool:
        """ override for type checking """
        return True

    def is_valid_sound(self) -> bool:
        """
        Semivowel Sounds are always single Sounds
        """
        if len(self.letters) != 1:
            return False
        return latin_letters[self.letters[0]] == LetterType.SEMIVOWEL


class ConsonantSound(Sound):
    """
    ConsonantSounds are non-syllable-bearing Sounds with potential
    to make a previous Syllable heavy. They do so when clustered,
    unless (maybe) in specific double-Consonant combinations
    """

    def __init__(self, *letters: str):
        super().__init__(*letters)

    def is_consonant(self) -> bool:
        """ override for type checking """
        return True

    def is_valid_sound(self) -> bool:
        """
        the only valid double Sounds are listed below
        """
        if len(self.letters) != 1:
            return self.is_valid_double_sound()
        return latin_letters[self.letters[0]] == LetterType.CONSONANT

    def is_h(self) -> bool:
        """
        method call avoids literal
        """
        return self.letters[0] == 'h'

    def is_muta_cum_liquida(self) -> bool:
        """
        MCL is a sequence of a stop or f and a liquid sound
        """
        if len(self.letters) < 2:
            return False
        return (self.letters[0] in muta) and (self.letters[1] in liquida)

    def is_valid_double_sound(self) -> bool:
        """
        the fixed list of combinations
        * QU
        * muta cum liquida
        * an aspirated consonant
        """
        if len(self.letters) != 2:
            return False
        first = self.letters[0]
        second = self.letters[1]
        return ((second == 'u' and first in ['q', 'g']) or
                self.is_muta_cum_liquida() or
                (second == 'h' and
                 (first == 'r' or first in hard_muta)))


class HeavyMakerSound(ConsonantSound):
    """
    HeavyMakerSounds are ConsonantSounds that
    inherently make the previous Syllable heavy
    because they essentially are two Sounds in one Letter
    """

    def __init__(self, *letters: str):
        super().__init__(*letters)

    def is_heavy_making(self) -> bool:
        """ override for type checking """
        return True

    def is_valid_sound(self) -> bool:
        """
        a HeavyMaker is never part of a one-sound Consonant cluster
        """
        if len(self.letters) != 1:
            return False
        return latin_letters[self.letters[0]] == LetterType.HEAVYMAKER


class SoundFactory:
    sound_dict: dict[str, Sound] = {}

    @staticmethod
    def create_single_letter(letter: str) -> Sound:
        try:
            lettertype = latin_letters[letter]
        except KeyError:
            raise SoundException("not a valid letter: " + str(letter))
        if lettertype == LetterType.VOWEL:
            return VowelSound(letter)
        elif lettertype == LetterType.CONSONANT:
            return ConsonantSound(letter)
        elif lettertype == LetterType.SEMIVOWEL:
            return SemivowelSound(letter)
        elif lettertype == LetterType.HEAVYMAKER:
            return HeavyMakerSound(letter)
        raise SoundException("not a valid letter: " + str(letter))

    @staticmethod
    def create(letters: str) -> Sound:
        """
        outward-facing factory which preparses its parameters
        and passes them to the internal factory method
        """
        first = True
        for letter in letters:
            item = letter.lower()
            if item == 'v':
                item = 'u'
            elif item == 'j':
                item = 'i'
            if first:
                sound = SoundFactory.create_single_letter(item)
                # set looping consonant to False
                first = False
            else:
                if sound.is_vowel() or sound.is_semivowel():
                    sound = Diphthong(sound.letters[0], item)
                if sound.is_consonant():
                    sound.letters.append(item)
        if not sound.is_valid_sound():
            raise SoundException("not a valid sound given in factory method")
        SoundFactory.sound_dict[sound.get_text()] = sound
        return sound

    @staticmethod
    def create_sounds_from_text(text: str) -> list[Sound]:
        """
        try to create a Sound from given text string of maximally 3 letters
        this is a static method because it acts as a (super-)Factory
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
            sound = SoundFactory.create(text[0:2])
        except SoundException:
            sound = SoundFactory.create(text[0])
        return [sound]

    @staticmethod
    def find_sounds_for_text(text: str) -> list[Sound]:
        """ iteratively allocate all text to a sound """
        i = 0
        sounds: list[Sound] = []
        while i < len(text):
            added_sounds = SoundFactory.create_sounds_from_text(text[i:i + 3])
            for sound in added_sounds:
                # dirty hack to prevent 'novae' type of word from being analyzed as 'no-va-e'
                if sounds and sound.letters == ['e'] and sounds[-1].letters == ['a']:
                    sound = SoundFactory.create('ae')
                    sounds.pop()
                sounds.append(sound)
                i += len(sound.letters)
        return sounds
