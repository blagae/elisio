import enum

from elisio.engine.exceptions import LetterException


class LetterType(enum.Enum):
    """
    The possible types of letters
    """
    VOWEL = 0
    CONSONANT = 1
    SEMIVOWEL = 2
    HEAVYMAKER = 3


class Letter(object):
    """
    The Letter class is mostly here to make sure
    only valid letters get passed to the Sound class
    See validity check in constructor
    """
    letters = {
        # This list is sorted by relative prevalence of letters
        # so that the most frequent letters have more optimal search
        'e': LetterType.VOWEL,
        'a': LetterType.VOWEL,
        'i': LetterType.SEMIVOWEL,
        'u': LetterType.SEMIVOWEL,
        't': LetterType.CONSONANT,
        's': LetterType.CONSONANT,
        'r': LetterType.CONSONANT,
        'n': LetterType.CONSONANT,
        'o': LetterType.VOWEL,
        'm': LetterType.CONSONANT,
        'c': LetterType.CONSONANT,
        'l': LetterType.CONSONANT,
        'p': LetterType.CONSONANT,
        'd': LetterType.CONSONANT,
        'q': LetterType.CONSONANT,
        'b': LetterType.CONSONANT,
        'g': LetterType.CONSONANT,
        'f': LetterType.CONSONANT,
        'h': LetterType.CONSONANT,
        'x': LetterType.HEAVYMAKER,
        'y': LetterType.VOWEL,
        'k': LetterType.CONSONANT,
        'z': LetterType.HEAVYMAKER,
        'ë': LetterType.VOWEL
    }

    liquida = ['r', 'l']
    hard_muta = ['p', 't', 'c']
    muta = ['b', 'd', 'g', 'f'] + hard_muta

    def __init__(self, ltr):
        """ construct a Letter by its contents """
        if not (isinstance(ltr, str) and len(ltr) == 1 and ltr.isalpha()):
            raise LetterException("wrong number of letters " +
                                  "or not a valid character")
        self.letter = ltr.lower()
        if self.letter == 'v':
            self.letter = 'u'
        elif self.letter == 'j':
            self.letter = 'i'
        if not self.is_valid_letter():
            raise LetterException("not a valid letter")

    def __eq__(self, other):
        """ Letters are equal if they have exactly the same character
        Case insensitivity is enforced by the constructor
        """
        return self.__str__() == other.__str__()

    def __str__(self):
        return self.letter

    def __repr__(self):
        return self.letter

    def get_type(self):
        """ returns the LetterType of this letter """
        return Letter.letters[self.letter]

    def is_valid_letter(self):
        """ a letter is only valid if it figures in the list of legal characters
        currently the only invalid (Roman) letters are W, V and J
        but V and J are replaced by their vocalic values U and I
        in the constructor
        """
        return self.letter in Letter.letters
