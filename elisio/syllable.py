from enum import Enum

from .exceptions import SyllableException
from .sound import Sound, SoundFactory


class Weight(Enum):
    """
    The possible types of syllable weights
    """
    NONE = 0
    LIGHT = 1
    HEAVY = 2
    ANCEPS = 3


class Syllable:
    """ Syllable class
    A syllable knows its sounds and can determine if the specific combination of them is a valid one
    """
    def __init__(self, text: str, validate: bool = True, weight: Weight = None):
        """ construct a Syllable by its contents """
        self.weight = weight
        self.stressed = False
        self.text = text
        self.fill_sounds(text, validate)
        self.recalculate_text()

    def __eq__(self, other: object) -> bool:
        return self.sounds == other.sounds

    def __repr__(self) -> str:
        return str(self.sounds)

    def recalculate_text(self) -> None:
        result = ""
        for sound in self.sounds:
            result += sound.letters
        self.text = result

    def copy_me(self) -> 'Syllable':
        other = Syllable(self.text, False, self.weight)
        other.stressed = self.stressed
        other.sounds = [x for x in self.sounds]
        other.text = self.text
        return other

    def fill_sounds(self, text: str, validate: bool) -> None:
        self.sounds = SoundFactory.find_sounds_for_text(text)
        if validate and not self.is_valid():
            raise SyllableException("invalid Syllable object")

    def is_valid(self, test: bool = False) -> bool:
        """
        a syllable is valid if it contains:
            * at most one consonant after the vocalic sound, and
            * a single vowel or semivowel
            * a semivowel and a vowel in that order
        """
        sounds = self.sounds
        if len(sounds) > 1 and sounds[0] == sounds[1] and sounds[0].letters == 'i':
            return False
        if sounds[0].letters == 'gu':
            copied = self.copy_me()
            copied.sounds[0] = SoundFactory.create('u')
            valid = copied.is_valid(test)
            if valid:
                sounds[0] = SoundFactory.create('g')
                sounds.insert(1, SoundFactory.create('u'))
            return valid
        contains_final_consonant = contains_vowel = contains_semivowel = False
        only_consonants = True
        for count, sound in enumerate(sounds):
            if sound.is_consonant():
                if contains_vowel or contains_semivowel:
                    if sound.letters == 'gu':
                        return False
                    contains_final_consonant = True
            elif sound.is_vowel():
                if contains_vowel or (contains_final_consonant and contains_semivowel):
                    return False
                contains_vowel = True
                only_consonants = False
            elif sound.is_semivowel():
                if contains_vowel or (contains_final_consonant and contains_semivowel):
                    return False
                if count > 0:
                    contains_vowel = True
                contains_semivowel = True
                only_consonants = False
        return contains_vowel or contains_semivowel or (only_consonants == test)

    def ends_with_consonant(self) -> bool:
        """ last sound of the syllable is consonantal """
        return self.sounds[-1].is_consonant()

    def ends_with_consonant_cluster(self) -> bool:
        return len(self.sounds) > 1 and self.ends_with_consonant() and self.sounds[-2].is_consonant()

    def must_be_heavy(self) -> bool:
        if self.ends_with_heavymaker():
            return True
        return False

    def ends_with_heavymaker(self) -> bool:
        """ last sound of the syllable is consonantal """
        return self.sounds[-1].is_heavy_making()

    def can_elide_if_final(self) -> bool:
        """ special property of words ending in a vowel """
        return self.ends_with_vowel() or self.ends_with_vowel_and_m()

    def ends_with_vowel_and_m(self) -> bool:
        return self.sounds[-1].letters == 'm' and (self.sounds[-2].is_vowel() or self.sounds[-2].is_semivowel())

    def has_diphthong(self) -> bool:
        return self.get_vowel().is_diphthong()

    def ends_with_vowel(self) -> bool:
        """
        last sound of the syllable is vocalic
        a final semivowel is always vocalic
        """
        return self.sounds[-1].is_vowel() or self.sounds[-1].is_semivowel()

    def starts_with_vowel(self, initial: bool = True) -> bool:
        """
        first sound of the syllable is vocalic
        an initial semivowel is only vocalic if it is the syllable's only sound
        or if it is followed directly by a consonant
        """
        if self.sounds[0].is_vowel():
            return True
        if self.sounds[0].is_h() and len(self.sounds) > 1 and not self.sounds[1].is_consonant():
            return True
        return self.sounds[0].is_semivowel() and (not initial or len(self.sounds) == 1 or self.sounds[1].is_consonant())

    def starts_with_consonant(self, initial: bool = True) -> bool:
        """
        first sound of the syllable is consonantal
        an initial semivowel is consonantal if it is followed by a vowel
        """
        return not self.starts_with_vowel(initial)

    def starts_with_consonant_cluster(self) -> bool:
        """ first sounds of the syllable are all consonants """
        return (self.starts_with_consonant() and self.sounds[0].letters != 'gu' and
                ((len(self.sounds) > 1 and self.sounds[1].is_consonant()) or self.makes_previous_heavy()))

    def makes_previous_heavy(self) -> bool:
        """ first sound of the syllable is a double consonant letter """
        return self.sounds[0].is_heavy_making()

    def get_vowel_location(self) -> int:
        for idx, sound in enumerate(reversed(self.sounds)):
            if sound.is_vowel() or sound.is_semivowel():
                return len(self.sounds) - idx - 1
        raise SyllableException("no vowel found in Syllable" + str(self.sounds))

    def get_vowel(self) -> Sound:
        """ get the vocalic sound from a syllable """
        return self.sounds[self.get_vowel_location()]

    def is_heavy(self, next_syllable: 'Syllable' = None) -> bool:
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
            if next_syllable.sounds[0].is_h():
                return self.ends_with_consonant_cluster() or self.ends_with_heavymaker()
            return ((self.ends_with_consonant() or next_syllable.makes_previous_heavy()) or
                    (not self.is_light(next_syllable) and vowel.is_diphthong()))
        return self.ends_with_consonant() or vowel.is_diphthong()

    def must_be_anceps(self, next_syllable: 'Syllable' = None) -> bool:
        if next_syllable and isinstance(next_syllable, Syllable):
            return self.ends_with_vowel() and self.get_vowel().is_diphthong() and next_syllable.starts_with_vowel()
        return False

    def is_light(self, next_syllable: 'Syllable' = None) -> bool:
        """
        determines whether the syllable is inherently light or not
        a syllable is always light if it ends in a vowel
        and is followed by a vowel in the next syllable
        final E is usually short
        """
        if next_syllable and isinstance(next_syllable, Syllable):
            return self.ends_with_vowel() and next_syllable.starts_with_vowel()
        return False

    def add_sound(self, sound: Sound) -> None:
        """ add a sound to a syllable if the syllable stays
        valid by the addition """
        test_syllable = self.copy_me()
        test_syllable.sounds.append(sound)
        if test_syllable.is_valid(True):
            self.sounds.append(sound)
        else:
            raise SyllableException("syllable invalidated by last addition")

    def get_weight(self, next_syllable: 'Syllable' = None) -> Weight:
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
        if self.is_heavy(next_syllable):
            self.weight = Weight.HEAVY
            return Weight.HEAVY
        return Weight.ANCEPS


class SyllableSplitter:

    @staticmethod
    def split_from_text(text: str) -> list[Syllable]:
        sounds = SoundFactory.find_sounds_for_text(text)
        sylls = SyllableSplitter.join_into_syllables(sounds)
        return SyllableSplitter.redistribute(sylls)

    @staticmethod
    def join_into_syllables(sounds: list[Sound]) -> list[Syllable]:
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
    def redistribute(syllables: list[Syllable]) -> list[Syllable]:
        """
        redistribute the sounds of a list of syllables
        in order to use the correct syllables, not the longest possible
        """
        for count in range(len(syllables) - 1):
            # TODO good location for whitaker (enclitic finder) ?
            if (count == len(syllables) - 2 and syllables[count + 1] == Syllable('ve')):
                continue
            if (syllables[count].ends_with_vowel() and syllables[count + 1].starts_with_consonant_cluster()):
                SyllableSplitter.__switch_sound(syllables[count], syllables[count + 1], True)
            elif syllables[count].ends_with_consonant():
                if (syllables[count + 1].sounds[0].letters == 'u' and len(syllables[count + 1].sounds) > 1 and
                        not syllables[count].ends_with_consonant_cluster() and
                        not syllables[count + 1].sounds[1].is_consonant()):
                    if not syllables[count].sounds[-1].letters in ['r', 'l']:
                        SyllableSplitter.__switch_sound(syllables[count], syllables[count + 1], False)
                elif syllables[count + 1].starts_with_vowel(False):
                    SyllableSplitter.__switch_sound(syllables[count], syllables[count + 1], False)
        local_sylls = []
        for syll in syllables:
            if not syll.is_valid():
                syll.recalculate_text()
                sounds = SoundFactory.find_sounds_for_text(syll.text)
                sylls = SyllableSplitter.join_into_syllables(sounds)
                for s in sylls:
                    if not s.is_valid():
                        raise SyllableException("unparseable syllable")
                local_sylls.extend(sylls)
            else:
                local_sylls.append(syll)
        for syll in local_sylls:
            syll.recalculate_text()
        return local_sylls

    @staticmethod
    def __switch_sound(syllable1: Syllable, syllable2: Syllable, to_first: bool) -> None:
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
