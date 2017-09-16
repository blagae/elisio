from Elisio.engine.Syllable import Weight
from Elisio.engine.Verse import Verse, Foot
from Elisio.exceptions import HexameterException
from Elisio.engine.VerseFactory import VerseCreator, VerseType


class HexameterCreator(VerseCreator):
    MAX_SYLL = 17
    MIN_SYLL = 12

    def __init__(self, lst):
        self.max_syllables = HexameterCreator.MAX_SYLL
        self.min_syllables = HexameterCreator.MIN_SYLL
        self.list = lst

    def get_type(self):
        return VerseType.HEXAMETER

    def get_subtype(self):
        if len(self.list) > self.max_syllables:
            raise HexameterException("too many syllables in first pass")
        elif len(self.list) < self.min_syllables:
            raise HexameterException("too few syllables in first pass")
        if (self.list[-3] == Weight.HEAVY or
            self.list[-4] == Weight.HEAVY or
                self.list[-5] == Weight.LIGHT):
            self.max_syllables -= 1
        else:
            self.min_syllables += 1
        if len(self.list) > self.max_syllables:
            raise HexameterException("too many syllables in second pass")
        elif len(self.list) < self.min_syllables:
            raise HexameterException("too few syllables in second pass")
        length = len(self.list) - self.min_syllables
        if length == 0:
            return SpondaicHexameter
        elif length == 1:
            return SpondaicDominantHexameter
        elif length == 2:
            return BalancedHexameter
        elif length == 3:
            return DactylicDominantHexameter
        elif length == 4:
            return DactylicHexameter
        else:
            raise HexameterException("{0} is an illegal number of"
                                     "syllables in a Hexameter"
                                     .format(len(self.list)))


class Hexameter(Verse):
    """ the most popular Latin verse type """

    def __init__(self, text):
        super(Hexameter, self).__init__(text)
        self.feet = [None] * 6
        self.hex = None

    def preparse(self):
        try:
            for i in range(0, len(self.flat_list)):
                if self.flat_list[i] == Weight.HEAVY and self.flat_list[i + 2] == Weight.HEAVY:
                    if self.flat_list[i + 1] == Weight.LIGHT:
                        raise HexameterException("cannot assign HEAVY to LIGHT syllable #" + str(i + 1))
                    else:
                        self.flat_list[i + 1] = Weight.HEAVY
                elif self.flat_list[i] == Weight.LIGHT and self.flat_list[i + 1] == Weight.LIGHT:
                    self.flat_list[i + 2] = Weight.HEAVY
                    self.flat_list[i - 1] = Weight.HEAVY
        except IndexError:
            pass

    def scan(self):
        """ main outward-facing method to be used for scanning purposes """
        # should be refactored
        if (self.flat_list[-3] == Weight.HEAVY or
            self.flat_list[-4] == Weight.HEAVY or
                self.flat_list[-5] == Weight.LIGHT):
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

    def fill_other_feet(self, from_foot, to_foot):
        """ only use after certifying that all necessary info is present """
        for count, foot in enumerate(self.feet):
            if count < 4 and foot != from_foot:
                self.feet[count] = to_foot

    def scan_for_real(self):
        pass


class SpondaicHexameter(Hexameter):
    """ a Hexameter with 4 Spondees in its first 4 feet """

    def __init__(self, text):
        super(SpondaicHexameter, self).__init__(text)

    def scan_for_real(self):
        for i in range(0, 4):
            self.feet[i] = Foot.SPONDAEUS


class DactylicHexameter(Hexameter):
    """ a Hexameter with 4 Dactyls in its first 4 feet """

    def __init__(self, text):
        super(DactylicHexameter, self).__init__(text)

    def scan_for_real(self):
        for i in range(0, 4):
            self.feet[i] = Foot.DACTYLUS


class SpondaicDominantHexameter(Hexameter):
    """ a Hexameter with 3 Spondees and 1 Dactyl in its first 4 feet """

    def __init__(self, text):
        super(SpondaicDominantHexameter, self).__init__(text)

    def scan_for_real(self):
        dact = False
        for count, weight in enumerate(self.flat_list):
            if 0 < count < 9 and weight == Weight.LIGHT:
                self.feet[(count - 1) // 2] = Foot.DACTYLUS
                dact = True
                break
        if dact:
            self.fill_other_feet(Foot.DACTYLUS, Foot.SPONDAEUS)
        else:
            for count, weight in enumerate(self.flat_list):
                if 0 < count < 9 and weight == Weight.HEAVY:
                    self.feet[(count - 1) // 2] = Foot.SPONDAEUS
            heavies = self.feet[0:4].count(Foot.SPONDAEUS)
            if heavies == 3:
                self.fill_other_feet(Foot.SPONDAEUS, Foot.DACTYLUS)
            else:
                raise HexameterException("cannot determine full foot structure" +
                                         " of single dactylus verse")


class DactylicDominantHexameter(Hexameter):
    """ a Hexameter with 3 Dactyls and 1 Spondee in its first 4 feet """

    def __init__(self, text):
        super(DactylicDominantHexameter, self).__init__(text)

    def __do_basic_checks(self):
        """ do easy pickings for DD hexameter """
        if (self.flat_list[1] == Weight.LIGHT or
            self.flat_list[2] == Weight.LIGHT or
                self.flat_list[3] == Weight.HEAVY):
            self.feet[0] = Foot.DACTYLUS
        if self.flat_list[4] == Weight.LIGHT:
            self.feet[1] = Foot.DACTYLUS
        if self.flat_list[7] == Weight.LIGHT:
            self.feet[2] = Foot.DACTYLUS
        if (self.flat_list[9] == Weight.LIGHT or
            self.flat_list[10] == Weight.LIGHT or
                self.flat_list[8] == Weight.HEAVY):
            self.feet[3] = Foot.DACTYLUS
        if (self.flat_list[5] == Weight.LIGHT or
                self.flat_list[6] == Weight.HEAVY):
            self.feet[0] = Foot.DACTYLUS
            self.feet[1] = Foot.DACTYLUS
        if (self.flat_list[5] == Weight.HEAVY or
                self.flat_list[6] == Weight.LIGHT):
            self.feet[2] = Foot.DACTYLUS
            self.feet[3] = Foot.DACTYLUS

    def scan_for_real(self):
        if (self.flat_list[1] == Weight.HEAVY or
            self.flat_list[2] == Weight.HEAVY or
                self.flat_list[3] == Weight.LIGHT):
            self.feet[0] = Foot.SPONDAEUS
        elif self.flat_list[4] == Weight.HEAVY:
            self.feet[1] = Foot.SPONDAEUS
        elif self.flat_list[7] == Weight.HEAVY:
            self.feet[2] = Foot.SPONDAEUS
        elif (self.flat_list[9] == Weight.HEAVY or
                self.flat_list[10] == Weight.HEAVY or
              self.flat_list[8] == Weight.LIGHT):
            self.feet[3] = Foot.SPONDAEUS
        for i in range(0, 4):
            if self.feet[i] == Foot.SPONDAEUS:
                self.fill_other_feet(Foot.SPONDAEUS, Foot.DACTYLUS)
                return

        self.__do_basic_checks()
        dactyls = self.feet[0:4].count(Foot.DACTYLUS)
        if dactyls == 3:
            self.fill_other_feet(Foot.DACTYLUS, Foot.SPONDAEUS)
        else:
            raise HexameterException("cannot determine full foot structure" +
                                     " of single spondaeus verse")


class BalancedHexameter(Hexameter):
    """ a Hexameter with 2 Spondees and 2 Dactyls in its first 4 feet"""

    def __init__(self, text):
        super(BalancedHexameter, self).__init__(text)
        self.dactyls = 0
        self.spondees = 0

    def __do_stab_in_the_dark(self):
        """ a reasonably prevalent scenario that can shortcut all logic """
        if (self.flat_list[3] == Weight.HEAVY and
            self.flat_list[5] == Weight.HEAVY and
                self.flat_list[7] == Weight.HEAVY):
            self.feet[0] = Foot.DACTYLUS
            self.feet[1] = Foot.SPONDAEUS
            self.feet[2] = Foot.SPONDAEUS
            self.feet[3] = Foot.DACTYLUS
            return True

    def __do_basic_checks(self):
        """ find easy pickings for balanced hexameters """
        if (self.flat_list[1] == Weight.HEAVY or
                self.flat_list[2] == Weight.HEAVY):
            self.feet[0] = Foot.SPONDAEUS
        elif (self.flat_list[1] == Weight.LIGHT or
              self.flat_list[2] == Weight.LIGHT):
            self.feet[0] = Foot.DACTYLUS
        if self.flat_list[3] == Weight.LIGHT:
            self.feet[0] = Foot.SPONDAEUS
            self.feet[1] = Foot.DACTYLUS
        if self.flat_list[4] == Weight.LIGHT:
            self.feet[1] = Foot.DACTYLUS
        elif self.flat_list[4] == Weight.HEAVY:
            self.feet[1] = Foot.SPONDAEUS
        if self.flat_list[6] == Weight.LIGHT:
            self.feet[2] = Foot.DACTYLUS
        elif self.flat_list[6] == Weight.HEAVY:
            self.feet[2] = Foot.SPONDAEUS
        if self.flat_list[7] == Weight.LIGHT:
            self.feet[2] = Foot.DACTYLUS
            self.feet[3] = Foot.SPONDAEUS
        if (self.flat_list[8] == Weight.HEAVY or
                self.flat_list[9] == Weight.HEAVY):
            self.feet[3] = Foot.SPONDAEUS
        elif (self.flat_list[8] == Weight.LIGHT or
              self.flat_list[9] == Weight.LIGHT):
            self.feet[3] = Foot.DACTYLUS

    def scan_for_real(self):
        """ mother method for all partial algorithms """
        if self.__do_stab_in_the_dark():
            return

        self.__do_basic_checks()

        if self.__calculate():
            return

        elif (self.flat_list[3] == Weight.HEAVY and
              self.flat_list[5] == Weight.HEAVY and
              self.flat_list[7] == Weight.HEAVY):
            self.feet[0] = Foot.DACTYLUS
            self.feet[1] = Foot.SPONDAEUS
            self.feet[2] = Foot.SPONDAEUS
            self.feet[3] = Foot.DACTYLUS
        elif ((self.feet[0] == Foot.SPONDAEUS or
               self.feet[1] == Foot.SPONDAEUS or
               self.feet[2] == Foot.DACTYLUS or
               self.feet[3] == Foot.DACTYLUS) and
                self.flat_list[5] == Weight.LIGHT):
            self.feet[0] = Foot.SPONDAEUS
            self.feet[1] = Foot.SPONDAEUS
            self.feet[2] = Foot.DACTYLUS
            self.feet[3] = Foot.DACTYLUS

        elif ((self.feet[0] == Foot.DACTYLUS or self.feet[1] == Foot.DACTYLUS or
               self.feet[2] == Foot.SPONDAEUS or self.feet[3] == Foot.SPONDAEUS) and
              self.flat_list[5] == Weight.LIGHT):
            self.feet[0] = Foot.DACTYLUS
            self.feet[1] = Foot.DACTYLUS
            self.feet[2] = Foot.SPONDAEUS
            self.feet[3] = Foot.SPONDAEUS

        elif self.spondees == 1 and self.dactyls == 1:
            self.__do_reasonable_guesses()

        elif self.dactyls + self.spondees == 1:
            self.__do_last_resort()

        self.__calculate()

    def __do_reasonable_guesses(self):
        """ try some scenarios if we've found a spondee and a dactyl """
        if ((self.feet[2] == Foot.SPONDAEUS and self.feet[3] == Foot.DACTYLUS) or
                (self.feet[2] == Foot.DACTYLUS and self.feet[3] == Foot.SPONDAEUS)):
            if self.flat_list[3] == Weight.HEAVY or self.flat_list[4] == Weight.HEAVY:
                self.feet[0] = Foot.DACTYLUS
                self.feet[1] = Foot.SPONDAEUS
            elif self.flat_list[1] == Weight.HEAVY or self.flat_list[2] == Weight.HEAVY:
                self.feet[0] = Foot.SPONDAEUS
                self.feet[1] = Foot.DACTYLUS
            elif self.flat_list[1] == Weight.LIGHT or self.flat_list[2] == Weight.LIGHT:
                self.feet[0] = Foot.DACTYLUS
                self.feet[1] = Foot.SPONDAEUS
            elif self.flat_list[3] == Weight.LIGHT or self.flat_list[4] == Weight.LIGHT:
                self.feet[0] = Foot.SPONDAEUS
                self.feet[1] = Foot.DACTYLUS

        elif ((self.feet[0] == Foot.DACTYLUS and self.feet[1] == Foot.SPONDAEUS) or
              (self.feet[0] == Foot.SPONDAEUS and self.feet[1] == Foot.DACTYLUS)):
            if self.flat_list[6] == Weight.HEAVY or self.flat_list[7] == Weight.HEAVY:
                self.feet[2] = Foot.SPONDAEUS
                self.feet[3] = Foot.DACTYLUS
            elif self.flat_list[8] == Weight.HEAVY or self.flat_list[9] == Weight.HEAVY:
                self.feet[2] = Foot.DACTYLUS
                self.feet[3] = Foot.SPONDAEUS
            elif self.flat_list[6] == Weight.LIGHT or self.flat_list[7] == Weight.LIGHT:
                self.feet[2] = Foot.DACTYLUS
                self.feet[3] = Foot.SPONDAEUS
            elif self.flat_list[8] == Weight.LIGHT or self.flat_list[9] == Weight.LIGHT:
                self.feet[2] = Foot.SPONDAEUS
                self.feet[3] = Foot.DACTYLUS

        elif self.feet[0] == Foot.SPONDAEUS and self.feet[2] == Foot.DACTYLUS:
            if (self.flat_list[3] == Weight.HEAVY or
                    self.flat_list[7] == Weight.HEAVY):
                self.feet[1] = Foot.SPONDAEUS
                self.feet[3] = Foot.DACTYLUS

            elif self.flat_list[5] == Weight.HEAVY:
                self.feet[1] = Foot.DACTYLUS
                self.feet[3] = Foot.SPONDAEUS

        elif self.feet[0] == Foot.SPONDAEUS and self.feet[3] == Foot.DACTYLUS:
            if self.flat_list[3] == Weight.HEAVY:
                self.feet[1] = Foot.SPONDAEUS
                self.feet[2] = Foot.DACTYLUS

            elif self.flat_list[5] == Weight.HEAVY:
                self.feet[1] = Foot.DACTYLUS
                self.feet[2] = Foot.SPONDAEUS

        elif self.feet[1] == Foot.SPONDAEUS and self.feet[2] == Foot.DACTYLUS:
            if self.flat_list[7] == Weight.HEAVY:
                self.feet[0] = Foot.SPONDAEUS
                self.feet[3] = Foot.DACTYLUS

            elif self.flat_list[5] == Weight.HEAVY:
                self.feet[0] = Foot.DACTYLUS
                self.feet[3] = Foot.SPONDAEUS

        elif (self.feet[1] == Foot.SPONDAEUS and
              self.feet[3] == Foot.DACTYLUS and
              self.flat_list[5] == Weight.HEAVY):
            self.feet[0] = Foot.DACTYLUS
            self.feet[2] = Foot.SPONDAEUS
        else:
            self.__continue_search()

    def __continue_search(self):
        """ do search if we've found 2 feet """
        if self.feet[0] == Foot.DACTYLUS and self.feet[2] == Foot.SPONDAEUS:
            if self.flat_list[5] == Weight.HEAVY:
                self.feet[1] = Foot.SPONDAEUS
                self.feet[3] = Foot.DACTYLUS

        elif self.feet[0] == Foot.DACTYLUS and self.feet[3] == Foot.SPONDAEUS:
            if self.flat_list[7] == Weight.HEAVY:
                self.feet[1] = Foot.DACTYLUS
                self.feet[2] = Foot.SPONDAEUS

            elif self.flat_list[5] == Weight.HEAVY:
                self.feet[1] = Foot.SPONDAEUS
                self.feet[2] = Foot.DACTYLUS

        elif self.feet[1] == Foot.DACTYLUS and self.feet[2] == Foot.SPONDAEUS:
            if self.flat_list[3] == Weight.HEAVY:
                self.feet[0] = Foot.DACTYLUS
                self.feet[3] = Foot.SPONDAEUS

            elif self.flat_list[5] == Weight.HEAVY:
                self.feet[0] = Foot.SPONDAEUS
                self.feet[3] = Foot.DACTYLUS

        elif self.feet[1] == Foot.DACTYLUS and self.feet[3] == Foot.SPONDAEUS:
            if (self.flat_list[3] == Weight.HEAVY or
                    self.flat_list[7] == Weight.HEAVY):
                self.feet[0] = Foot.DACTYLUS
                self.feet[2] = Foot.SPONDAEUS

            elif self.flat_list[5] == Weight.HEAVY:
                self.feet[0] = Foot.SPONDAEUS
                self.feet[2] = Foot.DACTYLUS

    def __do_last_resort(self):
        """ only execute method if we've only found one foot so far"""
        if ((self.feet[0] == Foot.SPONDAEUS and
             self.flat_list[3] == Weight.HEAVY) or
                (self.feet[2] == Foot.DACTYLUS and
                 self.flat_list[7] == Weight.HEAVY)):
            self.feet[0] = Foot.SPONDAEUS
            self.feet[1] = Foot.SPONDAEUS
            self.feet[2] = Foot.DACTYLUS
            self.feet[3] = Foot.DACTYLUS

        elif ((self.feet[1] == Foot.DACTYLUS and
               self.flat_list[3] == Weight.HEAVY) or
              (self.feet[3] == Foot.SPONDAEUS and
               self.flat_list[7] == Weight.HEAVY)):
            self.feet[0] = Foot.DACTYLUS
            self.feet[1] = Foot.DACTYLUS
            self.feet[2] = Foot.SPONDAEUS
            self.feet[3] = Foot.SPONDAEUS

        elif self.flat_list[5] == Weight.HEAVY:
            if ((self.feet[2] == Foot.DACTYLUS or
                 self.feet[3] == Foot.SPONDAEUS) and
                    self.flat_list[3] == Weight.HEAVY):
                self.feet[0] = Foot.DACTYLUS
                self.feet[1] = Foot.SPONDAEUS
                self.feet[2] = Foot.DACTYLUS
                self.feet[3] = Foot.SPONDAEUS

            elif ((self.feet[0] == Foot.SPONDAEUS or
                   self.feet[1] == Foot.DACTYLUS) and
                    self.flat_list[5] == Weight.HEAVY):
                self.feet[0] = Foot.SPONDAEUS
                self.feet[1] = Foot.DACTYLUS
                self.feet[2] = Foot.SPONDAEUS
                self.feet[3] = Foot.DACTYLUS

            elif (((self.feet[2] == Foot.SPONDAEUS or
                    self.feet[3] == Foot.DACTYLUS) and
                    self.flat_list[3] == Weight.HEAVY) or
                  ((self.feet[0] == Foot.DACTYLUS or
                    self.feet[1] == Foot.SPONDAEUS) and
                    self.flat_list[7] == Weight.HEAVY)):
                self.feet[0] = Foot.DACTYLUS
                self.feet[1] = Foot.SPONDAEUS
                self.feet[2] = Foot.SPONDAEUS
                self.feet[3] = Foot.DACTYLUS

    def __calculate(self):
        """ method that will try to fill the feet """
        self.dactyls = self.feet[0:4].count(Foot.DACTYLUS)
        self.spondees = self.feet[0:4].count(Foot.SPONDAEUS)
        if self.spondees > 2 or self.dactyls > 2:
            raise HexameterException(
                "{0} spondaei and {1} dactyli in balanced verse".format(self.spondees, self.dactyls))
        if self.spondees == 2 and self.dactyls == 2:
            return True
        if self.spondees == 2:
            self.fill_other_feet(Foot.SPONDAEUS, Foot.DACTYLUS)
            return True
        if self.dactyls == 2:
            self.fill_other_feet(Foot.DACTYLUS, Foot.SPONDAEUS)
            return True
