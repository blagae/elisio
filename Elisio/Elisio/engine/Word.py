""" processing unit for Words and lower entities """
from Elisio.engine.Syllable import Syllable, WordAnalyzer, Weight
from Elisio.exceptions import WordException

class Word(object):
    """ Word class
    A word is the representation of the Latin word
    It has extensive knowledge of its sounds, which it can join into syllables
    """
    def __init__(self, text):
        """ construct a Word by its contents """
        self.syllables = []
        if not (isinstance(text, str) and text.isalpha()):
            raise WordException("Word not initialized with alphatic data")
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
        temporary_syllables = WordAnalyzer.join_into_syllables(sounds)
        self.syllables = WordAnalyzer.redistribute(temporary_syllables)
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
        return WordAnalyzer.find_sounds_for_text(self.text)

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
                syll_struct[-1] = Weight.NONE
            elif (last_syllable.ends_with_consonant() and
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
