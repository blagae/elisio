""" the main module for parsing verses """
import enum
import re
from Elisio.engine.Syllable import Weight
from Elisio.engine.Word import Word
from Elisio.exceptions import VerseException, HexameterException, IllegalFootException

def set_django():
    """ in order to get to the database, we must use Django """
    import os
    if (not 'DJANGO_SETTINGS_MODULE' in os.environ or
            os.environ['DJANGO_SETTINGS_MODULE'] != 'Elisio.settings'):
        os.environ['DJANGO_SETTINGS_MODULE'] = 'Elisio.settings'
    import django
    if django.VERSION[:2] >= (1, 7):
        django.setup()

class Foot(enum.Enum):
    """ Types of verse foot """
    DACTYLUS = 0
    SPONDAEUS = 1
    TROCHAEUS = 2
    UNKNOWN = 3

    def get_length(self):
        """ number of syllables in the foot """
        return len(self.get_structure())

    def get_structure(self):
        """ available foot structures """
        if self == Foot.DACTYLUS:
            return [Weight.HEAVY, Weight.LIGHT, Weight.LIGHT]
        elif self == Foot.SPONDAEUS:
            return [Weight.HEAVY, Weight.HEAVY]
        elif self == Foot.TROCHAEUS:
            return [Weight.HEAVY, Weight.LIGHT]
        raise IllegalFootException("currently illegal foot structure: " + self.name)

class Verse(object):
    """ Verse class
    A verse is the representation of the Latin text of a verse
    It has no knowledge of its surroundings or context
    """
    def __init__(self, text):
        """ construct a Verse by its contents """
        if not isinstance(text, str):
            raise VerseException("Verse must be initialized with text data")
        self.text = text
        self.words = []

    def split(self):
        """ Split a Verse into Words, remembering only the letter characters """
        txt = self.text.strip()
        if self.words != []:
            return
        array = re.split('[^a-zA-Z]+', txt)
        for word in array:
            if word.isalpha():
                self.words.append(Word(word))

    def __repr__(self):
        return self.words
    def __str__(self):
        return self.words

    def __eq__(self, other):
        """ Verses are equal if they have exactly the same characters """
        return self.text == other.text

    def get_syllable_weights(self):
        """ get available weights of syllables """
        result = []
        for count, word in enumerate(self.words):
            try:
                result.append(word.get_syllable_structure(self.words[count+1]))
            except IndexError:
                result.append(word.get_syllable_structure())
        return result

    def preparse(self):
        """ prepare the list of Syllable weights """
        layered_list = self.get_syllable_weights()
        for word in layered_list:
            # TODO: open monosyllables ? se me ne are all heavy
            for weight in word:
                if weight != Weight.NONE:
                    self.flat_list.append(weight)

    def get_split_syllables(self):
        result = ""
        for word in self.words:
            for syll in word.syllables:
                for snd in syll.sounds:
                    for ltr in snd.letters:
                        result += ltr.letter
                result += "-"
            result = result[:-1] + " "
        return result

