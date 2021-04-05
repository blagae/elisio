﻿""" the main module for parsing verses """
import enum

from elisio.Syllable import Weight
from elisio.exceptions import VerseException, IllegalFootException


class Foot(enum.Enum):
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
        elif self == Foot.BINARY_ANCEPS:
            return [Weight.HEAVY, Weight.ANCEPS]
        elif self == Foot.MACRON:
            return [Weight.HEAVY]
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
        self.flat_list = []
        self.feet = []
        self.structure = None

    def __repr__(self):
        return self.words

    def __str__(self):
        return self.words

    def __eq__(self, other):
        """ Verses are equal if they have exactly the same characters """
        return self.text == other.text

    def parse(self, verse=None, bridge=None):
        self.preparse()
        self.scan()
        self.save_structure()
        self.save_feet()
        if verse and not verse.saved:
            bridge.save(self, verse.id)
        self.add_accents()

    def add_accents(self):
        for wrd in self.words:
            if len(wrd.syllables) < 3:
                wrd.syllables[0].stressed = True
            else:
                if wrd.syllables[-2].weight == Weight.HEAVY:
                    wrd.syllables[-2].stressed = True
                else:
                    wrd.syllables[-3].stressed = True

    def preparse(self):
        raise Exception("must be overridden")

    def scan(self):
        raise Exception("must be overridden")

    def save_structure(self):
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

    def save_feet(self):
        result = ""
        for foot in self.feet:
            result += str(foot.value)
        self.structure = result

    def get_zeleny_score(self):
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