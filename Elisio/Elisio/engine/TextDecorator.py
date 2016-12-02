from Elisio.engine.Verse import Verse
from Elisio.engine.Syllable import Weight

class TextDecorator(object):
    def __init__(self, verse):
        if isinstance(verse, Verse):
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
                vowel = False
                for sound in syll.sounds:
                    if vowel and not sound.is_consonant():
                        result = result[:-1]
                    for letter in sound.letters:
                        result += vrs[idx][lettercount]
                        lettercount += 1

                    if not sound.is_consonant():
                        vowel = True
                        result += self.glyph(syll.weight)
            if len(vrs[idx]) > lettercount:
                result += vrs[idx][-1]
            result += ' '
        return result

    def glyph(self, weight):
        if weight == Weight.HEAVY:
            return u'\u0331'
        elif weight == Weight.LIGHT:
            return u'\u032F'
        elif weight == Weight.NONE:
            return u'\u0325'
        return ''
