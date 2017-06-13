import re
import collections
from Elisio.engine.Word import Word, Weight
from Elisio.exceptions import ScansionException, VerseException
import enum

class VerseType(enum.Enum):
    UNKNOWN = 0
    HEXAMETER = 1
    PENTAMETER = 2

    def get_creators(self):
        from Elisio.engine.Hexameter import HexameterCreator
        from Elisio.engine.Pentameter import PentameterCreator
        if self == VerseType.HEXAMETER:
            return [HexameterCreator]
        if self == VerseType.PENTAMETER:
            return [PentameterCreator]
        return [HexameterCreator, PentameterCreator]

class VerseForm(enum.Enum):
    UNKNOWN = 0
    HEXAMETRIC = 1
    ELEGIAC_DISTICHON = 2
#    SAPPHIC_STOPHE = 3

    def get_verse_types(self):
        if self == VerseForm.UNKNOWN:
            return [VerseType.UNKNOWN]
        if self == VerseForm.HEXAMETRIC:
            return [VerseType.HEXAMETER]
        if self == VerseForm.ELEGIAC_DISTICHON:
            return [VerseType.HEXAMETER, VerseType.PENTAMETER]
#        if self == VerseForm.SAPPHIC_STOPHE:
        return [VerseType.UNKNOWN]

class VerseFactory(object):
    @classmethod
    def split(cls, text):
        return VerseFactoryImpl(text).split()
    @classmethod
    def layer(cls, text):
        return VerseFactoryImpl(text).layer()
    @classmethod
    def getlist(cls, text):
        return VerseFactoryImpl(text).getlist()
    @classmethod
    def get_split_syllables(cls, text):
        return VerseFactoryImpl(text).get_split_syllables()
    @classmethod
    def create(cls, verse, useDict=False, classes=None):
        return VerseFactoryImpl(verse, useDict, classes=classes).create()

class VerseFactoryImpl(object):
    def __init__(self, verse, useDict=False, classes=None):
        self.verse = verse
        self.use_dict = useDict
        self.words = []
        self.layers = [[]]
        self.flat_list = []
        # https://docs.python.org/3/tutorial/controlflow.html#default-argument-values
        if isinstance(classes, VerseType):
            self.classes = classes.get_creators()
        elif isinstance(classes, collections.Iterable):
            self.classes = set()
            for clazz in classes:
                self.classes.update(clazz.get_creators())
        else:
            self.classes = VerseType.UNKNOWN.get_creators()

    def is_from_db(self):
        from Elisio.models import DatabaseVerse
        return isinstance(self.verse, DatabaseVerse)

    def get_text(self):
        if self.is_from_db():
            return self.verse.contents
        return self.verse

    def split(self):
        """ Split a Verse into Words, remembering only the letter characters """
        txt = self.get_text().strip()
        array = re.split('[^a-zA-Z]+', txt)
        for word in array:
            if word.isalpha():
                self.words.append(Word(word, self.use_dict))
        return self.words

    def layer(self):
        """ get available weights of syllables """
        self.split()
        result = []
        for count, word in enumerate(self.words):
            try:
                syll_struct = word.get_syllable_structure(self.words[count+1])
            except IndexError:
                syll_struct = word.get_syllable_structure()
            result.append(syll_struct)
        self.layers = result
        return self.layers

    def getlist(self):
        self.layer()
        for word in self.layers:
            if len(word) == 1 and word[0] == Weight.ANCEPS:
                word[0] == Weight.HEAVY
            for weight in word:
                if weight != Weight.NONE:
                    self.flat_list.append(weight)
        return self.flat_list

    def create(self):
        self.getlist()
        problems = []
        for creator in self.classes:
            item = creator(self.flat_list)
            cls = item.get_subtype()
            verse = cls(self.get_text())
            verse.words = self.words
            verse.flat_list = self.flat_list.copy()
            try:
                if self.is_from_db():
                    verse.parse(self.verse)
                else:
                    verse.parse()
                return verse
            except ScansionException as exc:
                problems.append(exc)
        raise VerseException("parsing did not succeed", problems)

    def get_split_syllables(self):
        result = ""
        if not self.words:
            self.layer()
        for word in self.words:
            for syll in word.syllables:
                for snd in syll.sounds:
                    for ltr in snd.letters:
                        result += ltr.letter
                result += "-"
            result = result[:-1] + " "
        return result

class VerseCreator(object):
    def get_type(self):
        raise Exception("must be overridden")
    def get_subtype(self):
        raise Exception("must be overridden")
    