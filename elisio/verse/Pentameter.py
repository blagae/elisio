from typing import Type, Union

from elisio.exceptions import PentameterException, VerseCreatorException
from elisio.Syllable import Weight
from elisio.verse.Verse import Foot, Verse
from elisio.verse.VerseFactory import VerseCreator


class PentameterCreator(VerseCreator):
    MAX_SYLL = 14
    MIN_SYLL = 12

    def __init__(self, lst: list[Weight]):
        self.max_syllables = PentameterCreator.MAX_SYLL
        self.min_syllables = PentameterCreator.MIN_SYLL
        super().__init__(lst)

    def get_subtype(self) -> Type['Pentameter']:
        size = len(self.list)
        if size > self.max_syllables:
            raise VerseCreatorException("too many syllables")
        elif size < self.min_syllables:
            raise VerseCreatorException("too few syllables")
        length = size - self.min_syllables
        if length == 0:
            return SpondaicPentameter
        elif length == 1:
            return BalancedPentameter
        return DactylicPentameter


class Pentameter(Verse):
    def __init__(self, text: str):
        super().__init__(text)
        self.feet: list[Union[None, Foot]] = [None, None, Foot.MACRON, Foot.DACTYLUS, Foot.DACTYLUS, Foot.MACRON]

    def preparse(self) -> None:
        if (self.flat_list[-1] == Weight.LIGHT
            or self.flat_list[-2] == Weight.HEAVY
            or self.flat_list[-3] == Weight.HEAVY
            or self.flat_list[-4] == Weight.LIGHT
            or self.flat_list[-5] == Weight.HEAVY
            or self.flat_list[-6] == Weight.HEAVY
            or self.flat_list[-7] == Weight.LIGHT
                or self.flat_list[-8] == Weight.LIGHT):
            raise PentameterException("problem in second half with syllable weight")

    def scan(self) -> None:
        self.scan_first_half()

    def scan_first_half(self) -> None:
        pass


class SpondaicPentameter(Pentameter):
    def __init__(self, text: str):
        super().__init__(text)

    def scan_first_half(self) -> None:
        for i in range(4):
            if self.flat_list[i] == Weight.LIGHT:
                raise PentameterException("no light syllable allowed on pos {0} of Spondaic Pentameter".format(i))
        self.feet[0] = self.feet[1] = Foot.SPONDAEUS


class DactylicPentameter(Pentameter):
    def __init__(self, text: str):
        super().__init__(text)

    def scan_first_half(self) -> None:
        if (self.flat_list[0] == Weight.LIGHT
            or self.flat_list[1] == Weight.HEAVY
            or self.flat_list[2] == Weight.HEAVY
            or self.flat_list[3] == Weight.LIGHT
            or self.flat_list[4] == Weight.HEAVY
                or self.flat_list[5] == Weight.HEAVY):
            raise PentameterException("problem with first half of Dactylic Pentameter")
        self.feet[0] = self.feet[1] = Foot.DACTYLUS


class BalancedPentameter(Pentameter):
    def __init__(self, text: str):
        super().__init__(text)

    def scan_first_half(self) -> None:
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
