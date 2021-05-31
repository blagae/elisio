""" processing unit for Words and lower entities """
from typing import Optional
from whitakers_words.parser import Parser

from .bridge import Bridge, DummyBridge
from .exceptions import SyllableException, WordException
from .sound import SoundFactory
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
        # TODO determine if we need all these properties
        self.can_be_name = text.istitle()
        self.whitaker = parser.parse(text, not self.can_be_name)
        self.syllables: list[Syllable] = []
        self.find_sounds(text)
        self.reconstruct_text()
        self.enclitic = self.put_enclitic()

    def __repr__(self) -> str:
        return ''.join(str(x) for x in self.syllables)

    def __eq__(self, other: object) -> bool:
        """
        Words are equal if they have exactly the same characters
        Case insensitivity is enforced by the constructor
        """
        if not isinstance(other, Word):
            return False
        return self.syllables == other.syllables and self.enclitic == other.enclitic

    def __len__(self) -> int:
        if self.syllables:
            return sum(len(syllable) for syllable in self.syllables)
        return sum(len(sound) for sound in self.sounds)

    def find_sounds(self, text: str) -> None:
        self.sounds = SoundFactory.find_sounds_for_text(text)

    def reconstruct_text(self) -> None:
        """
        find the sequence of sounds from the textual representation of the word
        """
        self.text = ''.join(sound.letters for sound in self.sounds)

    def find_proclitic(self) -> str:
        # TODO to be solved by whitaker, after "reduce" logic is implemented
        proclitics = ('ab', 'ad', 'con', 'dis', 'in', 'ob', 'sub')
        for proc in proclitics:
            if self.text.startswith(proc) and self.text != proc:
                return proc
        return ''

    def split(self, bridge: Bridge = DummyBridge()) -> None:
        """
        splits a word into syllables by using a few static methods from the Syllable class
        """
        deviant_syllables = bridge.split_from_deviant_word(self.without_enclitic())
        if deviant_syllables:
            self.syllables = list(deviant_syllables)
            text = self.text[len(self):]
            if text:
                wrd = Word(text)
                wrd.split()
                self.syllables += wrd.syllables
            self.reconstruct_text()
            return
        if not self.syllables:
            temporary_syllables = SyllableSplitter.join_into_syllables(self.sounds)
            self.syllables = SyllableSplitter.redistribute(temporary_syllables)
            self.check_consistency()
        if len(self.syllables) == 1 and len(self.text) == 1:
            self.syllables[0].weight = Weight.HEAVY
        stored_structures = bridge.use_dictionary(self.text)
        self.assign_weights_from_dict(stored_structures)

    def assign_weights_from_dict(self, stored_structures: list[str]) -> None:
        if len(stored_structures):
            for count in range(len(max(stored_structures, key=len))):
                weight = None
                for struct in stored_structures:
                    try:
                        if not weight and struct[count] != "3" and struct[count] != "0":
                            weight = struct[count]
                        elif weight != struct[count]:
                            if struct[count] != "3" and struct[count] != "0":
                                weight = "3"
                                break
                    except IndexError:
                        pass
                if weight and count < len(self.syllables):
                    self.syllables[count].weight = Weight(int(weight))

    def ends_in_variable_declension(self) -> bool:
        return len(self.syllables) > 1 and (self.text.endswith(("us", "a")))  # TODO whitaker

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
        if not self.syllables:
            self.split(bridge)
        for count, syllable in enumerate(self.syllables):
            try:
                syllable.weight = syllable.get_weight(self.syllables[count + 1])
            except IndexError:
                syllable.weight = syllable.get_weight()
        if self.can_be_name:
            for syllable in self.syllables[:-1]:
                if syllable.weight == Weight.LIGHT:
                    syllable.weight = Weight.ANCEPS

    def apply_word_contact(self, next_word: 'Word') -> Optional[Weight]:
        """ See if next word has any influence on the syllable structure """
        final = self.syllables[-1]
        first = next_word.syllables[0]
        if (final.can_elide_if_final() and first.starts_with_vowel()):
            final.alternative_weight = final.weight  # keep the possibility of hiatus alive
            return Weight.NONE  # elision
        if final.must_be_heavy() or (final.ends_with_vowel() and first.starts_with_consonant_cluster()):
            return Weight.HEAVY
        if final.ends_with_consonant():
            if (not final.ends_with_consonant_cluster() and not final.has_diphthong() and first.starts_with_vowel()):
                # consonant de facto redistributed
                if final.get_weight() != Weight.LIGHT:
                    return Weight.ANCEPS
            if first.starts_with_consonant():
                return Weight.HEAVY
        if final == Syllable('que') and final.get_weight() != Weight.NONE:
            return Weight.LIGHT
        return None

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
        proc = self.find_proclitic()
        if proc:
            self.split_proclitic(proc)
        else:
            # recheck to catch a-chi-u-is type errors
            for count, syllable in enumerate(self.syllables):
                if (len(syllable.sounds) == 1 and syllable.sounds[0].is_semivowel() and
                        count < len(self.syllables) - 1 and self.syllables[count + 1].starts_with_vowel()):
                    try:
                        syllable = Syllable(syllable.sounds + self.syllables[count + 1].sounds)
                        self.syllables.remove(self.syllables[count + 1])
                        self.syllables[count] = syllable
                    except SyllableException:
                        pass

    def split_proclitic(self, proc: str) -> None:
        # try to maintain the morpheme boundary
        mainword = self.text.replace(proc, '', 1)
        snd = SoundFactory.create(mainword[0])
        if (snd.is_consonant() or
                (snd.is_semivowel() and len(mainword) > 1 and not SoundFactory.create(mainword[1]).is_consonant())):
            wrd = Word(mainword)
            wrd.split()
            syl = Syllable(proc)
            self.sounds = list(syl.sounds) + wrd.sounds
            self.syllables = [syl] + wrd.syllables
