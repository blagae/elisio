from Elisio.engine.Syllable import Weight
from Elisio.engine.Verse import Verse
from Elisio.engine.VerseFactory import VerseCreator
from Elisio.engine.exceptions import VerseException


class HendecaException(VerseException):
    pass


class HendecaCreator(VerseCreator):
    SYLL = 11

    def __init__(self, lst):
        self.list = lst

    def get_subtype(self):
        if len(self.list) != 11:
            raise HendecaException("incorrect number of syllables: " + str(len(self.list)))
        li = self.list
        """
        https://en.wikipedia.org/wiki/Hendecasyllable
        xx-uu-u-u-x : Phalaecian
        x-u-x-uu-u- : Alcaic
        -x-x-uu-u-- : Sapphic
        """
        # unambiguous
        if li[10] == Weight.LIGHT:
            return PhalaecianHendeca
        if li[2] == Weight.LIGHT or li[7] == Weight.LIGHT or li[8] == Weight.HEAVY or li[9] == Weight.LIGHT:
            return AlcaicHendeca
        if li[5] == Weight.LIGHT:
            return SapphicHendeca
        # elimination game
        poss = {PhalaecianHendeca, AlcaicHendeca, SapphicHendeca}
        if li[3] == Weight.HEAVY or li[4] == Weight.HEAVY:
            poss.discard(PhalaecianHendeca)
        if (li[1] == Weight.LIGHT or li[2] == Weight.HEAVY or li[3] == Weight.LIGHT or
                li[7] == Weight.HEAVY or li[8] == Weight.LIGHT or li[9] == Weight.HEAVY):
            poss.discard(AlcaicHendeca)
        if li[0] == Weight.LIGHT or li[4] == Weight.LIGHT or li[5] == Weight.HEAVY:
            poss.discard(SapphicHendeca)
        if len(poss) == 1:
            return poss.pop()
        raise HendecaException("could not determine type")


class Hendeca(Verse):
    def preparse(self):
        for count, x in enumerate(self.get_structure()):
            if x == '-':
                if self.flat_list[count] == Weight.LIGHT:
                    raise HendecaException("cannot be light")
                self.flat_list[count] = Weight.HEAVY
            elif x == 'u':
                if self.flat_list[count] == Weight.HEAVY:
                    raise HendecaException("cannot be heavy")
                self.flat_list[count] = Weight.LIGHT

    def scan(self):
        pass

    def get_structure(self):
        raise HendecaException("must be overridden")


class PhalaecianHendeca(Hendeca):
    def preparse(self):
        super().preparse()
        if self.flat_list[0] == Weight.ANCEPS and self.flat_list[1] == Weight.LIGHT:
            self.flat_list[0] = Weight.HEAVY
        if self.flat_list[0] == Weight.LIGHT and self.flat_list[1] == Weight.ANCEPS:
            self.flat_list[1] = Weight.HEAVY

    def get_structure(self):
        return "xx-uu-u-u-x"


class AlcaicHendeca(Hendeca):
    def get_structure(self):
        return "x-u-x-uu-u-"


class SapphicHendeca(Hendeca):
    def get_structure(self):
        return "-x-x-uu-u--"
