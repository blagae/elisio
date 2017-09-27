import copy
import enum
import re
from Elisio.engine.Sound import SoundFactory
from Elisio.exceptions import SyllableException


class Weight(enum.Enum):
    """
    The possible types of syllable weights
    """
    NONE = 0
    LIGHT = 1
    HEAVY = 2
    ANCEPS = 3


class Syllable(object):
    """ Syllable class
    A syllable knows its sounds and can determine
    if the specific combination of them is a valid one
    """
    final_heavy = [re.compile('.*[ao]s$')]

    def __init__(self, text, validate=True, weight=None):
        """ construct a Syllable by its contents """
        self.weight = weight
        self.stressed = False
        self.sounds = self.fill_sounds(text, validate)
        self.text = Syllable.reconstruct_text(self.sounds)

    def __eq__(self, other):
        return self.sounds == other.sounds

    def __repr__(self):
        return str(self.sounds)

    def recalculate_text(self):
        self.text = Syllable.reconstruct_text(self.sounds)

    @staticmethod
    def reconstruct_text(sounds):
        """ get String representation for output purposes """
        result = ""
        for sound in sounds:
            result += sound.get_text()
        return result

    @staticmethod
    def fill_sounds(text, validate):
        sounds = SoundFactory.find_sounds_for_text(text)
        if validate and not Syllable.is_valid(sounds):
            raise SyllableException("invalid Syllable object")
        return sounds

    @staticmethod
    def is_valid(sounds, test=False):
        """
        a syllable is valid if it contains:
            * at most one consonant after the vocalic sound, and
            * a single vowel or semivowel
            * a semivowel and a vowel in that order
        """
        if len(sounds) > 1 and sounds[0] == sounds[1] and sounds[0] == SoundFactory.create('i'):
            return False
        if sounds[0] == SoundFactory.create('gu'):
            copied = copy.deepcopy(sounds)
            copied[0] = SoundFactory.create('u')
            valid = Syllable.is_valid(copied, test)
            if valid:
                sounds[0] = SoundFactory.create('g')
                sounds.insert(1, SoundFactory.create('u'))
            return valid
        contains_final_consonant = contains_vowel = contains_semivowel = False
        only_consonants = True
        for count, sound in enumerate(sounds):
            if sound.is_consonant():
                if contains_vowel or contains_semivowel:
                    if sound == SoundFactory.create('gu'):
                        return False
                    contains_final_consonant = True
            elif sound.is_vowel():
                if (contains_vowel or
                        (contains_final_consonant and
                         contains_semivowel)):
                    return False
                contains_vowel = True
                only_consonants = False
            elif sound.is_semivowel():
                if (contains_vowel or
                        (contains_final_consonant and
                         contains_semivowel)):
                    return False
                if count > 0:
                    contains_vowel = True
                contains_semivowel = True
                only_consonants = False
        return contains_vowel or contains_semivowel or (only_consonants == test)

    def ends_with_consonant(self):
        """ last sound of the syllable is consonantal """
        return self.sounds[-1].is_consonant()

    def ends_with_consonant_cluster(self):
        return (len(self.sounds) > 1 and self.ends_with_consonant() and
                self.sounds[-2].is_consonant())

    def must_be_heavy(self):
        if self.ends_with_heavymaker():
            return True
        for rgx in Syllable.final_heavy:
            if rgx.match(self.text):
                return True
        return False

    def ends_with_heavymaker(self):
        """ last sound of the syllable is consonantal """
        return self.sounds[-1].is_heavy_making()

    def can_elide_if_final(self):
        """ special property of words ending in a vowel """
        return (self.ends_with_vowel() or
                (self.sounds[-1] == SoundFactory.create('m') and
                 (self.sounds[-2].is_vowel() or self.sounds[-2].is_semivowel())))

    def has_diphthong(self):
        return self.get_vowel().is_diphthong()

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
        if self.sounds[0].is_vowel():
            return True
        if (self.sounds[0].is_h() and
            len(self.sounds) > 1 and
                not self.sounds[1].is_consonant()):
            return True
        if (self.sounds[0].is_semivowel() and
                (not initial or (len(self.sounds) == 1 or
                                 self.sounds[1].is_consonant()))):
            return True
        return False

    def starts_with_consonant(self, initial=True):
        """
        first sound of the syllable is consonantal
        an initial semivowel is consonantal if it is followed by a vowel
        """
        return not self.starts_with_vowel(initial)

    def starts_with_consonant_cluster(self):
        """ first sounds of the syllable are all consonants """
        return (self.starts_with_consonant() and
                ((len(self.sounds) > 1 and self.sounds[1].is_consonant()) or
                 self.makes_previous_heavy())
                and self.sounds[0] != SoundFactory.create('gu'))

    def makes_previous_heavy(self):
        """ first sound of the syllable is a double consonant letter """
        return self.sounds[0].is_heavy_making()

    def get_vowel_location(self):
        for idx, sound in enumerate(reversed(self.sounds)):
            if sound.is_vowel() or sound.is_semivowel():
                return len(self.sounds) - idx - 1
        raise SyllableException("no vowel found in Syllable" + str(self.sounds))

    def get_vowel(self):
        """ get the vocalic sound from a syllable """
        return self.sounds[self.get_vowel_location()]

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
            if next_syllable.sounds[0] == SoundFactory.create('h'):
                return self.ends_with_consonant_cluster() or self.ends_with_heavymaker()
            return ((self.ends_with_consonant() or
                     next_syllable.makes_previous_heavy()) or
                    (not self.is_light(next_syllable) and vowel.is_diphthong()))
        return (self.ends_with_consonant() or vowel.is_diphthong() or
                vowel.letters[0] in SyllableSplitter.longEndVowels)

    def must_be_anceps(self, next_syllable=None):
        if next_syllable and isinstance(next_syllable, Syllable):
            return (self.ends_with_vowel() and
                    self.get_vowel().is_diphthong() and
                    next_syllable.starts_with_vowel())
        return False

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
                self.get_vowel().letters[0] in SyllableSplitter.shortEndVowels)

    def add_sound(self, sound):
        """ add a sound to a syllable if the syllable stays
        valid by the addition """
        test_syllable = copy.deepcopy(self)
        test_syllable.sounds.append(sound)
        if Syllable.is_valid(test_syllable.sounds, True):
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
        if self.must_be_anceps(next_syllable):
            self.weight = Weight.ANCEPS
            return Weight.ANCEPS
        if self.is_light(next_syllable):
            self.weight = Weight.LIGHT
            return Weight.LIGHT
        elif self.is_heavy(next_syllable):
            self.weight = Weight.HEAVY
            return Weight.HEAVY
        return Weight.ANCEPS

    @staticmethod
    def create_syllable_from_database(syll):
        """
        The factory method that will create a syllable from the database
        with its given weight (if stored in the database)
        """
        from Elisio.models.deviant import DeviantSyllable
        if not isinstance(syll, DeviantSyllable):
            raise SyllableException("database error with Deviant Syllable")
        result = Syllable(syll.contents, False, syll.weight)
        return result


class SyllableSplitter(object):
    shortEndVowels = []
    longEndVowels = ['i', 'o', 'u']

    @staticmethod
    def join_into_syllables(sounds):
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

    @staticmethod
    def redistribute(syllables):
        """
        redistribute the sounds of a list of syllables
        in order to use the correct syllables, not the longest possible
        """
        for count in range(len(syllables) - 1):
            if (count == len(syllables) - 2 and
                    syllables[count + 1] == Syllable('ve')):
                continue
            if (syllables[count].ends_with_vowel() and
                    syllables[count + 1].starts_with_consonant_cluster()):
                SyllableSplitter.__switch_sound(syllables[count], syllables[count + 1], True)
            elif syllables[count].ends_with_consonant():
                if (syllables[count + 1].sounds[0] == SoundFactory.create('u') and
                        len(syllables[count + 1].sounds) > 1 and
                        not syllables[count].ends_with_consonant_cluster() and
                        not syllables[count + 1].sounds[1].is_consonant()):
                    pass
                elif syllables[count + 1].starts_with_vowel(False):
                    SyllableSplitter.__switch_sound(syllables[count], syllables[count + 1], False)
        for syll in syllables:
            syll.recalculate_text()
        return syllables

    @staticmethod
    def __switch_sound(syllable1, syllable2, to_first):
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
            syllable1.sounds = syllable1.sounds[:-1]
            syllable2.sounds.insert(0, given_sound)
