""" processing unit for Words and lower entities """
from whitakers_words.parser import Parser

from .bridge import Bridge, DummyBridge
from .exceptions import SyllableException, WordException
from .sound import Sound, SoundFactory
from .syllable import Syllable, SyllableSplitter, Weight


class Word:
    """ Word class
    A word is the representation of the Latin word
    It has extensive knowledge of its sounds, which it can join into syllables
    """
    def __init__(self, text: str, parser: Parser = Parser(frequency="X")):
        """ construct a Word by its contents """
        if not (isinstance(text, str) and text.isalpha()):
            raise WordException("Word not initialized with alphabetic data")
        self.whitaker = parser.parse(text)
        self.syllables: list[Syllable] = []
        self.sounds = SoundFactory.find_sounds_for_text(text)
        self.text = Word.reconstruct_text(self.sounds)
        self.enclitic = self.put_enclitic()
        self.istitle = text.istitle()

    def __repr__(self) -> str:
        return ''.join(str(x) for x in self.syllables)

    def __str__(self) -> str:
        return self.__repr__()

    def __eq__(self, other: object) -> bool:
        """
        Words are equal if they have exactly the same characters
        Case insensitivity is enforced by the constructor
        """
        if not isinstance(other, Word):
            return False
        return self.syllables == other.syllables and self.enclitic == other.enclitic

    def recalculate_text(self) -> None:
        self.text = Word.reconstruct_text(self.sounds)

    @staticmethod
    def reconstruct_text(sounds: list[Sound]) -> str:
        """
        find the sequence of sounds from the textual representation of the word
        """
        local_text = ""
        for sound in sounds:
            local_text += sound.letters
        return local_text

    def starts_with_proclitic(self) -> str:
        # TODO to be solved by whitaker, after "reduce" logic is implemented
        proclitics = ('ab', 'ad', 'con', 'dis', 'in', 'ob', 'sub')  # circum?, de?, e-?,ob?per?prae?pro?
        for proc in proclitics:
            if self.text.startswith(proc) and self.text != proc:
                return proc
        return ''

    def split(self, bridge: Bridge = DummyBridge()) -> None:
        """
        splits a word into syllables by using a few static methods
        from the Syllable class
        """
        deviant_syllables = bridge.split_from_deviant_word(self.without_enclitic())
        if deviant_syllables:
            self.syllables = deviant_syllables
            text = self.text
            num = 0
            for syll in self.syllables:
                num += sum(len(x.letters) for x in syll.sounds)
            text = text[num:]
            if len(text) > 0:
                wrd = Word(text)
                wrd.split()
                for syllab in wrd.syllables:
                    self.syllables.append(syllab)
            self.recalculate_text()
            return
        if len(self.syllables) == 0:
            temporary_syllables = SyllableSplitter.join_into_syllables(self.sounds)
            self.syllables = SyllableSplitter.redistribute(temporary_syllables)
            self.check_consistency()
        if len(self.syllables) == 1 and len(self.text) == 1:
            self.syllables[0].weight = Weight.HEAVY
        structs = bridge.use_dictionary(self.text)
        self.assign_weights_from_dict(structs)

    def assign_weights_from_dict(self, structs: list[str]) -> None:
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

    def ends_in_variable_declension(self) -> bool:
        return len(self.syllables) > 1 and (self.text.endswith(("us", "a")))

    def ends_in_enclitic(self) -> bool:
        """ for now, use the longest enclitic that can be analyzed """
        return any((x.enclitic for x in self.whitaker.forms))

    def without_enclitic(self) -> str:
        """ for now, use the longest enclitic that can be analyzed """
        if self.enclitic:
            return self.text[:-len(self.enclitic)]
        return self.text

    def put_enclitic(self) -> str:
        """ for now, use the longest enclitic that can be analyzed """
        return max([x.enclitic.text for x in self.whitaker.forms if x.enclitic], key=len, default='')

    def may_be_heavy_by_position(self, next_word: 'Word') -> bool:
        return (self.syllables[-1].is_heavy() and
                ((next_word.syllables[0].starts_with_consonant_cluster() and self.syllables[-1].ends_with_vowel()) or
                 (self.syllables[-1].ends_with_consonant() and next_word.syllables[0].starts_with_consonant())))

    def analyze_structure(self, bridge: Bridge) -> None:
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

    def apply_word_contact(self, next_word: 'Word') -> None:
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

    def get_syllable_structure(self) -> list[Weight]:
        result = []
        for count, syll in enumerate(self.syllables):
            try:
                result.append(syll.get_weight(self.syllables[count+1]))
            except IndexError:
                result.append(syll.get_weight())
        return result

    def check_consistency(self) -> None:
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
            if not syllable.is_valid():
                word = FallbackWord(syllable.sounds)
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
                        syllable = Syllable(syllable.sounds + self.syllables[count + 1].sounds)
                        self.syllables.remove(self.syllables[count + 1])
                        self.syllables[count] = syllable
                    except SyllableException:
                        pass


class FallbackWord(Word):
    def __init__(self, text: list[Sound]):
        super().__init__(''.join(sound.letters for sound in text))

    def check_consistency(self) -> None:
        pass
