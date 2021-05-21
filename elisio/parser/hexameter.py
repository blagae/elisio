from typing import Optional, Type

from ..exceptions import HexameterException, VerseCreatorException
from ..syllable import Weight
from .verse import Foot, Verse


MAX_SYLL = 17
MIN_SYLL = 12


class Hexameter(Verse):
    """ the most popular Latin verse type """

    def __init__(self, text: str):
        super().__init__(text)
        self.feet: list[Optional[Foot]] = [None] * 6
        self.hex = None

    def preparse(self) -> None:
        try:
            for i in range(len(self.flat_list)):
                if self.flat_list[i] == Weight.HEAVY and self.flat_list[i + 2] == Weight.HEAVY:
                    if self.flat_list[i + 1] == Weight.LIGHT:
                        raise HexameterException(f"cannot assign HEAVY to LIGHT syllable #{i+1}")
                    else:
                        self.flat_list[i + 1] = Weight.HEAVY
                elif self.flat_list[i] == Weight.LIGHT and self.flat_list[i + 1] == Weight.LIGHT:
                    self.flat_list[i + 2] = Weight.HEAVY
                    self.flat_list[i - 1] = Weight.HEAVY
        except IndexError:
            pass

    def scan(self) -> None:
        """ main outward-facing method to be used for scanning purposes """
        if Hexameter.has_spondaic_fifth_foot(self.flat_list):
            self.feet[4] = Foot.SPONDAEUS
        else:
            self.feet[4] = Foot.DACTYLUS
        if self.flat_list[-1] == Weight.HEAVY:
            self.feet[5] = Foot.SPONDAEUS
        elif self.flat_list[-1] == Weight.LIGHT:
            self.feet[5] = Foot.TROCHAEUS
        else:
            self.feet[5] = Foot.BINARY_ANCEPS
        self.scan_for_real()

    def fill_other_feet(self, from_foot: Foot, to_foot: Foot) -> None:
        """ only use after certifying that all necessary info is present """
        for count in range(4):
            if self.feet[count] != from_foot:
                self.feet[count] = to_foot

    def scan_for_real(self) -> None:
        pass

    @staticmethod
    def has_spondaic_fifth_foot(lst: list[Weight]) -> bool:
        return lst[-3] == Weight.HEAVY or lst[-4] == Weight.HEAVY or lst[-5] == Weight.LIGHT


def get_hexa_subtype(lst: list[Weight]) -> Type[Hexameter]:
    hex_types = [SpondaicHexameter, SpondaicDominantHexameter, BalancedHexameter,
                 DactylicDominantHexameter, DactylicHexameter]  # this is an ordered list !
    size = len(lst)
    if size > MAX_SYLL:
        raise VerseCreatorException("too many syllables in first pass")
    elif size < MIN_SYLL:
        raise VerseCreatorException("too few syllables in first pass")
    max_syllables = MAX_SYLL
    min_syllables = MIN_SYLL
    if Hexameter.has_spondaic_fifth_foot(lst):
        max_syllables -= 1
    else:
        min_syllables += 1
    if size > max_syllables:
        raise VerseCreatorException("too many syllables in second pass")
    if size < min_syllables:
        raise VerseCreatorException("too few syllables in second pass")
    length = size - min_syllables
    try:
        return hex_types[length]
    except IndexError:
        raise VerseCreatorException(f"{size} is an illegal number of syllables in a Hexameter")


class SpondaicHexameter(Hexameter):
    """ a Hexameter with 4 Spondees in its first 4 feet """
    def scan_for_real(self) -> None:
        self.feet[:4] = [Foot.SPONDAEUS] * 4


class DactylicHexameter(Hexameter):
    """ a Hexameter with 4 Dactyls in its first 4 feet """
    def scan_for_real(self) -> None:
        self.feet[:4] = [Foot.DACTYLUS] * 4


class SpondaicDominantHexameter(Hexameter):
    """ a Hexameter with 3 Spondees and 1 Dactyl in its first 4 feet """
    def scan_for_real(self) -> None:
        dact = False
        for count in range(1, 9):
            if self.flat_list[count] == Weight.LIGHT:
                self.feet[(count - 1) // 2] = Foot.DACTYLUS
                dact = True
                break
        if dact:
            self.fill_other_feet(Foot.DACTYLUS, Foot.SPONDAEUS)
        else:
            for count in range(1, 9):
                if self.flat_list[count] == Weight.HEAVY:
                    self.feet[(count - 1) // 2] = Foot.SPONDAEUS
            if self.feet[:4].count(Foot.SPONDAEUS) == 3:
                self.fill_other_feet(Foot.SPONDAEUS, Foot.DACTYLUS)
            else:
                raise HexameterException("cannot determine full foot structure of single dactylus verse")


class DactylicDominantHexameter(Hexameter):
    """ a Hexameter with 3 Dactyls and 1 Spondee in its first 4 feet """
    def __do_basic_checks(self) -> None:
        """ do easy pickings for DD hexameter """
        if (self.flat_list[1] == Weight.LIGHT or self.flat_list[2] == Weight.LIGHT or
                self.flat_list[3] == Weight.HEAVY):
            self.feet[0] = Foot.DACTYLUS
        if self.flat_list[4] == Weight.LIGHT:
            self.feet[1] = Foot.DACTYLUS
        if self.flat_list[7] == Weight.LIGHT:
            self.feet[2] = Foot.DACTYLUS
        if (self.flat_list[9] == Weight.LIGHT or self.flat_list[10] == Weight.LIGHT or
                self.flat_list[8] == Weight.HEAVY):
            self.feet[3] = Foot.DACTYLUS
        if self.flat_list[5] == Weight.LIGHT or self.flat_list[6] == Weight.HEAVY:
            self.feet[0] = Foot.DACTYLUS
            self.feet[1] = Foot.DACTYLUS
        if self.flat_list[5] == Weight.HEAVY or self.flat_list[6] == Weight.LIGHT:
            self.feet[2] = Foot.DACTYLUS
            self.feet[3] = Foot.DACTYLUS

    def scan_for_real(self) -> None:
        if (self.flat_list[1] == Weight.HEAVY or self.flat_list[2] == Weight.HEAVY or
                self.flat_list[3] == Weight.LIGHT):
            self.feet[0] = Foot.SPONDAEUS
        elif self.flat_list[4] == Weight.HEAVY:
            self.feet[1] = Foot.SPONDAEUS
        elif self.flat_list[7] == Weight.HEAVY:
            self.feet[2] = Foot.SPONDAEUS
        elif (self.flat_list[9] == Weight.HEAVY or self.flat_list[10] == Weight.HEAVY or
              self.flat_list[8] == Weight.LIGHT):
            self.feet[3] = Foot.SPONDAEUS
        for i in range(4):
            if self.feet[i] == Foot.SPONDAEUS:
                self.fill_other_feet(Foot.SPONDAEUS, Foot.DACTYLUS)
                return

        self.__do_basic_checks()

        if self.feet[:4].count(Foot.DACTYLUS) == 3:
            self.fill_other_feet(Foot.DACTYLUS, Foot.SPONDAEUS)
        else:
            raise HexameterException("cannot determine full foot structure of single spondaeus verse")


class BalancedHexameter(Hexameter):
    """ a Hexameter with 2 Spondees and 2 Dactyls in its first 4 feet"""
    def __init__(self, text: str):
        super().__init__(text)
        self.dactyls = 0
        self.spondees = 0

    def __do_stab_in_the_dark(self) -> bool:
        """ a reasonably prevalent scenario that can shortcut all logic """
        if (self.flat_list[3] == Weight.HEAVY and self.flat_list[5] == Weight.HEAVY and
                self.flat_list[7] == Weight.HEAVY):
            self.feet[:4] = [Foot.DACTYLUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS]
            return True
        return False

    def __do_basic_checks(self) -> None:
        """ find easy pickings for balanced hexameters """
        if self.flat_list[1] == Weight.HEAVY or self.flat_list[2] == Weight.HEAVY:
            self.feet[0] = Foot.SPONDAEUS
        elif self.flat_list[1] == Weight.LIGHT or self.flat_list[2] == Weight.LIGHT:
            self.feet[0] = Foot.DACTYLUS
        if self.flat_list[3] == Weight.LIGHT:
            self.feet[:2] = [Foot.SPONDAEUS, Foot.DACTYLUS]
        if self.flat_list[4] == Weight.LIGHT:
            self.feet[1] = Foot.DACTYLUS
        elif self.flat_list[4] == Weight.HEAVY:
            self.feet[1] = Foot.SPONDAEUS
        if self.flat_list[6] == Weight.LIGHT:
            self.feet[2] = Foot.DACTYLUS
        elif self.flat_list[6] == Weight.HEAVY:
            self.feet[2] = Foot.SPONDAEUS
        if self.flat_list[7] == Weight.LIGHT:
            self.feet[2:4] = [Foot.DACTYLUS, Foot.SPONDAEUS]
        if self.flat_list[8] == Weight.HEAVY or self.flat_list[9] == Weight.HEAVY:
            self.feet[3] = Foot.SPONDAEUS
        elif self.flat_list[8] == Weight.LIGHT or self.flat_list[9] == Weight.LIGHT:
            self.feet[3] = Foot.DACTYLUS

    def scan_for_real(self) -> None:
        """ mother method for all partial algorithms """
        if self.__do_stab_in_the_dark():
            return
        self.__do_basic_checks()
        if self.flat_list[5] == Weight.LIGHT:
            if (self.feet[0] == Foot.SPONDAEUS or self.feet[1] == Foot.SPONDAEUS or
                    self.feet[2] == Foot.DACTYLUS or self.feet[3] == Foot.DACTYLUS):
                self.feet[:4] = [Foot.SPONDAEUS] * 2 + [Foot.DACTYLUS] * 2
            elif (self.feet[0] == Foot.DACTYLUS or self.feet[1] == Foot.DACTYLUS or
                    self.feet[2] == Foot.SPONDAEUS or self.feet[3] == Foot.SPONDAEUS):
                self.feet[:4] = [Foot.DACTYLUS] * 2 + [Foot.SPONDAEUS] * 2
        if self.__calculate():
            return
        if self.spondees == 1 and self.dactyls == 1:
            self.__do_reasonable_guesses()

        elif self.dactyls + self.spondees == 1:
            self.__do_last_resort()

        self.__calculate()

    def __do_reasonable_guesses(self) -> None:
        """ try some scenarios if we've found a spondee and a dactyl """
        if ((self.feet[2] == Foot.SPONDAEUS and self.feet[3] == Foot.DACTYLUS) or
                (self.feet[2] == Foot.DACTYLUS and self.feet[3] == Foot.SPONDAEUS)):
            if (self.flat_list[3] == Weight.HEAVY or self.flat_list[4] == Weight.HEAVY or
                    self.flat_list[1] == Weight.LIGHT or self.flat_list[2] == Weight.LIGHT):
                self.feet[:2] = [Foot.DACTYLUS, Foot.SPONDAEUS]
            elif (self.flat_list[1] == Weight.HEAVY or self.flat_list[2] == Weight.HEAVY or
                    self.flat_list[3] == Weight.LIGHT or self.flat_list[4] == Weight.LIGHT):
                self.feet[:2] = [Foot.SPONDAEUS, Foot.DACTYLUS]

        elif ((self.feet[0] == Foot.DACTYLUS and self.feet[1] == Foot.SPONDAEUS) or
              (self.feet[0] == Foot.SPONDAEUS and self.feet[1] == Foot.DACTYLUS)):
            if (self.flat_list[6] == Weight.HEAVY or self.flat_list[7] == Weight.HEAVY or
                    self.flat_list[8] == Weight.LIGHT or self.flat_list[9] == Weight.LIGHT):
                self.feet[2:4] = [Foot.SPONDAEUS, Foot.DACTYLUS]
            elif (self.flat_list[8] == Weight.HEAVY or self.flat_list[9] == Weight.HEAVY or
                    self.flat_list[6] == Weight.LIGHT or self.flat_list[7] == Weight.LIGHT):
                self.feet[2:4] = [Foot.DACTYLUS, Foot.SPONDAEUS]

        elif self.feet[0] == Foot.SPONDAEUS and self.feet[2] == Foot.DACTYLUS:
            if self.flat_list[3] == Weight.HEAVY or self.flat_list[7] == Weight.HEAVY:
                self.feet[1] = Foot.SPONDAEUS
                self.feet[3] = Foot.DACTYLUS

            elif self.flat_list[5] == Weight.HEAVY:
                self.feet[1] = Foot.DACTYLUS
                self.feet[3] = Foot.SPONDAEUS

        elif self.feet[0] == Foot.SPONDAEUS and self.feet[3] == Foot.DACTYLUS:
            if self.flat_list[3] == Weight.HEAVY:
                self.feet[1:3] = [Foot.SPONDAEUS, Foot.DACTYLUS]

            elif self.flat_list[5] == Weight.HEAVY:
                self.feet[1:3] = [Foot.DACTYLUS, Foot.SPONDAEUS]

        elif self.feet[1] == Foot.SPONDAEUS and self.feet[2] == Foot.DACTYLUS:
            if self.flat_list[7] == Weight.HEAVY:
                self.feet[0] = Foot.SPONDAEUS
                self.feet[3] = Foot.DACTYLUS

            elif self.flat_list[5] == Weight.HEAVY:
                self.feet[0] = Foot.DACTYLUS
                self.feet[3] = Foot.SPONDAEUS

        elif self.feet[1] == Foot.SPONDAEUS and self.feet[3] == Foot.DACTYLUS and self.flat_list[5] == Weight.HEAVY:
            self.feet[0] = Foot.DACTYLUS
            self.feet[2] = Foot.SPONDAEUS
        else:
            self.__continue_search()

    def __continue_search(self) -> None:
        """ do search if we've found 2 feet """
        if self.feet[0] == Foot.DACTYLUS and self.feet[2] == Foot.SPONDAEUS:
            if self.flat_list[5] == Weight.HEAVY:
                self.feet[1] = Foot.SPONDAEUS
                self.feet[3] = Foot.DACTYLUS

        elif self.feet[0] == Foot.DACTYLUS and self.feet[3] == Foot.SPONDAEUS:
            if self.flat_list[7] == Weight.HEAVY:
                self.feet[1:3] = [Foot.DACTYLUS, Foot.SPONDAEUS]

            elif self.flat_list[5] == Weight.HEAVY:
                self.feet[1:3] = [Foot.SPONDAEUS, Foot.DACTYLUS]

        elif self.feet[1] == Foot.DACTYLUS and self.feet[2] == Foot.SPONDAEUS:
            if self.flat_list[3] == Weight.HEAVY:
                self.feet[0] = Foot.DACTYLUS
                self.feet[3] = Foot.SPONDAEUS

            elif self.flat_list[5] == Weight.HEAVY:
                self.feet[0] = Foot.SPONDAEUS
                self.feet[3] = Foot.DACTYLUS

        elif self.feet[1] == Foot.DACTYLUS and self.feet[3] == Foot.SPONDAEUS:
            if self.flat_list[3] == Weight.HEAVY or self.flat_list[7] == Weight.HEAVY:
                self.feet[0] = Foot.DACTYLUS
                self.feet[2] = Foot.SPONDAEUS

            elif self.flat_list[5] == Weight.HEAVY:
                self.feet[0] = Foot.SPONDAEUS
                self.feet[2] = Foot.DACTYLUS

    def __do_last_resort(self) -> None:
        """ only execute method if we've only found one foot so far"""
        if ((self.feet[0] == Foot.SPONDAEUS and self.flat_list[3] == Weight.HEAVY) or
                (self.feet[2] == Foot.DACTYLUS and self.flat_list[7] == Weight.HEAVY)):
            self.feet[:4] = [Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS]

        elif ((self.feet[1] == Foot.DACTYLUS and self.flat_list[3] == Weight.HEAVY) or
              (self.feet[3] == Foot.SPONDAEUS and self.flat_list[7] == Weight.HEAVY)):
            self.feet[:4] = [Foot.DACTYLUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.SPONDAEUS]

    def __calculate(self) -> bool:
        """ method that will try to fill the feet """
        self.dactyls = self.feet[:4].count(Foot.DACTYLUS)
        self.spondees = self.feet[:4].count(Foot.SPONDAEUS)
        if self.spondees > 2 or self.dactyls > 2:
            raise HexameterException(f"{self.spondees} spondaei and {self.dactyls} dactyli in balanced verse")
        if self.spondees == 2 and self.dactyls == 2:
            return True
        if self.spondees == 2:
            self.fill_other_feet(Foot.SPONDAEUS, Foot.DACTYLUS)
            return True
        if self.dactyls == 2:
            self.fill_other_feet(Foot.DACTYLUS, Foot.SPONDAEUS)
            return True
        return False
