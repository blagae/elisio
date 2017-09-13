from Elisio.engine.Syllable import Weight
from Elisio.engine.Verse import Verse, Foot
from Elisio.exceptions import PentameterException
from Elisio.engine.VerseFactory import VerseCreator, VerseType


class PentameterCreator(VerseCreator):
    MAX_SYLL = 14
    MIN_SYLL = 12

    def __init__(self, lst):
        self.max_syllables = PentameterCreator.MAX_SYLL
        self.min_syllables = PentameterCreator.MIN_SYLL
        self.list = lst

    def get_type(self):
        return VerseType.PENTAMETER

    def get_subtype(self):
        if len(self.list) > self.max_syllables:
            raise PentameterException("too many syllables")
        elif len(self.list) < self.min_syllables:
            raise PentameterException("too few syllables")
        length = len(self.list) - self.min_syllables
        if length == 0:
            return SpondaicPentameter
        elif length == 1:
            return BalancedPentameter
        elif length == 2:
            return DactylicPentameter
        else:
            raise PentameterException("{0} is an illegal number of"
                                      "syllables in a Pentameter"
                                      .format(len(self.list)))


class Pentameter(Verse):
    def __init__(self, text):
        super(Pentameter, self).__init__(text)
        self.feet = [None, None, Foot.MACRON, Foot.DACTYLUS, Foot.DACTYLUS, Foot.MACRON]

    def preparse(self):
        if (self.flat_list[-1] == Weight.LIGHT
            or self.flat_list[-2] == Weight.HEAVY
            or self.flat_list[-3] == Weight.HEAVY
            or self.flat_list[-4] == Weight.LIGHT
            or self.flat_list[-5] == Weight.HEAVY
            or self.flat_list[-6] == Weight.HEAVY
            or self.flat_list[-7] == Weight.LIGHT
            or self.flat_list[-8] == Weight.LIGHT):
            raise PentameterException("problem in second half with syllable weight")

    def scan(self):
        self.scan_first_half()
        self.fill()

    def scan_first_half(self):
        pass

    def fill(self):
        pass


class SpondaicPentameter(Pentameter):
    def __init__(self, text):
        super(SpondaicPentameter, self).__init__(text)

    def scan_first_half(self):
        for i in range(0, 4):
            if self.flat_list[i] == Weight.LIGHT:
                raise PentameterException("no light syllable allowed on pos " + i + " of Spondaic Pentameter")
        self.feet[0] = Foot.SPONDAEUS
        self.feet[1] = Foot.SPONDAEUS


class DactylicPentameter(Pentameter):
    def __init__(self, text):
        super(DactylicPentameter, self).__init__(text)

    def scan_first_half(self):
        if (self.flat_list[0] == Weight.LIGHT
            or self.flat_list[1] == Weight.HEAVY
            or self.flat_list[2] == Weight.HEAVY
            or self.flat_list[3] == Weight.LIGHT
            or self.flat_list[4] == Weight.HEAVY
            or self.flat_list[5] == Weight.HEAVY):
            raise PentameterException("problem with first half of Dactylic Pentameter")
        self.feet[0] = self.feet[1] = Foot.DACTYLUS


class BalancedPentameter(Pentameter):
    def __init__(self, text):
        super(BalancedPentameter, self).__init__(text)

    def scan_first_half(self):
        for i in range(1, 5):
            if self.flat_list[i] != Weight.ANCEPS:
                if self.flat_list[i] == Weight.LIGHT:
                    self.feet[i // 3] = Foot.DACTYLUS
                    self.feet[(5 - i) // 3] = Foot.SPONDAEUS
                else:
                    self.feet[i // 3] = Foot.SPONDAEUS
                    self.feet[(5 - i) // 3] = Foot.DACTYLUS
                return
        raise PentameterException("not enough info in first half of Balanced Pentameter")
