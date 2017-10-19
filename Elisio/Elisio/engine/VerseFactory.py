import collections
import re

from Elisio.engine.Word import Word, Weight
from Elisio.engine.bridge.Bridge import DummyBridge
from Elisio.engine.exceptions import ScansionException, VerseException
from Elisio.engine.verse.VerseType import VerseType


class VerseFactory(object):
    """ Static factory method container for verse creation.
    The methods delegate pre-analysis work to the VersePreprocessor class,
    which in turn delegates actual Verse object creation to a VerseCreator class.
    """

    @staticmethod
    def __create_preprocessor(text, bridge=DummyBridge(), classes=None):
        return VersePreprocessor(text, bridge, classes)

    @staticmethod
    def split(text, bridge=DummyBridge(), classes=None):
        return VerseFactory.__create_preprocessor(text, bridge, classes).split()

    @staticmethod
    def layer(text, bridge=DummyBridge(), classes=None):
        return VerseFactory.__create_preprocessor(text, bridge, classes).layer()

    @staticmethod
    def get_flat_list(text, bridge=DummyBridge(), classes=None):
        return VerseFactory.__create_preprocessor(text, bridge, classes).get_flat_list()

    @staticmethod
    def create(verse, bridge=DummyBridge(), classes=None):
        return VerseFactory.__create_preprocessor(verse, bridge, classes).create_verse()

    @staticmethod
    def get_split_syllables(text, bridge=DummyBridge(), classes=None):
        return VerseFactory.__create_preprocessor(text, bridge, classes).get_split_syllables()


class VersePreprocessor(object):
    """ The verse preprocessor will do the heavy lifting of analyzing words and their structure.
    This happens in 5 steps:
    * split the verse into words
    * find the syllable lengths of the words
    * store the syllable lengths in a one-dimensional list
    * determine which Verse subtype should be created, according to given Verse type(s)
    * try to create the verse, and throw if impossible for the given Verse type

    In practice, the step that determines the subtype is delegated to a VerseCreator
    """
    def __init__(self, verse, bridge=DummyBridge(), classes=None):
        self.verse = verse
        self.bridge = bridge
        self.words = []
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

    def get_text(self):
        try:
            return self.verse.contents
        except AttributeError:
            return self.verse

    def split(self):
        """ Split a Verse into Words, remembering only the letter characters """
        txt = self.get_text().strip()
        array = re.split('[^a-zA-Z]+', txt)
        for word in array:
            if word.isalpha():
                self.words.append(Word(word))
        return self.words

    def layer(self):
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

    def get_flat_list(self):
        layers = self.layer()
        for word in layers:
            for weight in word:
                if weight != Weight.NONE:
                    self.flat_list.append(weight)
        return self.flat_list

    def create_verse(self):
        self.get_flat_list()
        problems = []
        for creator in self.classes:
            item = creator(self.flat_list)
            cls = item.get_subtype()  # returns e.g. the SpondaicHexameter type
            verse = cls(self.get_text())
            verse.words = self.words
            verse.flat_list = self.flat_list.copy()
            try:
                verse.parse(self.verse, self.bridge)
                return verse
            except AttributeError:
                verse.parse(None, self.bridge)
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
    """ De facto interface that Verse Creator types must follow """
    def get_subtype(self):
        raise Exception("must be overridden")
