import re
from enum import Enum

from .exceptions import SoundException


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
        if not letters:
            raise SoundException("Sound constructor cannot have empty argument list")
        local_letters = ''
        for letter in letters:
            if letter in latin_letters:
                local_letters += letter
            else:
                raise SoundException(f"invalid constructor arguments: {letters}")
        self.letters = local_letters

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
        return str(self.letters)

    def __len__(self) -> int:
        return len(self.letters)

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
        if len(self.letters) == 1:
            return latin_letters[self.letters] == LetterType.VOWEL
        return False


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
        return self.letters in ('au', 'ae', 'oe')

    def get_type(self) -> LetterType:
        """ general API method for getting the type """
        return LetterType.VOWEL


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
        if len(self.letters) == 1:
            return latin_letters[self.letters] == LetterType.SEMIVOWEL
        return False


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
        if len(self.letters) == 1:
            return latin_letters[self.letters] == LetterType.CONSONANT
        return self.is_valid_double_sound()

    def is_h(self) -> bool:
        """
        method call avoids literal
        """
        return self.letters[0] == 'h'

    def is_muta_cum_liquida(self) -> bool:
        """
        MCL is a sequence of a stop or f and a liquid sound
        """
        if len(self.letters) == 2:
            return (self.letters[0] in muta) and (self.letters[1] in liquida)
        return False

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


class HeavymakerSound(ConsonantSound):
    """
    HeavymakerSounds are ConsonantSounds that
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
        if len(self.letters) == 1:
            return latin_letters[self.letters] == LetterType.HEAVYMAKER
        return False


class SoundFactory:
    sound_dict = {letter: globals()[str.title(typ.name) + "Sound"](letter) for (letter, typ) in latin_letters.items()}

    @staticmethod
    def create(letters: str) -> Sound:
        """
        outward-facing factory which preparses its parameters
        and passes them to the internal factory method
        """
        if letters.lower() in SoundFactory.sound_dict:
            return SoundFactory.sound_dict[letters.lower()]
        for count, letter in enumerate(letters):
            item = letter.lower()
            if item == 'v':
                item = 'u'
            elif item == 'j':
                item = 'i'
            if not count:
                try:
                    sound = SoundFactory.sound_dict[item]
                except KeyError:
                    raise SoundException(f"not a valid letter: {item}")
            else:
                if sound.is_vowel() or sound.is_semivowel():
                    sound = Diphthong(sound.letters[0], item)
                elif sound.is_consonant():
                    sound = ConsonantSound(sound.letters[0], item)
        if not sound.is_valid_sound():
            raise SoundException("not a valid sound given in factory method")
        SoundFactory.sound_dict[sound.letters] = sound
        return sound

    @staticmethod
    def create_sounds_from_text(text: str) -> list[Sound]:
        """
        try to create a Sound from given text string of maximally 3 letters
        this is a static method because it acts as a (super-)Factory
        returns an array of sounds
        """
        if ' ' in text:
            raise SoundException("argument cannot contain spaces")
        if len(text) > 3:
            raise SoundException("too many letters in this text sample")
        elif len(text) == 3:
            # detect intervocalic semivowels
            if re.match("^[aeijouvy][ijuv][aeijouvy]$", text):
                return [SoundFactory.create(text[0]), SoundFactory.create(text[1])]
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
                sounds.append(sound)
                i += len(sound.letters)
        return sounds
