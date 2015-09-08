""" the main module for parsing verses """
import re
import enum
from Elisio.exceptions import ScansionException, HexameterException
from Elisio.engine.wordProcessor import Weights, Word

def set_django():
    """ in order to get to the database, we must use Django """
    import os
    if (not 'DJANGO_SETTINGS_MODULE' in os.environ or
            os.environ['DJANGO_SETTINGS_MODULE'] != 'Elisio.settings'):
        os.environ['DJANGO_SETTINGS_MODULE'] = 'Elisio.settings'
    import django
    if django.VERSION[:2] >= (1, 7):
        django.setup()

class Feet(enum.Enum):
    """ Types of verse foot """
    DACTYLUS = 0
    SPONDAEUS = 1
    TROCHAEUS = 2
    UNKNOWN = 3

    def get_length(self):
        """ number of syllables in the foot """
        return len(self.get_structure())

    def get_structure(self):
        """ available foot structures """
        if self == Feet.DACTYLUS:
            return [Weights.HEAVY, Weights.LIGHT, Weights.LIGHT]
        elif self == Feet.SPONDAEUS:
            return [Weights.HEAVY, Weights.HEAVY]
        elif self == Feet.TROCHAEUS:
            return [Weights.HEAVY, Weights.LIGHT]
        raise ScansionException("currently illegal foot structure: " + self)

class Verse(object):
    """ Verse class
    A verse is the representation of the Latin text of a verse
    It has no knowledge of its surroundings or context
    """
    def __init__(self, text):
        """ construct a Verse by its contents """
        if not isinstance(text, str):
            raise ScansionException("Verse must be initialized with text data")
        self.text = text
        self.words = []

    def split(self):
        """ Split a Verse into Words, remembering only the letter characters """
        txt = self.text.strip()
        if self.words != []:
            return
        array = re.split('[^a-zA-Z]+', txt)
        for word in array:
            if word.isalpha():
                self.words.append(Word(word))

    def __repr__(self):
        return self.words
    def __str__(self):
        return self.words

    def __eq__(self, other):
        """ Verses are equal if they have exactly the same characters """
        return self.text == other.text

    def get_syllable_weights(self):
        """ get available weights of syllables """
        result = []
        for count, word in enumerate(self.words):
            try:
                result.append(word.get_syllable_structure(self.words[count+1]))
            except IndexError:
                result.append(word.get_syllable_structure())
        return result

    def preparse(self):
        """ prepare the list of Syllable weights """
        layered_list = self.get_syllable_weights()
        for word in layered_list:
            # TODO: open monosyllables ? se me ne are all heavy
            for weight in word:
                if weight != Weights.NONE:
                    self.flat_list.append(weight)

    def get_split_syllables(self):
        result = ""
        for word in self.words:
            for syll in word.syllables:
                for snd in syll.sounds:
                    for ltr in snd.letters:
                        result += ltr.letter
                result += "-"
            result = result[:-1] + " "
        return result

class Hexameter(Verse):
    """ the most popular Latin verse type """
    # CONSTANTS
    MAX_SYLL = 17
    MIN_SYLL = 12

    def __init__(self, text):
        super(Hexameter, self).__init__(text)
        self.max_syllables = Hexameter.MAX_SYLL
        self.min_syllables = Hexameter.MIN_SYLL
        self.feet = [None]*6
        self.flat_list = []
        self.hex = None

    def __construct_hexameter(self):
        """ factory method """
        if len(self.flat_list) == self.min_syllables:
            self.hex = SpondaicHexameter(self.text)
        elif len(self.flat_list) == self.min_syllables + 1:
            self.hex = SpondaicDominantHexameter(self.text)
        elif len(self.flat_list) == self.max_syllables - 2:
            self.hex = BalancedHexameter(self.text)
        elif len(self.flat_list) == self.max_syllables - 1:
            self.hex = DactylicDominantHexameter(self.text)
        elif len(self.flat_list) == self.max_syllables:
            self.hex = DactylicHexameter(self.text)
        else:
            raise HexameterException("{0} is an illegal number of"
                                     "syllables in a Hexameter"
                                     .format(len(self.flat_list)))

    def scan(self):
        """ main outward-facing method to be used for scanning purposes """
        self.preparse()
        if (self.flat_list[-3] == Weights.HEAVY or
                self.flat_list[-4] == Weights.HEAVY or
                self.flat_list[-5] == Weights.LIGHT):
            self.feet[4] = Feet.SPONDAEUS
            self.max_syllables -= 1
        else:
            self.feet[4] = Feet.DACTYLUS
            self.min_syllables += 1
        if self.flat_list[-1] == Weights.HEAVY:
            self.feet[5] = Feet.SPONDAEUS
        else:
            self.feet[5] = Feet.TROCHAEUS

        self.__construct_hexameter()
        # TODO: not a very elegant solution
        self.hex.flat_list = self.flat_list
        self.hex.max_syllables = self.max_syllables
        self.hex.min_syllables = self.min_syllables
        self.hex.feet = self.feet
        self.hex.scan_for_real()
        self.feet = self.hex.feet
        # control mechanism and syllable filler
        start = 0
        for feet_num, foot in enumerate(self.feet):
            if foot is None:
                raise ScansionException("impossible to determine foot"
                                        " number {0}".format(feet_num))
            for count, weight in enumerate(foot.get_structure()):
                if (weight != Weights.ANCEPS and
                        self.flat_list[count+start] != Weights.ANCEPS and
                        weight != self.flat_list[count+start]):
                    raise ScansionException("weight #{0} was already {1}"
                                            ", tried to assign {2}"
                                            .format(count+start,
                                                    str(self.flat_list[count+start]),
                                                    str(weight)))
                self.flat_list[count+start] = weight
            start += foot.get_length()

    def fill_other_feet(self, from_foot, to_foot):
        """ only use after certifying that all necessary info is present """
        for count, foot in enumerate(self.feet):
            if count < 4 and foot != from_foot:
                self.feet[count] = to_foot

    def scan_for_real(self):
        """ main scanning method, written to be overridden """
        pass

class SpondaicHexameter(Hexameter):
    """ a Hexameter with 4 Spondees in its first 4 feet """
    def __init__(self, text):
        super(SpondaicHexameter, self).__init__(text)
    def scan_for_real(self):
        for i in range(0, 4):
            self.feet[i] = Feet.SPONDAEUS

class DactylicHexameter(Hexameter):
    """ a Hexameter with 4 Dactyls in its first 4 feet """
    def __init__(self, text):
        super(DactylicHexameter, self).__init__(text)
    def scan_for_real(self):
        for i in range(0, 4):
            self.feet[i] = Feet.DACTYLUS

class SpondaicDominantHexameter(Hexameter):
    """ a Hexameter with 3 Spondees and 1 Dactyl in its first 4 feet """
    def __init__(self, text):
        super(SpondaicDominantHexameter, self).__init__(text)
    def scan_for_real(self):
        if len(self.flat_list) != self.min_syllables + 1:
            # avoid wrong use
            raise HexameterException("a verse of {0} syllables cannot "
                                     "have exactly one dactylus in foot 1-4"
                                     .format(len(self.flat_list)))
        dact = False
        for count, weight in enumerate(self.flat_list):
            if count > 0 and count < 9 and weight == Weights.LIGHT:
                self.feet[(count-1)//2] = Feet.DACTYLUS
                dact = True
                break
        if dact:
            self.fill_other_feet(Feet.DACTYLUS, Feet.SPONDAEUS)
        else:
            for count, weight in enumerate(self.flat_list):
                if count > 0 and count < 9 and weight == Weights.HEAVY:
                    self.feet[(count-1)//2] = Feet.SPONDAEUS
            heavies = 0
            for i in range(0, 4):
                if self.feet[i] == Feet.SPONDAEUS:
                    heavies += 1
            if heavies == 3:
                self.fill_other_feet(Feet.SPONDAEUS, Feet.DACTYLUS)
            else:
                raise HexameterException("cannot determine full foot structure"+
                                         " of single dactylus verse")

class DactylicDominantHexameter(Hexameter):
    """ a Hexameter with 3 Dactyls and 1 Spondee in its first 4 feet """
    def __init__(self, text):
        super(DactylicDominantHexameter, self).__init__(text)

    def __do_basic_checks(self):
        """ do easy pickings for DD hexameter """
        if (self.flat_list[1] == Weights.LIGHT or
                self.flat_list[2] == Weights.LIGHT or
                self.flat_list[3] == Weights.HEAVY):
            self.feet[0] = Feet.DACTYLUS
        if self.flat_list[4] == Weights.LIGHT:
            self.feet[1] = Feet.DACTYLUS
        if self.flat_list[7] == Weights.LIGHT:
            self.feet[2] = Feet.DACTYLUS
        if (self.flat_list[9] == Weights.LIGHT or
                self.flat_list[10] == Weights.LIGHT or
                self.flat_list[8] == Weights.HEAVY):
            self.feet[3] = Feet.DACTYLUS
        if (self.flat_list[5] == Weights.LIGHT or
                self.flat_list[6] == Weights.HEAVY):
            self.feet[0] = Feet.DACTYLUS
            self.feet[1] = Feet.DACTYLUS
        if (self.flat_list[5] == Weights.HEAVY or
                self.flat_list[6] == Weights.LIGHT):
            self.feet[1] = Feet.DACTYLUS
            self.feet[2] = Feet.DACTYLUS

    def scan_for_real(self):
        if len(self.flat_list) != self.max_syllables - 1:
            # avoid wrong use
            raise HexameterException("a verse of {0} syllables cannot have"
                                     "exactly one spondaeus in foot 1-4"
                                     .format(len(self.flat_list)))
        if (self.flat_list[1] == Weights.HEAVY or
                self.flat_list[2] == Weights.HEAVY or
                self.flat_list[3] == Weights.LIGHT):
            self.feet[0] = Feet.SPONDAEUS
        elif self.flat_list[4] == Weights.HEAVY:
            self.feet[1] = Feet.SPONDAEUS
        elif self.flat_list[7] == Weights.HEAVY:
            self.feet[2] = Feet.SPONDAEUS
        elif (self.flat_list[9] == Weights.HEAVY or
              self.flat_list[10] == Weights.HEAVY or
              self.flat_list[8] == Weights.LIGHT):
            self.feet[3] = Feet.SPONDAEUS
        for i in range(0, 4):
            if self.feet[i] == Feet.SPONDAEUS:
                self.fill_other_feet(Feet.SPONDAEUS, Feet.DACTYLUS)
                return

        self.__do_basic_checks()
        dactyls = 0
        for i in range(0, 4):
            if self.feet[i] == Feet.DACTYLUS:
                dactyls += 1
        if dactyls == 3:
            self.fill_other_feet(Feet.DACTYLUS, Feet.SPONDAEUS)
        else:
            raise HexameterException("cannot determine full foot structure"+
                                     " of single spondaeus verse")


class BalancedHexameter(Hexameter):
    """ a Hexameter with 2 Spondees and 2 Dactyls in its first 4 feet"""
    def __init__(self, text):
        super(BalancedHexameter, self).__init__(text)
        self.dactyls = 0
        self.spondees = 0

    def __do_stab_in_the_dark(self):
        """ a reasonably prevalent scenario that can shortcut all logic """
        if (self.flat_list[3] == Weights.HEAVY and
                self.flat_list[5] == Weights.HEAVY and
                self.flat_list[7] == Weights.HEAVY):
            self.feet[0] = Feet.DACTYLUS
            self.feet[1] = Feet.SPONDAEUS
            self.feet[2] = Feet.SPONDAEUS
            self.feet[3] = Feet.DACTYLUS
            return True

    def __do_basic_checks(self):
        """ find easy pickings for balanced hexameters """
        if (self.flat_list[1] == Weights.HEAVY or
                self.flat_list[2] == Weights.HEAVY):
            self.feet[0] = Feet.SPONDAEUS
        elif (self.flat_list[1] == Weights.LIGHT or
              self.flat_list[2] == Weights.LIGHT):
            self.feet[0] = Feet.DACTYLUS
        if self.flat_list[3] == Weights.LIGHT:
            self.feet[0] = Feet.SPONDAEUS
            self.feet[1] = Feet.DACTYLUS
        if self.flat_list[4] == Weights.LIGHT:
            self.feet[1] = Feet.DACTYLUS
        elif self.flat_list[4] == Weights.HEAVY:
            self.feet[1] = Feet.SPONDAEUS
        if self.flat_list[6] == Weights.LIGHT:
            self.feet[2] = Feet.DACTYLUS
        elif self.flat_list[6] == Weights.HEAVY:
            self.feet[2] = Feet.SPONDAEUS
        if self.flat_list[7] == Weights.LIGHT:
            self.feet[2] = Feet.DACTYLUS
            self.feet[3] = Feet.SPONDAEUS
        if (self.flat_list[8] == Weights.HEAVY or
                self.flat_list[9] == Weights.HEAVY):
            self.feet[3] = Feet.SPONDAEUS
        elif (self.flat_list[8] == Weights.LIGHT or
              self.flat_list[9] == Weights.LIGHT):
            self.feet[3] = Feet.DACTYLUS

    def scan_for_real(self):
        """ mother method for all partial algorithms """
        if len(self.flat_list) != self.max_syllables - 2:
            # avoid wrong use
            raise HexameterException("a verse of {0} syllables "
                                     "cannot be balanced in foot 1-4"
                                     .format(len(self.flat_list)))
        if self.__do_stab_in_the_dark():
            return

        self.__do_basic_checks()

        if self.__calculate():
            return

        elif (self.flat_list[3] == Weights.HEAVY and
              self.flat_list[5] == Weights.HEAVY and
              self.flat_list[7] == Weights.HEAVY):
            self.feet[0] = Feet.DACTYLUS
            self.feet[1] = Feet.SPONDAEUS
            self.feet[2] = Feet.SPONDAEUS
            self.feet[3] = Feet.DACTYLUS
        elif ((self.feet[0] == Feet.SPONDAEUS or
               self.feet[1] == Feet.SPONDAEUS or
               self.feet[2] == Feet.DACTYLUS or
               self.feet[3] == Feet.DACTYLUS) and
              self.flat_list[5] == Weights.LIGHT):
            self.feet[0] = Feet.SPONDAEUS
            self.feet[1] = Feet.SPONDAEUS
            self.feet[2] = Feet.DACTYLUS
            self.feet[3] = Feet.DACTYLUS

        elif ((self.feet[0] == Feet.DACTYLUS or self.feet[1] == Feet.DACTYLUS or
               self.feet[2] == Feet.SPONDAEUS or self.feet[3] == Feet.SPONDAEUS)
              and self.flat_list[5] == Weights.LIGHT):
            self.feet[0] = Feet.DACTYLUS
            self.feet[1] = Feet.DACTYLUS
            self.feet[2] = Feet.SPONDAEUS
            self.feet[3] = Feet.SPONDAEUS

        elif self.spondees == 1 and self.dactyls == 1:
            self.__do_reasonable_guesses()

        elif self.dactyls+self.spondees == 1:
            self.__do_last_resort()

        self.__calculate()

    def __do_reasonable_guesses(self):
        """ try some scenarios if we've found a spondee and a dactyl """
        if self.flat_list[3] == Weights.HEAVY:
            self.feet[0] = Feet.DACTYLUS
            self.feet[1] = Feet.SPONDAEUS

        elif self.feet[0] == Feet.SPONDAEUS and self.feet[2] == Feet.DACTYLUS:
            if (self.flat_list[3] == Weights.HEAVY or
                    self.flat_list[7] == Weights.HEAVY):
                self.feet[1] = Feet.SPONDAEUS
                self.feet[3] = Feet.DACTYLUS

            elif self.flat_list[5] == Weights.HEAVY:
                self.feet[1] = Feet.DACTYLUS
                self.feet[3] = Feet.SPONDAEUS

        elif self.feet[0] == Feet.SPONDAEUS and self.feet[3] == Feet.DACTYLUS:
            if self.flat_list[3] == Weights.HEAVY:
                self.feet[1] = Feet.SPONDAEUS
                self.feet[2] = Feet.DACTYLUS

            elif self.flat_list[5] == Weights.HEAVY:
                self.feet[1] = Feet.DACTYLUS
                self.feet[2] = Feet.SPONDAEUS

        elif self.feet[1] == Feet.SPONDAEUS and self.feet[2] == Feet.DACTYLUS:
            if self.flat_list[7] == Weights.HEAVY:
                self.feet[0] = Feet.SPONDAEUS
                self.feet[3] = Feet.DACTYLUS

            elif self.flat_list[5] == Weights.HEAVY:
                self.feet[0] = Feet.DACTYLUS
                self.feet[3] = Feet.SPONDAEUS

        elif (self.feet[1] == Feet.SPONDAEUS and
              self.feet[3] == Feet.DACTYLUS and
              self.flat_list[5] == Weights.HEAVY):
            self.feet[0] = Feet.DACTYLUS
            self.feet[2] = Feet.SPONDAEUS
        else:
            self.__continue_search()

    def __continue_search(self):
        """ do search if we've found 2 feet """
        if self.feet[0] == Feet.DACTYLUS and self.feet[2] == Feet.SPONDAEUS:
            if self.flat_list[5] == Weights.HEAVY:
                self.feet[1] = Feet.SPONDAEUS
                self.feet[3] = Feet.DACTYLUS

        elif self.feet[0] == Feet.DACTYLUS and self.feet[3] == Feet.SPONDAEUS:
            if self.flat_list[7] == Weights.HEAVY:
                self.feet[1] = Feet.DACTYLUS
                self.feet[2] = Feet.SPONDAEUS

            elif self.flat_list[5] == Weights.HEAVY:
                self.feet[1] = Feet.SPONDAEUS
                self.feet[2] = Feet.DACTYLUS

        elif self.feet[1] == Feet.DACTYLUS and self.feet[2] == Feet.SPONDAEUS:
            if self.flat_list[3] == Weights.HEAVY:
                self.feet[0] = Feet.DACTYLUS
                self.feet[3] = Feet.SPONDAEUS

            elif self.flat_list[5] == Weights.HEAVY:
                self.feet[0] = Feet.SPONDAEUS
                self.feet[3] = Feet.DACTYLUS

        elif self.feet[1] == Feet.DACTYLUS and self.feet[3] == Feet.SPONDAEUS:
            if (self.flat_list[3] == Weights.HEAVY or
                    self.flat_list[7] == Weights.HEAVY):
                self.feet[0] = Feet.DACTYLUS
                self.feet[2] = Feet.SPONDAEUS

            elif self.flat_list[5] == Weights.HEAVY:
                self.feet[0] = Feet.SPONDAEUS
                self.feet[2] = Feet.DACTYLUS

    def __do_last_resort(self):
        """ only execute method if we've only found one foot so far"""
        if ((self.feet[0] == Feet.SPONDAEUS and
             self.flat_list[3] == Weights.HEAVY) or
                (self.feet[2] == Feet.DACTYLUS and
                 self.flat_list[7] == Weights.HEAVY)):
            self.feet[0] = Feet.SPONDAEUS
            self.feet[1] = Feet.SPONDAEUS
            self.feet[2] = Feet.DACTYLUS
            self.feet[3] = Feet.DACTYLUS

        elif ((self.feet[1] == Feet.DACTYLUS and
               self.flat_list[3] == Weights.HEAVY) or
              (self.feet[3] == Feet.SPONDAEUS and
               self.flat_list[7] == Weights.HEAVY)):
            self.feet[0] = Feet.DACTYLUS
            self.feet[1] = Feet.DACTYLUS
            self.feet[2] = Feet.SPONDAEUS
            self.feet[3] = Feet.SPONDAEUS

        elif self.flat_list[5] == Weights.HEAVY:
            if ((self.feet[2] == Feet.DACTYLUS or
                 self.feet[3] == Feet.SPONDAEUS) and
                    self.flat_list[3] == Weights.HEAVY):
                self.feet[0] = Feet.DACTYLUS
                self.feet[1] = Feet.SPONDAEUS
                self.feet[2] = Feet.DACTYLUS
                self.feet[3] = Feet.SPONDAEUS

            elif ((self.feet[0] == Feet.SPONDAEUS or
                   self.feet[1] == Feet.DACTYLUS) and
                  self.flat_list[5] == Weights.HEAVY):
                self.feet[0] = Feet.SPONDAEUS
                self.feet[1] = Feet.DACTYLUS
                self.feet[2] = Feet.SPONDAEUS
                self.feet[3] = Feet.DACTYLUS

            elif (((self.feet[2] == Feet.SPONDAEUS or
                    self.feet[3] == Feet.DACTYLUS) and
                   self.flat_list[3] == Weights.HEAVY) or
                  ((self.feet[0] == Feet.DACTYLUS or
                    self.feet[1] == Feet.SPONDAEUS) and
                   self.flat_list[7] == Weights.HEAVY)):
                self.feet[0] = Feet.DACTYLUS
                self.feet[1] = Feet.SPONDAEUS
                self.feet[2] = Feet.SPONDAEUS
                self.feet[3] = Feet.DACTYLUS

    def __calculate(self):
        """ method that will try to fill the feet """
        self.dactyls = 0
        self.spondees = 0
        for i in range(0, 4):
            if self.feet[i] == Feet.SPONDAEUS:
                self.spondees += 1
            if self.feet[i] == Feet.DACTYLUS:
                self.dactyls += 1
        if self.spondees > 2 or self.dactyls > 2:
            raise HexameterException(
                "{0} spondaei and {1} dactyli in balanced verse"
                .format(self.spondees, self.dactyls))
        if self.spondees == 2 and self.dactyls == 2:
            return True
        if self.spondees == 2:
            self.fill_other_feet(Feet.SPONDAEUS, Feet.DACTYLUS)
            return True
        if self.dactyls == 2:
            self.fill_other_feet(Feet.DACTYLUS, Feet.SPONDAEUS)
            return True
