""" processing unit for Words and lower entities """
import copy
import enum
import re
from Elisio.exceptions import ScansionException

class LetterTypes(enum.Enum):
    """
    The possible types of letters
    """
    VOWEL = 0
    CONSONANT = 1
    SEMIVOWEL = 2
    HEAVYMAKER = 3

class Weights(enum.Enum):
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


class Word(object):
    """ Word class
    A word is the representation of the Latin word
    It has extensive knowledge of its sounds, which it can join into syllables
    """
    # TODO: this breaks a lot of verses with final long e
    # and the Verse tests where e$ is scheduled to be light
    # proposed solution: find deviant word ?
    shortEndVowels = []
    longEndVowels = ['i', 'o', 'u']
    def __init__(self, text):
        """ construct a Word by its contents """
        self.syllables = []
        if not (isinstance(text, str) and text.isalpha()):
            raise ScansionException("Word not initialized with alphatic data")
        self.text = text.lower()

    def __repr__(self):
        return self.syllables
    def __str__(self):
        return self.syllables

    def split(self, test_deviant=True):
        """
        splits a word into syllables by using a few static methods
        from the Syllable class
        """
        if test_deviant and self.split_from_deviant_word():
            return
        sounds = self.find_sounds()
        temporary_syllables = Word.__join_into_syllables(sounds)
        self.syllables = Word.redistribute(temporary_syllables)
        self.check_consistency()

    def split_from_deviant_word(self):
        """
        if the word can be found the repository of Deviant Words,
        we should use that instead
        """
        from Elisio.models import DeviantWord
        deviant = DeviantWord.find(self.text)
        if deviant:
            self.syllables = deviant.get_syllables()
            txt = self.text
            for syll in self.syllables:
                if len(syll.syllable) >= 1:
                    txt = txt[len(syll.syllable):]
            if len(txt) > 0:
                wrd = Word(txt)
                wrd.split(False)
                for syllab in wrd.syllables:
                    self.syllables.append(syllab)
            return True

    def find_sounds(self):
        """
        find the sequence of sounds from the textual representation of the word
        """
        return Word.find_sounds_for_text(self.text)

    def __eq__(self, other):
        """
        Words are equal if they have exactly the same characters
        Case insensitivity is enforced by the constructor
        """
        return self.__dict__ == other.__dict__

    def get_syllable_structure(self, next_word=None):
        """ get the list of syllable weights based on the syllable list """
        syll_struct = []
        if self.syllables == []:
            self.split()
        for count, syllable in enumerate(self.syllables):
            try:
                syll_struct.append(syllable.get_weight(self.syllables[count+1]))
            except IndexError:
                syll_struct.append(syllable.get_weight())
        if next_word and isinstance(next_word, Word):
            # word contact
            last_syllable = self.syllables[-1]
            next_word.split()
            first_syllable = next_word.syllables[0]
            if (last_syllable.can_elide_if_final() and
                    first_syllable.starts_with_vowel()):
                # elision
                syll_struct[-1] = Weights.NONE
            elif (last_syllable.ends_with_consonant() and
                  first_syllable.starts_with_vowel()):
                # consonant de facto redistributed
                syll_struct[-1] = Weights.ANCEPS
            elif (last_syllable.ends_with_vowel() and
                  first_syllable.starts_with_consonant_cluster()):
                syll_struct[-1] = Weights.HEAVY
            if last_syllable == Syllable('que') and syll_struct[-1] != Weights.NONE:
                syll_struct[-1] = Weights.LIGHT
        return syll_struct

    def check_consistency(self):
        """
        see that all syllables are valid
        or fix if necessary
        """
        for syllable in self.syllables:
            if not syllable.is_valid():
                word = Word(syllable.get_text())
                word.split()
                index = self.syllables.index(syllable)
                self.syllables.remove(syllable)
                for syll in reversed(word.syllables):
                    self.syllables.insert(index, syll)

    @classmethod
    def find_sounds_for_text(cls, text):
        """ iteratively allocate all text to a sound """
        i = 0
        sounds = []
        while i < len(text):
            added_sounds = Sound.create_sounds_from_text(text[i:i+3])
            for sound in added_sounds:
                sounds.append(sound)
                i += len(sound.letters)
        return sounds

    @classmethod
    def __join_into_syllables(cls, sounds):
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
            except ScansionException:
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
                Word.__switch_sound(syllables[count], syllables[count+1], True)
            elif (syllables[count].ends_with_consonant() and
                  syllables[count+1].starts_with_vowel(False)):
                Word.__switch_sound(syllables[count], syllables[count+1], False)
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

class Syllable(object):
    """ Syllable class
    A syllable knows its sounds and can determine
    if the specific combination of them is a valid one
    """
    def __init__(self, syllable, test=True, weight=None):
        """ construct a Syllable by its contents """
        self.weight = weight
        self.syllable = syllable
        self.sounds = Word.find_sounds_for_text(syllable)
        if test and not self.is_valid():
            raise ScansionException("invalid Syllable object")

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
                (self.sounds[-1] == Sound.create('m') and
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
        raise ScansionException("no vowel found in Syllable"+str(self.sounds))

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
                vowel.letters[0] in Word.longEndVowels)

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
                self.get_vowel().letters[0] in Word.shortEndVowels
               )

    def add_sound(self, sound):
        """ add a sound to a syllable if the syllable stays
        valid by the addition """
        test_syllable = copy.deepcopy(self)
        test_syllable.sounds.append(sound)
        if test_syllable.is_valid():
            self.sounds.append(sound)
        else:
            raise ScansionException("syllable invalidated by last addition")

    def get_weight(self, next_syllable=None):
        """
        try to determine the weight of the syllable
        in the light of the next syllable
        if this doesn't succeed, assign the weight ANCEPS = undetermined
        """
        if self.weight:
            return self.weight
        if self.is_light(next_syllable):
            return Weights.LIGHT
        elif self.is_heavy(next_syllable):
            return Weights.HEAVY
        else:
            return Weights.ANCEPS

    @classmethod
    def create_syllable_from_database(cls, syll):
        """
        The factory method that will create a syllable from the database
        with its given weight (if stored in the database)
        """
        from Elisio.models import DeviantSyllable
        if not isinstance(syll, DeviantSyllable):
            raise ScansionException("database error with Deviant Syllable")
        result = Syllable(syll.contents, False, syll.weight)
        return result

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
                raise ScansionException("invalid constructor"+str(self.letters))

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

        return Sound.__factory(letterlist)

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

                if lettertype == LetterTypes.VOWEL:
                    sound = VowelSound(item)
                elif lettertype == LetterTypes.CONSONANT:
                    sound = ConsonantSound(item)
                elif lettertype == LetterTypes.SEMIVOWEL:
                    sound = SemivowelSound(item)
                elif lettertype == LetterTypes.HEAVYMAKER:
                    sound = HeavyMakerSound(item)
                else:
                    raise ScansionException("not a valid letter"+str(item))
                # set looping consonant to False
                first = False
            else:
                if sound.is_vowel():
                    sound = Diphthong(sound.letters[0], item)
                if sound.is_consonant():
                    sound.letters.append(item)
        if not sound.is_valid_sound():
            raise ScansionException("not a valid sound given in factory method")
        return sound

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
        return True

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.letters)

    @classmethod
    def create_sounds_from_text(cls, text):
        """
        try to create a Sound from given text string of maximally 3 letters
        this is a classmethod because it acts as a (super-)Factory
        returns an array of sounds
        """
        if len(text) > 3:
            raise ScansionException("too many letters in this text sample")
        elif len(text) == 3:
            # detect intervocalic semivowels
            if re.match("^[aeijouvy][ijuv][aeijouvy]$", text):
                sounds = []
                for i in text:
                    snd = Sound.create(i)
                    sounds.append(snd)
                return sounds
        try:
            sound = Sound.create(text[0:2])
        except ScansionException:
            sound = Sound.create(text[0])
        return [sound]

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
        return Letter.letters[first] == LetterTypes.VOWEL

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
        return Letter.letters[first] == LetterTypes.SEMIVOWEL

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
        return Letter.letters[first] == LetterTypes.CONSONANT

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
        return Letter.letters[first] == LetterTypes.HEAVYMAKER

class Letter(object):
    """
    The Letter class is mostly here to make sure
    only valid letters get passed to the Sound class
    See validity check in constructor
    """
    letters = {
        # This list is sorted by relative prevalence of letters
        # so that the most frequent letters have more optimal search
        'e' : LetterTypes.VOWEL,
        'a' : LetterTypes.VOWEL,
        'i' : LetterTypes.SEMIVOWEL,
        'u' : LetterTypes.SEMIVOWEL,
        't' : LetterTypes.CONSONANT,
        's' : LetterTypes.CONSONANT,
        'r' : LetterTypes.CONSONANT,
        'n' : LetterTypes.CONSONANT,
        'o' : LetterTypes.VOWEL,
        'm' : LetterTypes.CONSONANT,
        'c' : LetterTypes.CONSONANT,
        'l' : LetterTypes.CONSONANT,
        'p' : LetterTypes.CONSONANT,
        'd' : LetterTypes.CONSONANT,
        'q' : LetterTypes.CONSONANT,
        'b' : LetterTypes.CONSONANT,
        'g' : LetterTypes.CONSONANT,
        'f' : LetterTypes.CONSONANT,
        'h' : LetterTypes.CONSONANT,
        'x' : LetterTypes.HEAVYMAKER,
        'y' : LetterTypes.VOWEL,
        'k' : LetterTypes.CONSONANT,
        'z' : LetterTypes.HEAVYMAKER
        }

    def __init__(self, ltr):
        """ construct a Letter by its contents """
        if not (isinstance(ltr, str) and len(ltr) == 1 and ltr.isalpha()):
            raise ScansionException("wrong number of letters " +
                                    "or not a valid character")
        self.letter = ltr.lower()
        if self.letter == 'v':
            self.letter = 'u'
        elif self.letter == 'j':
            self.letter = 'i'
        if not self.is_valid_letter():
            raise ScansionException("not a valid letter")

    def __eq__(self, other):
        """ Letters are equal if they have exactly the same character
        Case insensitivity is enforced by the constructor
        """
        return self.__str__() == other.__str__()

    def __str__(self):
        return self.letter
    def __repr__(self):
        return self.letter

    def get_type(self):
        """ returns the LetterType of this letter """
        return Letter.letters[self.letter]

    def is_valid_letter(self):
        """ a letter is only valid if it figures in the list of legal characters
        currently the only invalid (Roman) letters are W, V and J
        but V and J are replaced by their vocalic values U and I
        in the constructor
        """
        return self.letter in Letter.letters
