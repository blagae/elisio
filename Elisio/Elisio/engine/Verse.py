""" the main module for parsing verses """
import enum
import re
from Elisio.engine.Syllable import Weight
from Elisio.engine.Word import Word
from Elisio.exceptions import VerseException, HexameterException, IllegalFootException
from Elisio import settings

def set_django():
    """ in order to get to the database, we must use Django """
    import os
    module = 'DJANGO_SETTINGS_MODULE'
    if (not module in os.environ or
            os.environ[module] != settings.__name__):
        os.environ[module] = settings.__name__
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

    def __repr__(self):
        return self.words
    def __str__(self):
        return self.words

    def __eq__(self, other):
        """ Verses are equal if they have exactly the same characters """
        return self.text == other.text

    def parse(self, save=False):
        self.preparse()
        self.scan()
        self.save_structure()
        if save:
            from Elisio.models import WordOccurrence
            entries = []
            for count, wrd in enumerate(self.words):
                strct = ""
                for cnt, syll in enumerate(wrd.syllables):
                    strct += str(syll.weight.value)
                    if cnt == len(wrd.syllables)-1 and count < len(self.words) - 1:
                        if wrd.may_be_heavy_by_position(self.words[count+1]):
                            if syll.weight != Weight.NONE:
                                strct = strct[:-1]
                                strct += str(Weight.ANCEPS.value)
                entries.append(WordOccurrence(word=wrd.text, struct=strct))
            if len(entries) > 0:
                WordOccurrence.objects.bulk_create(entries)

    def preparse(self):
        pass

    def scan(self):
        pass

    def save_structure(self):
        i = 0
        for word in self.words:
            for syll in word.syllables:
                #if not syll.weight or syll.weight == Weight.ANCEPS:
                if syll.weight != Weight.NONE:
                    syll.weight = self.flat_list[i]
                    i+=1