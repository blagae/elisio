#from django.db import models
import re
from Elisio.exceptions import ScansionException

class Verse():
    """ Verse class
    commit 1 (blagae): BLI 9
    reason: creation
    """
    text = ""
    words = []
    def __init__(self, text):
        """ construct a Verse by its contents """
        self.text = text

    def split(self):
        """ Split a Verse into Words, remembering only the letter characters """
        s = self.text.strip()
        array = re.split('\W+', s)
        for word in array:
            if word.isalpha():
                self.words.append(Word(word))

    def __eq__(self, other): 
        """ Verses are equal if they have exactly the same characters """
        return self.__dict__ == other.__dict__

class Word():
    """ Word class
    commit 1 (blagae): BLI 9
    reason: creation of stub for interaction with Verse
    """
    text = ""
    syllables = []
    def __init__(self, text):
        """ construct a Word by its contents """
        if not text.isalpha():
            raise ScansionException
        self.text = text

    def split():
        pass
    
    def __eq__(self, other): 
        """ Words are equal if they have exactly the same characters """
        return self.__dict__ == other.__dict__

class Syllable():
    """ Syllable class
    commit 1 (blagae): BLI 10
    reason: creation of stub for interaction with Word
    """
    syllable = ""
    def __init__(self, syllable):
        """ construct a Syllable by its contents """
        self.syllable = syllable

class Letter():
    """ Letter class
    commit 1 (blagae): BLI 10
    reason: creation of stub for interaction with Word
    """
    letter = ""
    def __init__(self, letter):
        """ construct a Letter by its contents """
        self.letter = letter