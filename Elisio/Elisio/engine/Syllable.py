from Elisio.engine.Sound import *
import copy
import enum
from Elisio.exceptions import SyllableException

class Syllable(object):
    """ Syllable class
    A syllable knows its sounds and can determine
    if the specific combination of them is a valid one
    """
    def __init__(self, syllable, test=True, weight=None):
        """ construct a Syllable by its contents """
        self.weight = weight
        self.syllable = syllable
        self.sounds = WordAnalyzer.find_sounds_for_text(syllable)
        if test and not self.is_valid():
            raise SyllableException("invalid Syllable object")

    def __eq__(self, other):
        return self.sounds == other.sounds

    def __repr__(self):
        return str(self.sounds)

    def get_text(self):
        """ get String representation for output purposes """
        result = ""
        for sound in self.sounds:
            result += sound.get_text()
        return result

    def is_valid(self):
        """
        a syllable is valid if it contains:
            * at most one consonant after the vocalic sound, and
            * a single vowel or semivowel
            * a semivowel and a vowel in that order
        """
        if self.get_text() == 'gui':
            return True
        contains_final_consonant = contains_vowel = contains_semivowel = False
        only_consonants = True
        for count, sound in enumerate(self.sounds):
            if isinstance(sound, ConsonantSound):
                if contains_final_consonant:
                    pass
                    #return False
                if contains_vowel or contains_semivowel:
                    contains_final_consonant = True
            elif isinstance(sound, VowelSound):
                if (contains_vowel or
                        (contains_final_consonant and
                         contains_semivowel)):
                    return False
                contains_vowel = True
                only_consonants = False
            elif isinstance(sound, SemivowelSound):
                if (contains_vowel or
                        (contains_final_consonant and
                         contains_semivowel)):
                    return False
                if count > 0:
                    contains_vowel = True
                contains_semivowel = True
                only_consonants = False
        return contains_vowel or contains_semivowel or only_consonants

    def ends_with_consonant(self):
        """ last sound of the syllable is consonantal """
        return self.sounds[-1].is_consonant()

    def can_elide_if_final(self):
        """ special property of words ending in a vowel """
        return (self.ends_with_vowel() or
                (self.sounds[-1] == SoundFactory.create('m') and
                 (self.sounds[-2].is_vowel() or self.sounds[-2].is_semivowel()))
               )

    def ends_with_vowel(self):
        """
        last sound of the syllable is vocalic
        a final semivowel is always vocalic
        """
        return self.sounds[-1].is_vowel() or self.sounds[-1].is_semivowel()

    def starts_with_vowel(self, initial=True):
        """
        first sound of the syllable is vocalic
        an initial semivowel is only vocalic if it is the syllable's only sound
        or if it is followed directly by a consonant
        """
        return (self.sounds[0].is_vowel() or
                self.sounds[0].is_h() or
                (self.sounds[0].is_semivowel() and
                 (not initial or len(self.sounds) == 1 or
                  self.sounds[1].is_consonant()))
               )
    def starts_with_consonant(self):
        """
        first sound of the syllable is consonantal
        an initial semivowel is consonantal if it is followed by a vowel
        """
        return (self.sounds[0].is_consonant() or
                (self.sounds[0].is_semivowel() and len(self.sounds) > 1 and
                 self.sounds[1].is_vowel()))

    def starts_with_consonant_cluster(self):
        """ first sounds of the syllable are all consonants """
        return (self.starts_with_consonant() and
                ((len(self.sounds) > 1 and self.sounds[1].is_consonant()) or
                 self.makes_previous_heavy())
               )

    def makes_previous_heavy(self):
        """ first sound of the syllable is a double consonant letter """
        return self.sounds[0].is_heavy_making()

    def get_vowel(self):
        """ get the vocalic sound from a syllable """
        semivowel = None
        for sound in reversed(self.sounds):
            if sound.is_vowel():
                return sound
            if sound.is_semivowel():
                if semivowel:
                    return semivowel
                semivowel = sound
        if semivowel:
            return semivowel
        raise SyllableException("no vowel found in Syllable"+str(self.sounds))

    def is_heavy(self, next_syllable=None):
        """
        determines whether the syllable is inherently heavy or not
        a syllable is heavy if it ends in a consonant
        or if the next syllable starts with a heavy-making consonant
        or if it contains a final diphthong which isn't shortened
        by the next syllable (with vocalic start)
        final syllables are long if they are O, U, or I, or a diphthong
        """
        vowel = self.get_vowel()
        if next_syllable and isinstance(next_syllable, Syllable):
            return ((self.ends_with_consonant() or
                     next_syllable.makes_previous_heavy()) or
                    (not self.is_light(next_syllable) and vowel.is_diphthong()))
        return (self.ends_with_consonant() or vowel.is_diphthong() or
                vowel.letters[0] in WordAnalyzer.longEndVowels)

    def is_light(self, next_syllable=None):
        """
        determines whether the syllable is inherently light or not
        a syllable is always light if it ends in a vowel
        and is followed by a vowel in the next syllable
        final E is usually short
        """
        if next_syllable and isinstance(next_syllable, Syllable):
            return self.ends_with_vowel() and next_syllable.starts_with_vowel()
        return (self.ends_with_vowel() and
                not self.get_vowel().is_diphthong() and
                self.get_vowel().letters[0] in WordAnalyzer.shortEndVowels
               )

    def add_sound(self, sound):
        """ add a sound to a syllable if the syllable stays
        valid by the addition """
        test_syllable = copy.deepcopy(self)
        test_syllable.sounds.append(sound)
        if test_syllable.is_valid():
            self.sounds.append(sound)
        else:
            raise SyllableException("syllable invalidated by last addition")

    def get_weight(self, next_syllable=None):
        """
        try to determine the weight of the syllable
        in the light of the next syllable
        if this doesn't succeed, assign the weight ANCEPS = undetermined
        """
        if self.weight:
            return self.weight
        if self.is_light(next_syllable):
            return Weight.LIGHT
        elif self.is_heavy(next_syllable):
            return Weight.HEAVY
        else:
            return Weight.ANCEPS

    @classmethod
    def create_syllable_from_database(cls, syll):
        """
        The factory method that will create a syllable from the database
        with its given weight (if stored in the database)
        """
        from Elisio.models import DeviantSyllable
        if not isinstance(syll, DeviantSyllable):
            raise SyllableException("database error with Deviant Syllable")
        result = Syllable(syll.contents, False, syll.weight)
        return result

    
class Weight(enum.Enum):
    """
    The possible types of syllable weights
    """
    NONE = 0
    LIGHT = 1
    HEAVY = 2
    ANCEPS = 3

    labels = {
        NONE: 'None',
        LIGHT: 'Light',
        HEAVY: 'Heavy',
        ANCEPS: 'Anceps'
    }

class WordAnalyzer(object):
    # TODO: this breaks a lot of verses with final long e
    # and the Verse tests where e$ is scheduled to be light
    # proposed solution: find deviant word ?
    shortEndVowels = ['e']
    longEndVowels = ['i', 'o', 'u']

    @classmethod
    def find_sounds_for_text(cls, text):
        """ iteratively allocate all text to a sound """
        i = 0
        sounds = []
        while i < len(text):
            added_sounds = SoundFactory.create_sounds_from_text(text[i:i+3])
            for sound in added_sounds:
                sounds.append(sound)
                i += len(sound.letters)
        return sounds

    @classmethod
    def join_into_syllables(cls, sounds):
        """
        join a list of sounds into a preliminary syllables
        keep adding sounds to the syllable until it becomes illegal
        or the word ends.
        at either point, save the syllable
        """
        syllables = []
        current_syllable = Syllable("", False)
        for sound in sounds:
            try:
                current_syllable.add_sound(sound)
            except SyllableException:
                syllables.append(current_syllable)
                current_syllable = Syllable("", False)
                current_syllable.add_sound(sound)
        syllables.append(current_syllable)
        return syllables

    @classmethod
    def redistribute(cls, syllables):
        """
        redistribute the sounds of a list of syllables
        in order to use the correct syllables, not the longest possible
        """
        for count in range(len(syllables)-1):
            if (count == len(syllables)-2 and
                    syllables[count+1] == Syllable('ve')):
                continue
            if (syllables[count].ends_with_vowel() and
                    syllables[count+1].starts_with_consonant_cluster()):
                WordAnalyzer.__switch_sound(syllables[count], syllables[count+1], True)
            elif (syllables[count].ends_with_consonant() and
                  syllables[count+1].starts_with_vowel(False)):
                WordAnalyzer.__switch_sound(syllables[count], syllables[count+1], False)
        return syllables

    @classmethod
    def __switch_sound(cls, syllable1, syllable2, to_first):
        """ switch sounds from one syllable to another
        if toFirst is True, switch from the second to the first
        if toFirst is False, switch from the first to the second
        """
        if to_first:
            given_sound = syllable2.sounds[0]
            syllable2.sounds.remove(given_sound)
            syllable1.sounds.append(given_sound)
        else:
            given_sound = syllable1.sounds[-1]
            syllable1.sounds.reverse()
            syllable1.sounds.remove(given_sound)
            syllable1.sounds.reverse()
            syllable2.sounds.insert(0, given_sound)