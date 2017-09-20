﻿""" processing unit for Words and lower entities """
from Elisio.engine.Sound import SoundFactory
from Elisio.engine.Syllable import Syllable, SyllableSplitter, Weight
from Elisio.exceptions import WordException, SyllableException


class Word(object):
    """ Word class
    A word is the representation of the Latin word
    It has extensive knowledge of its sounds, which it can join into syllables
    """
    enclitics = ('que', 'ue')
    proclitics = ('ab', 'ad', 'con', 'dis', 'in', 'ob', 'sub')  # circum?, de?, e-?,ob?per?prae?pro?

    def __init__(self, text, use_dict=False):
        """ construct a Word by its contents """
        if not (isinstance(text, str) and text.isalpha()):
            raise WordException("Word not initialized with alphatic data")
        self.syllables = []
        self.sounds = SoundFactory.find_sounds_for_text(text)
        self.text = Word.reconstruct_text(self.sounds)
        self.enclitic = None
        self.use_dict = use_dict

    def __repr__(self):
        return self.syllables

    def __str__(self):
        return self.syllables

    def recalculate_text(self):
        self.text = Word.reconstruct_text(self.sounds)

    @staticmethod
    def reconstruct_text(sounds):
        """
        find the sequence of sounds from the textual representation of the word
        """
        local_text = ""
        for sound in sounds:
            local_text += sound.get_text()
        return local_text

    def starts_with_proclitic(self):
        for proc in Word.proclitics:
            if self.text.startswith(proc) and self.text != proc:
                return proc

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
                if strc not in structs:
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
                                    val = "3"
                                    break
                        except IndexError:
                            pass
                    if val:
                        self.syllables[count].weight = Weight(int(val))

    def ends_in_variable_declension(self):
        return len(self.syllables) > 1 and (self.text.endswith(("us", "a")))

    def ends_in_enclitic(self):
        if self.enclitic:
            return True
        # catch isolated -que
        if self.text in Word.enclitics:
            return False
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
            for syll in self.syllables:
                if len(syll.text) >= 1:
                    self.text = self.text[len(syll.text):]
            if len(self.text) > 0:
                wrd = Word(self.text)
                wrd.split(False)
                for syllab in wrd.syllables:
                    self.syllables.append(syllab)
            self.recalculate_text()
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
        if not self.syllables:
            self.split()
        for count, syllable in enumerate(self.syllables):
            try:
                syll_struct.append(syllable.get_weight(self.syllables[count + 1]))
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
            elif last_syllable.must_be_heavy():
                syll_struct[-1] = Weight.HEAVY
            elif last_syllable.ends_with_consonant():
                if (not last_syllable.ends_with_consonant_cluster() and
                        not last_syllable.has_diphthong() and
                        first_syllable.starts_with_vowel()):
                    # consonant de facto redistributed
                    if syll_struct[-1] != Weight.LIGHT:
                        syll_struct[-1] = Weight.ANCEPS
                elif first_syllable.starts_with_consonant():
                    syll_struct[-1] = Weight.HEAVY
            elif (last_syllable.ends_with_vowel() and
                  first_syllable.starts_with_consonant_cluster()):
                syll_struct[-1] = Weight.HEAVY
            if last_syllable == Syllable('que') and syll_struct[-1] != Weight.NONE:
                syll_struct[-1] = Weight.LIGHT
        if self.text.istitle():
            for count in range(len(syll_struct) - 1):
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
        proc = self.starts_with_proclitic()
        if proc:
            mainword = self.text.replace(proc, '', 1)
            snd = SoundFactory.create(mainword[0])
            if (snd.is_consonant() or
                    (snd.is_semivowel() and not SoundFactory.create(mainword[1]).is_consonant())):
                wrd = Word(mainword)
                wrd.split()
                syl = Syllable(proc)
                self.sounds = syl.sounds.copy()
                self.sounds += wrd.sounds
                self.syllables = [syl]
                self.syllables += wrd.syllables
                return
        for syllable in self.syllables:
            if not Syllable.is_valid(syllable.sounds):
                word = FallbackWord(syllable.text)
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
                        syllable = Syllable(syllable.text + self.syllables[count + 1].text)
                        self.syllables.remove(self.syllables[count + 1])
                        self.syllables[count] = syllable
                    except SyllableException:
                        pass


class FallbackWord(Word):
    def __init__(self, text, use_dict=False):
        super(FallbackWord, self).__init__(text, use_dict)

    def check_consistency(self):
        pass
