""" the main module for parsing verses """
from enum import Enum
from typing import Any, Union

from ..bridge import Bridge
from ..exceptions import IllegalFootException, VerseException
from ..sound import SoundFactory
from ..syllable import Weight
from ..word import Word


class Foot(Enum):
    """ Types of verse foot """
    UNKNOWN = 0
    MACRON = 1
    BREVE = 2
    SPONDAEUS = 3
    TROCHAEUS = 4
    BINARY_ANCEPS = 5
    IAMBUS = 6
    PYRRHICUS = 7
    DACTYLUS = 8

    def get_length(self) -> int:
        """ number of syllables in the foot """
        return len(self.get_structure())

    def get_structure(self) -> list[Weight]:
        """ available foot structures """
        if self == Foot.DACTYLUS:
            return [Weight.HEAVY, Weight.LIGHT, Weight.LIGHT]
        elif self == Foot.SPONDAEUS:
            return [Weight.HEAVY, Weight.HEAVY]
        elif self == Foot.TROCHAEUS:
            return [Weight.HEAVY, Weight.LIGHT]
        elif self == Foot.BINARY_ANCEPS:
            return [Weight.HEAVY, Weight.ANCEPS]
        elif self == Foot.MACRON:
            return [Weight.HEAVY]
        raise IllegalFootException("currently illegal foot structure: " + self.name)


class Verse:
    """ Verse class
    A verse is the representation of the Latin text of a verse
    It has no knowledge of its surroundings or context
    """

    def __init__(self, text: str):
        """ construct a Verse by its contents """
        if not isinstance(text, str):
            raise VerseException("Verse must be initialized with text data")
        self.text = text
        self.words: list[Word] = []
        self.flat_list: list[Weight] = []
        self.feet: list[Union[None, Foot]] = []
        self.structure = ''

    def __repr__(self) -> str:
        return ''.join(str(x) for x in self.words)

    def __eq__(self, other: object) -> bool:
        """ Verses are equal if they have exactly the same characters """
        return self.text == other.text

    def parse(self) -> None:
        self.preparse()
        self.scan()
        self.save_structure()
        self.save_feet()
        self.add_accents()

    def save(self, db_id: int, bridge: Bridge) -> None:
        entries: list[Any] = []
        for count, wrd in enumerate(self.words):
            strct = ""
            txt = wrd.text
            for cnt, syll in enumerate(wrd.syllables):
                if syll.weight:
                    strct += str(syll.weight.value)
                else:
                    strct += ' '
                if cnt == len(wrd.syllables) - 1 and count < len(self.words) - 1:
                    if wrd.may_be_heavy_by_position(self.words[count + 1]):
                        if syll.weight != Weight.NONE:
                            strct = strct[:-1]
                            strct += str(Weight.ANCEPS.value)
            if wrd.ends_in_enclitic():
                strct = strct[:-1]
                txt = wrd.without_enclitic()
                if strct[-1] == str(Weight.HEAVY.value):
                    ltr = SoundFactory.create(txt[-1])
                    if ltr.is_consonant() and not ltr.is_heavy_making():
                        strct = strct[:-1]
                        strct += str(Weight.ANCEPS.value)
            if wrd.ends_in_variable_declension():
                strct = strct[:-1]
                strct += str(Weight.ANCEPS.value)
            entries.append(bridge.make_entry(txt, strct, db_id))
        if len(entries) > 0:
            bridge.dump(entries)

    def add_accents(self) -> None:
        for wrd in self.words:
            if len(wrd.syllables) < 3:
                wrd.syllables[0].stressed = True
            else:
                if wrd.syllables[-2].weight == Weight.HEAVY:
                    wrd.syllables[-2].stressed = True
                else:
                    wrd.syllables[-3].stressed = True

    def preparse(self) -> None:
        raise Exception("must be overridden")

    def scan(self) -> None:
        raise Exception("must be overridden")

    def save_structure(self) -> None:
        # control mechanism and syllable filler
        start = 0
        for feet_num, foot in enumerate(self.feet):
            if foot is None:
                raise VerseException("impossible to determine foot"
                                     " number {0}".format(feet_num))
            for count, weight in enumerate(foot.get_structure()):
                if (weight != Weight.ANCEPS and
                    self.flat_list[count + start] != Weight.ANCEPS and
                        weight != self.flat_list[count + start]):
                    raise VerseException("weight #{0} was already {1}"
                                         ", tried to assign {2}"
                                         .format(count + start,
                                                 str(self.flat_list[count + start]),
                                                 str(weight)))
                self.flat_list[count + start] = weight
            start += foot.get_length()
        i = 0
        for word in self.words:
            for syll in word.syllables:
                if syll.weight != Weight.NONE:
                    syll.weight = self.flat_list[i]
                    i += 1

    def save_feet(self) -> None:
        result = ""
        for foot in self.feet:
            if foot:
                result += str(foot.value)
            else:
                result += ' '
        self.structure = result

    def get_zeleny_score(self) -> list[int]:
        score = []
        current = 0
        for word in self.words:
            for syll in word.syllables:
                if current > 0 and syll.stressed:
                    score.append(current)
                    current = 0
                if syll.weight == Weight.NONE:
                    continue
                elif syll.weight == Weight.LIGHT:
                    current += 1
                else:
                    current += 2
        score.append(current)
        return score
