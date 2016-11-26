from Elisio.engine.Verse import Verse
from Elisio.engine.Syllable import Weight

class TextDecorator(object):
    # TODO: don't put diacritic on consonantal semivowel
    # TODO: include punctuation marks
    # TODO: include capitals
    def __init__(self, verse):
        if (isinstance(verse, Verse)):
            self.verse = verse

    def decorate(self):
        s = ''
        for word in self.verse.words:
            for syll in word.syllables:
                for sound in syll.sounds:
                    for letter in sound.letters:
                        s += letter.letter
                    if not sound.is_consonant():
                        s += self.glyph(syll.weight)
            s += ' '
        return s

    def glyph(self, weight):
        if (weight == Weight.HEAVY):
            return u'\u0331'
        elif (weight == Weight.LIGHT):
            return u'\u032F'
        elif (weight == Weight.NONE):
            return u'\u0325'
        return ''