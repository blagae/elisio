""" processing unit for Words and lower entities """
from Elisio.engine.Sound import SoundFactory
from Elisio.engine.Syllable import Syllable, SyllableSplitter, Weight
from Elisio.engine.bridge.Bridge import DummyBridge
from Elisio.engine.exceptions import WordException, SyllableException


class Word(object):
    """ Word class
    A word is the representation of the Latin word
    It has extensive knowledge of its sounds, which it can join into syllables
    """
    enclitics = (Syllable('que'), Syllable('ue'))
    proclitics = (Syllable('ab'), Syllable('ad'), Syllable('con'), Syllable('dis'), Syllable('in')
                  , Syllable('ob'), Syllable('sub'))  # circum?, de?, e-?,ob?per?prae?pro?

    def __init__(self, text):
        """ construct a Word by its contents """
        if not (isinstance(text, str) and text.isalpha()):
            raise WordException("Word not initialized with alphatic data")
        self.syllables = []
        self.sounds = SoundFactory.find_sounds_for_text(text)
        self.text = Word.reconstruct_text(self.sounds)
        self.enclitic = None
        self.istitle = text.istitle()

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
            if self.text.startswith(proc.text) and self.text != proc.text:
                return proc.text

    def split(self, bridge=DummyBridge()):
        """
        splits a word into syllables by using a few static methods
        from the Syllable class
        """
        if bridge.split_from_deviant_word(self):
            return
        if len(self.syllables) == 0:
            temporary_syllables = SyllableSplitter.join_into_syllables(self.sounds)
            self.syllables = SyllableSplitter.redistribute(temporary_syllables)
            self.check_consistency()
        if len(self.syllables) == 1 and len(self.text) == 1:
            self.syllables[0].weight = Weight.HEAVY
        bridge.use_dictionary(self)

    def ends_in_variable_declension(self):
        return len(self.syllables) > 1 and (self.text.endswith(("us", "a")))

    def ends_in_enclitic(self):
        if self.enclitic:
            return True
        # catch isolated -que
        if len(self.syllables) == 1 and self.syllables[0] in Word.enclitics:
            return False
        elif not self.syllables and self.text in (x.text for x in Word.enclitics):
            return False
        for encl in Word.enclitics:
            if self.text.endswith(encl.text):
                self.enclitic = encl.text
                return True
        return False

    def without_enclitic(self):
        if self.ends_in_enclitic():
            stem = self.text[:-len(self.enclitic)]
            return stem
        return self.text

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

    def analyze_structure(self, bridge):
        """ Get the syllable structure, regardless of word contact """
        syll_struct = []
        if not self.syllables:
            self.split(bridge)
        for count, syllable in enumerate(self.syllables):
            try:
                syll_struct.append(syllable.get_weight(self.syllables[count + 1]))
            except IndexError:
                syll_struct.append(syllable.get_weight())
        if self.istitle:
            for count in range(len(syll_struct) - 1):
                if syll_struct[count] == Weight.LIGHT:
                    syll_struct[count] = Weight.ANCEPS
        for count, syll in enumerate(self.syllables):
            syll.weight = syll_struct[count]

    def apply_word_contact(self, next_word):
        """ See if next word has any influence on the syllable structure """
        if not isinstance(next_word, Word):
            raise WordException("Cannot compare if next_word is not a Word")
        last_syllable = self.syllables[-1]
        first_syllable = next_word.syllables[0]
        if (last_syllable.can_elide_if_final() and
                first_syllable.starts_with_vowel()):
            # elision
            last_syllable.weight = Weight.NONE
        elif last_syllable.must_be_heavy():
            last_syllable.weight = Weight.HEAVY
        elif last_syllable.ends_with_consonant():
            if (not last_syllable.ends_with_consonant_cluster() and
                    not last_syllable.has_diphthong() and
                    first_syllable.starts_with_vowel()):
                # consonant de facto redistributed
                if last_syllable.get_weight() != Weight.LIGHT:
                    last_syllable.weight = Weight.ANCEPS
            elif first_syllable.starts_with_consonant():
                last_syllable.weight = Weight.HEAVY
        elif (last_syllable.ends_with_vowel() and
              first_syllable.starts_with_consonant_cluster()):
            last_syllable.weight = Weight.HEAVY
        if last_syllable == Syllable('que') and last_syllable.get_weight() != Weight.NONE:
            last_syllable.weight = Weight.LIGHT

    def get_syllable_structure(self):
        result = []
        for count, syll in enumerate(self.syllables):
            try:
                result.append(syll.get_weight(self.syllables[count+1]))
            except IndexError:
                result.append(syll.get_weight())
        return result

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
                    (snd.is_semivowel() and len(mainword) > 1 and not SoundFactory.create(mainword[1]).is_consonant())):
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
    def __init__(self, text):
        super().__init__(text)

    def check_consistency(self):
        pass
