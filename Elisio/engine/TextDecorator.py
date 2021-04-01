from elisio.engine.Verse import Verse
from elisio.engine.Syllable import Weight


class TextDecorator(object):
    def __init__(self, verse):
        if not isinstance(verse, Verse):
            raise TypeError("parameter must be a verse")
        self.verse = verse

    def decorate(self):
        result = ''
        vrs = self.verse.text.split(' ')
        for idx, word in enumerate(self.verse.words):
            lettercount = 0
            while not vrs[idx][lettercount].isalnum():
                result += vrs[idx][lettercount]
                lettercount += 1
            for syll in word.syllables:
                for indx, sound in enumerate(syll.sounds):
                    for i in range(len(sound.letters)):
                        result += vrs[idx][lettercount]
                        lettercount += 1
                    if indx == syll.get_vowel_location():
                        result += TextDecorator.glyph(syll.weight)
            if len(vrs[idx]) > lettercount:
                result += vrs[idx][-1]
            result += ' '
        return result.strip()

    @staticmethod
    def glyph(weight):
        if weight == Weight.HEAVY:
            return u'\u0331'
        elif weight == Weight.LIGHT:
            return u'\u032F'
        elif weight == Weight.NONE:
            return u'\u0325'
        return ''
