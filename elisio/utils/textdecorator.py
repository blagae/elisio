from typing import Optional

from ..parser.verse import Verse
from ..syllable import Weight


def decorate(verse: Verse) -> str:
    if not isinstance(verse, Verse):
        raise TypeError("parameter must be a verse")
    result = ''
    vrs = verse.text.split(' ')
    for idx, word in enumerate(verse.words):
        lettercount = 0
        while not vrs[idx][lettercount].isalnum():
            result += vrs[idx][lettercount]
            lettercount += 1
        for syll in word.syllables:
            for indx, sound in enumerate(syll.sounds):
                result += vrs[idx][lettercount:lettercount+len(sound)]
                lettercount += len(sound)
                if indx == syll.get_vowel_location():
                    result += _glyph(syll.weight)
        if len(vrs[idx]) > lettercount:
            result += vrs[idx][-1]
        result += ' '
    return result.strip()


def _glyph(weight: Optional[Weight]) -> str:
    if weight == Weight.HEAVY:
        return u'\u0331'
    elif weight == Weight.LIGHT:
        return u'\u032F'
    elif weight == Weight.NONE:
        return u'\u0325'
    return ''
