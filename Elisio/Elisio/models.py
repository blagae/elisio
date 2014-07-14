#from django.db import models
import re

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
    def __init__(self, text):
        """ construct a Word by its contents """
        self.text = text

    def __eq__(self, other): 
        """ Words are equal if they have exactly the same characters """
        return self.__dict__ == other.__dict__