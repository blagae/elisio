""" processing unit for Words and lower entities """
from Elisio.engine.Sound import SoundFactory
from Elisio.engine.Syllable import Syllable, SyllableSplitter, Weight
from Elisio.exceptions import WordException, SyllableException

class Word(object):
    """ Word class
    A word is the representation of the Latin word
    It has extensive knowledge of its sounds, which it can join into syllables
    """
    enclitics = ('que', 'ue')
    def __init__(self, text, use_dict = False):
        """ construct a Word by its contents """
        self.syllables = []
        if not (isinstance(text, str) and text.isalpha()):
            raise WordException("Word not initialized with alphatic data")
        self.find_sounds(text)
        self.enclitic = None
        self.use_dict = use_dict
        self.name = text.istitle()

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
        if self.use_dict:
            from Elisio.models import WordOccurrence
            structs = []
            for hit in WordOccurrence.objects.filter(word=self.text):
                strc = hit.struct
                if len(strc) == 1 and strc[-1] == "0":
                    continue
                if len(strc) > 1 and (strc[-1] == "3" or strc[-1] == "0"):
                    strc = strc[:-1]
                if not strc in structs:
                    structs.append(strc)
            if len(structs) == 1:
                for count, wght in enumerate(structs[0]):
                    self.syllables[count].weight = Weight(int(wght))
            if len(structs) > 1:
                structs.sort(key=len, reverse=True)
                for count in range(len(structs[0])):
                    val = None
                    for strc in structs:
                        try:
                            if not val and (strc[count] != "3" and strc[count] != "0"):
                                val = strc[count]
                            elif val != strc[count]:
                                if strc[count] != "3" and strc[count] != "0":
                                    val = None
                                    break
                                    #raise WordException("different occurrences have different qualities")
                        except IndexError:
                            pass
                    if val:
                        self.syllables[count].weight = Weight(int(val))

    def ends_in_variable_declension(self):
        return self.text.endswith("us") or self.text.endswith("a")

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

    def may_be_heavy_by_position(self, next_word):
        return (self.syllables[-1].is_heavy() and
                ((next_word.syllables[0].starts_with_consonant_cluster() and
                  self.syllables[-1].ends_with_vowel()) or
                 (self.syllables[-1].ends_with_consonant() and
                  next_word.syllables[0].starts_with_consonant()
                  )))

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
            elif last_syllable.ends_with_consonant():
                if (not last_syllable.ends_with_consonant_cluster() and 
                   not last_syllable.has_diphthong() and
                   first_syllable.starts_with_vowel()):
                    # consonant de facto redistributed
                    syll_struct[-1] = Weight.ANCEPS
                elif first_syllable.starts_with_consonant():
                    syll_struct[-1] = Weight.HEAVY
            elif (last_syllable.ends_with_vowel() and
                  first_syllable.starts_with_consonant_cluster()):
                syll_struct[-1] = Weight.HEAVY
            if last_syllable == Syllable('que') and syll_struct[-1] != Weight.NONE:
                syll_struct[-1] = Weight.LIGHT
        if self.name:
            for count in range(len(syll_struct)-1):
                if syll_struct[count] == Weight.LIGHT:
                    syll_struct[count] = Weight.ANCEPS
        for count, syll in enumerate(self.syllables):
            syll.weight = syll_struct[count]
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
        # recheck to catch a-chi-u-is type errors
        for count, syllable in enumerate(self.syllables):
            if len(syllable.sounds) == 1 and syllable.sounds[0].is_semivowel():
                if count < len(self.syllables) - 1 and self.syllables[count + 1].starts_with_vowel():
                    try:
                        syllable = Syllable(syllable.get_text() + self.syllables[count + 1].get_text())
                        self.syllables.remove(self.syllables[count + 1])
                        self.syllables[count] = syllable
                    except SyllableException:
                        pass
