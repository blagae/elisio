from typing import Optional, Type

from ..exceptions import PentameterException, VerseCreatorException
from ..syllable import Weight
from .verse import Foot, Verse


MAX_SYLL = 14
MIN_SYLL = 12


class Pentameter(Verse):
    def __init__(self, text: str):
        super().__init__(text)
        self.feet: list[Optional[Foot]] = [None, None, Foot.MACRON, Foot.DACTYLUS, Foot.DACTYLUS, Foot.MACRON]

    def preparse(self) -> None:
        if (self.flat_list[-1] == Weight.LIGHT or self.flat_list[-2] == Weight.HEAVY
                or self.flat_list[-3] == Weight.HEAVY or self.flat_list[-4] == Weight.LIGHT
                or self.flat_list[-5] == Weight.HEAVY or self.flat_list[-6] == Weight.HEAVY
                or self.flat_list[-7] == Weight.LIGHT or self.flat_list[-8] == Weight.LIGHT):
            raise PentameterException("problem in second half with syllable weight")

    def scan(self) -> None:
        self.scan_first_half()

    def scan_first_half(self) -> None:
        pass


def get_penta_subtype(lst: list[Weight]) -> Type[Pentameter]:
    pent_types = [SpondaicPentameter, BalancedPentameter, DactylicPentameter]
    size = len(lst)
    if size > MAX_SYLL:
        raise VerseCreatorException("too many syllables")
    elif size < MIN_SYLL:
        raise VerseCreatorException("too few syllables")
    length = size - MIN_SYLL
    try:
        return pent_types[length]
    except IndexError:
        raise VerseCreatorException(f"{size} is an illegal number of syllables in a Pentameter")


class SpondaicPentameter(Pentameter):

    def scan_first_half(self) -> None:
        for i in range(4):
            if self.flat_list[i] == Weight.LIGHT:
                raise PentameterException(f"no light syllable allowed on pos {i} of Spondaic Pentameter")
        self.feet[:2] = [Foot.SPONDAEUS, Foot.SPONDAEUS]


class DactylicPentameter(Pentameter):

    def scan_first_half(self) -> None:
        if (self.flat_list[0] == Weight.LIGHT or self.flat_list[1] == Weight.HEAVY
                or self.flat_list[2] == Weight.HEAVY or self.flat_list[3] == Weight.LIGHT
                or self.flat_list[4] == Weight.HEAVY or self.flat_list[5] == Weight.HEAVY):
            raise PentameterException("problem with first half of Dactylic Pentameter")
        self.feet[:2] = [Foot.DACTYLUS, Foot.DACTYLUS]


class BalancedPentameter(Pentameter):

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
