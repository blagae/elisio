""" processing unit for Words and lower entities """
from Elisio.engine.Sound import SoundFactory
from Elisio.engine.Syllable import Syllable, SyllableSplitter, Weight
from Elisio.exceptions import WordException

class Word(object):
    """ Word class
    A word is the representation of the Latin word
    It has extensive knowledge of its sounds, which it can join into syllables
    """
    enclitics = ('que', 'ue')
    def __init__(self, text):
        """ construct a Word by its contents """
        self.syllables = []
        if not (isinstance(text, str) and text.isalpha()):
            raise WordException("Word not initialized with alphatic data")
        self.find_sounds(text)
        self.enclitic = None

    def __repr__(self):
        return self.syllables
    def __str__(self):
        return self.syllables

    def find_sounds(self, text):
        """
        find the sequence of sounds from the textual representation of the word
        """
        self.sounds = SoundFactory.find_sounds_for_text(text)
        local_text = ""
        for sound in self.sounds:
            local_text += sound.get_text()
        self.text = local_text

    def split(self, test_deviant=True):
        """
        splits a word into syllables by using a few static methods
        from the Syllable class
        """
        if test_deviant and self.split_from_deviant_word():
            return
        if len(self.syllables) == 0:
            temporary_syllables = SyllableSplitter.join_into_syllables(self.sounds)
            self.syllables = SyllableSplitter.redistribute(temporary_syllables)
            self.check_consistency()
        if test_deviant and len(self.syllables) == 1 and len(self.text) == 1:
            self.syllables[0].weight = Weight.HEAVY

    def ends_in_enclitic(self):
        if self.enclitic:
            return True
        for encl in Word.enclitics:
            if self.text.endswith(encl):
                self.enclitic = encl
                return True
        return False

    def without_enclitic(self):
        if self.ends_in_enclitic():
            stem = self.text[:-len(self.enclitic)]
            return stem
        return self.text

    def split_from_deviant_word(self):
        """
        if the word can be found the repository of Deviant Words,
        we should use that instead
        """
        from Elisio.models import DeviantWord
        deviant = DeviantWord.find(self.without_enclitic())
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
            if len(next_word.syllables) == 0:
                next_word.split()
            first_syllable = next_word.syllables[0]
            if (last_syllable.can_elide_if_final() and
                    first_syllable.starts_with_vowel()):
                # elision
                syll_struct[-1] = Weight.NONE
            # TODO: redefine redistribution ! heavymakers, -os, etc
            elif last_syllable.must_be_heavy():
                syll_struct[-1] = Weight.HEAVY
            elif (last_syllable.ends_with_consonant() and 
                  not last_syllable.ends_with_consonant_cluster() and 
                  first_syllable.starts_with_vowel()):
                # consonant de facto redistributed
                syll_struct[-1] = Weight.ANCEPS
            elif (last_syllable.ends_with_vowel() and
                  first_syllable.starts_with_consonant_cluster()):
                syll_struct[-1] = Weight.HEAVY
            if last_syllable == Syllable('que') and syll_struct[-1] != Weight.NONE:
                syll_struct[-1] = Weight.LIGHT
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
