import re
from Elisio.engine.Word import Word, Weight
from Elisio.exceptions import ScansionException, VerseException

class VerseFactory(object):
    classes = []
    @classmethod
    def init_class(cls):
        VerseFactory.classes = VerseCreator.__subclasses__()
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
    def create(cls, text):
        return VerseFactoryImpl(text).create()

class VerseFactoryImpl(object):
    def __init__(self, text):
        self.text = text
        self.words = []
        self.layers = [[]]
        self.flat_list = []

    def create(self):
        return self.__create_verse()

    def split(self):
        """ Split a Verse into Words, remembering only the letter characters """
        txt = self.text.strip()
        array = re.split('[^a-zA-Z]+', txt)
        for word in array:
            if word.isalpha():
                self.words.append(Word(word))
        return self.words

    def layer(self):
        """ get available weights of syllables """
        self.split()
        result = []
        for count, word in enumerate(self.words):
            try:
                result.append(word.get_syllable_structure(self.words[count+1]))
            except IndexError:
                result.append(word.get_syllable_structure())
        self.layers = result
        return self.layers

    def getlist(self):
        self.layer()
        for word in self.layers:
            # TODO: open monosyllables ? se me ne are all heavy
            for weight in word:
                if weight != Weight.NONE:
                    self.flat_list.append(weight)
        return self.flat_list

    def __create_verse(self):
        self.getlist()
        VerseFactory.classes = VerseCreator.__subclasses__()
        problems = []
        for creator in VerseFactory.classes:
            item = creator(self.flat_list)
            cls = item.get_subtype()
            verse = cls(self.text)
            verse.words = self.words
            verse.flat_list = self.flat_list
            try:
                verse.parse()
                return verse
            except ScansionException as exc:
                problems.append(exc)
        raise VerseException("parsing did not succeed", problems)
    
    def get_split_syllables(self):
        result = ""
        if not self.layers:
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
    def get_subtype(self):
        raise Exception("must be overridden")