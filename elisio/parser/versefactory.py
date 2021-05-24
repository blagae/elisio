import re
from collections.abc import Iterable
from enum import Enum
from itertools import product as cartesian_product
from typing import Callable, Optional, Sequence, Type

from ..bridge import Bridge, DummyBridge
from ..exceptions import ScansionException, VerseException
from ..syllable import Syllable
from ..word import Weight, Word
from .hendeca import get_hendeca_subtype
from .hexameter import get_hexa_subtype
from .pentameter import get_penta_subtype
from .verse import Verse


VerseCreator = Callable[[list[Weight]], Type[Verse]]


class VerseType(Enum):
    UNKNOWN = 0
    HEXAMETER = 1
    PENTAMETER = 2
    HENDECASYLLABUS = 3

    def get_creators(self) -> list[VerseCreator]:
        if self == VerseType.HEXAMETER:
            return [get_hexa_subtype]
        if self == VerseType.PENTAMETER:
            return [get_penta_subtype]
        if self == VerseType.HENDECASYLLABUS:
            return [get_hendeca_subtype]
        return [get_hexa_subtype, get_penta_subtype]


class VerseForm(Enum):
    UNKNOWN = 0
    HEXAMETRIC = 1
    ELEGIAC_DISTICHON = 2
    HENDECASYLLABUS = 3

    def get_verse_types(self) -> list[VerseType]:
        if self == VerseForm.UNKNOWN:
            return [VerseType.UNKNOWN]
        if self == VerseForm.HEXAMETRIC:
            return [VerseType.HEXAMETER]
        if self == VerseForm.ELEGIAC_DISTICHON:
            return [VerseType.HEXAMETER, VerseType.PENTAMETER]
        if self == VerseForm.HENDECASYLLABUS:
            return [VerseType.HENDECASYLLABUS]
        return [VerseType.UNKNOWN]


class VerseFactory:
    """ Static factory method container for verse creation.
    The methods delegate pre-analysis work to the VersePreprocessor class,
    which in turn delegates actual Verse object creation to a VerseCreator class.
    """
    @staticmethod
    def split(text: str, bridge: Bridge = DummyBridge(), creators: Sequence[VerseType] = []) -> list[Word]:
        return VersePreprocessor(text, bridge, creators).split()

    @staticmethod
    def layer(text: str, bridge: Bridge = DummyBridge(), creators: Sequence[VerseType] = []) -> list[list[Weight]]:
        return VersePreprocessor(text, bridge, creators).layer()

    @staticmethod
    def create(text: str, db_id: int = 0, bridge: Bridge = DummyBridge(), creators: Sequence[VerseType] = []) -> Verse:
        return VersePreprocessor(text, bridge, creators).create_verse(db_id)


class VersePreprocessor:
    """ The verse preprocessor will do the heavy lifting of analyzing words and their structure.
    This happens in 5 steps:
    * split the verse into words
    * find the syllable lengths of the words
    * store the syllable lengths in a one-dimensional list
    * determine which Verse subtype should be created, according to given Verse type(s)
    * try to create the verse, and throw if impossible for the given Verse type

    In practice, the step that determines the subtype is delegated to a VerseCreator
    """
    def __init__(self, verse: str, bridge: Bridge = DummyBridge(), creators: Sequence[VerseType] = []):
        self.verse = verse
        self.bridge = bridge
        self.words: list[Word] = []
        self.creators: set[VerseCreator]
        # https://docs.python.org/3/tutorial/controlflow.html#default-argument-values
        if isinstance(creators, VerseType):
            self.creators = set(creators.get_creators())
        elif isinstance(creators, Iterable):
            self.creators = set()
            for creator in creators:
                self.creators.update(creator.get_creators())
        else:
            self.creators = set(VerseType.UNKNOWN.get_creators())

    def split(self) -> list[Word]:
        """ Split a Verse into Words, remembering only the letter characters """
        array = re.split('[^a-zA-Z]+', self.verse.strip())
        for word in array:
            if word.isalpha():
                self.words.append(Word(word))
        return self.words

    def layer(self) -> list[list[Weight]]:
        """ get available weights of syllables """
        self.split()
        for word in self.words:
            word.analyze_structure(self.bridge)
        for count, word in enumerate(self.words[:-1]):
            new_weight = word.apply_word_contact(self.words[count + 1])
            if new_weight:
                word.syllables[-1].weight = new_weight
        return [word.get_syllable_structure() for word in self.words]

    def get_flat_lists(self) -> list[list[Optional[Weight]]]:
        self.layer()
        flat_lists: list[list[Optional[Weight]]] = []
        flat_list: list[Syllable] = []

        for word in self.words:
            flat_list += [syll for syll in word.syllables]
        permutations = [idx for idx, syll in enumerate(flat_list) if syll.get_alternative_weight()]
        for a in range(2**len(permutations)):
            flat_lists.append(list(syll.weight for syll in flat_list))
        prod = list(cartesian_product(*[[False, True]] * len(permutations)))
        for count, lst in enumerate(flat_lists):
            for x, perm in enumerate(permutations):
                if prod[count][x]:
                    lst[perm] = flat_list[perm].get_alternative_weight()
        for i in range(len(flat_lists)):
            flat_lists[i] = [weight for weight in flat_lists[i] if weight != Weight.NONE]
        return flat_lists

    def create_verse(self, verse_id: int) -> Verse:
        flat_lists = self.get_flat_lists()
        problems = []
        for creator in self.creators:
            local_problems = []
            worked = False
            for flat_list in flat_lists:
                verseClassType = creator(flat_list)  # returns e.g. the SpondaicHexameter type
                verse = verseClassType(self.verse)
                verse.words = self.words
                verse.flat_list = list(flat_list)
                try:
                    verse.parse()
                    worked = True
                    if verse_id:
                        verse.save(verse_id, self.bridge)
                    return verse  # TODO what if multiple options are viable
                except ScansionException as exc:
                    local_problems.append(exc)
            if not worked:
                problems += local_problems
        raise VerseException("parsing did not succeed", *problems)
