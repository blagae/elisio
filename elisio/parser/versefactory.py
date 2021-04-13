import re
from collections.abc import Iterable
from enum import Enum
from typing import Sequence, Type

from elisio.bridge import Bridge, DummyBridge
from elisio.exceptions import ScansionException, VerseException
from elisio.parser.verse import Verse
from elisio.word import Weight, Word


class VerseType(Enum):
    UNKNOWN = 0
    HEXAMETER = 1
    PENTAMETER = 2
    HENDECASYLLABUS = 3

    def get_creators(self) -> list[Type['VerseCreator']]:
        from elisio.parser.hendeca import HendecaCreator
        from elisio.parser.hexameter import HexameterCreator
        from elisio.parser.pentameter import PentameterCreator
        if self == VerseType.HEXAMETER:
            return [HexameterCreator]
        if self == VerseType.PENTAMETER:
            return [PentameterCreator]
        if self == VerseType.HENDECASYLLABUS:
            return [HendecaCreator]
        return [HexameterCreator, PentameterCreator]


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
    def __create_preprocessor(text: str, bridge: Bridge = DummyBridge(),
                              classes: Sequence[VerseType] = []) -> 'VersePreprocessor':
        return VersePreprocessor(text, bridge, classes)

    @staticmethod
    def split(text: str, bridge: Bridge = DummyBridge(), classes: Sequence[VerseType] = []) -> list[Word]:
        return VerseFactory.__create_preprocessor(text, bridge, classes).split()

    @staticmethod
    def layer(text: str, bridge: Bridge = DummyBridge(), classes: Sequence[VerseType] = []) -> list[list[Weight]]:
        return VerseFactory.__create_preprocessor(text, bridge, classes).layer()

    @staticmethod
    def get_flat_list(text: str, bridge: Bridge = DummyBridge(), classes: Sequence[VerseType] = []) -> list[Weight]:
        return VerseFactory.__create_preprocessor(text, bridge, classes).get_flat_list()

    @staticmethod
    def create(text: str, db_id: int = 0, bridge: Bridge = DummyBridge(), classes: Sequence[VerseType] = []) -> Verse:
        return VerseFactory.__create_preprocessor(text, bridge, classes).create_verse(db_id)

    @staticmethod
    def get_split_syllables(text: str, bridge: Bridge = DummyBridge(), classes: Sequence[VerseType] = []) -> str:
        return VerseFactory.__create_preprocessor(text, bridge, classes).get_split_syllables()


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
    def __init__(self, verse: str, bridge: Bridge = DummyBridge(), classes: Sequence[VerseType] = []):
        self.verse = verse
        self.bridge = bridge
        self.words: list[Word] = []
        self.flat_list: list[Weight] = []
        self.classes: set[Type[VerseCreator]] = set()
        # https://docs.python.org/3/tutorial/controlflow.html#default-argument-values
        if isinstance(classes, VerseType):
            self.classes = set(classes.get_creators())
        elif isinstance(classes, Iterable):
            for clazz in classes:
                self.classes.update(clazz.get_creators())
        else:
            self.classes = set(VerseType.UNKNOWN.get_creators())

    def split(self) -> list[Word]:
        """ Split a Verse into Words, remembering only the letter characters """
        txt = self.verse.strip()
        array = re.split('[^a-zA-Z]+', txt)
        for word in array:
            if word.isalpha():
                self.words.append(Word(word))
        return self.words

    def layer(self) -> list[list[Weight]]:
        """ get available weights of syllables """
        self.split()
        for word in self.words:
            word.analyze_structure(self.bridge)
        for count, word in enumerate(self.words):
            try:
                word.apply_word_contact(self.words[count + 1])
            except IndexError:
                # last word in verse
                pass
        return [word.get_syllable_structure() for word in self.words]

    def get_flat_list(self) -> list[Weight]:
        layers = self.layer()
        for word in layers:
            for weight in word:
                if weight != Weight.NONE:
                    self.flat_list.append(weight)
        return self.flat_list

    def create_verse(self, verse_id: int) -> Verse:
        self.get_flat_list()
        problems = []
        for creator in self.classes:
            item = creator(self.flat_list)
            verseClassType = item.get_subtype()  # returns e.g. the SpondaicHexameter type
            verse = verseClassType(self.verse)
            verse.words = self.words
            verse.flat_list = self.flat_list.copy()
            try:
                verse.parse()
                if verse_id:
                    verse.save(verse_id, self.bridge)
                return verse
            except ScansionException as exc:
                problems.append(exc)
        raise VerseException("parsing did not succeed", *problems)

    def get_split_syllables(self) -> str:
        result = ""
        if not self.words:
            self.layer()
        for word in self.words:
            for syll in word.syllables:
                for snd in syll.sounds:
                    for ltr in snd.letters:
                        result += ltr
                result += "-"
            result = result[:-1] + " "
        return result


class VerseCreator:
    """ De facto interface that Verse Creator types must follow """
    def __init__(self, lst: list[Weight]):
        self.list = lst

    def get_subtype(self) -> Type[Verse]:
        raise Exception("must be overridden")
