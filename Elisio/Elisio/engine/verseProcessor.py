import re
import enum
from Elisio.exceptions import ScansionException, HexameterException
from Elisio.engine.wordProcessor import *

def setDjango():
    import os
    if not 'DJANGO_SETTINGS_MODULE' in os.environ or os.environ['DJANGO_SETTINGS_MODULE'] != 'Elisio.settings':
        os.environ['DJANGO_SETTINGS_MODULE'] = 'Elisio.settings'

class Feet(enum.Enum):
    DACTYLUS = 0
    SPONDAEUS = 1
    TROCHAEUS = 2
    UNKNOWN = 3

    def getLength(self):
        return len(self.getStructure())

    def getStructure(self):
        if self == Feet.DACTYLUS:
            return [SyllableWeights.HEAVY, SyllableWeights.LIGHT, SyllableWeights.LIGHT]
        elif self == Feet.SPONDAEUS:
            return [SyllableWeights.HEAVY, SyllableWeights.HEAVY]
        elif self == Feet.TROCHAEUS:
            return [SyllableWeights.HEAVY, SyllableWeights.LIGHT]
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
        s = self.text.strip()
        if self.words != []:
            return
        array = re.split('[^a-zA-Z]+', s)
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

    def getSyllableLengths(self):
        result = []
        for count, word in enumerate(self.words):
            try:
                result.append(word.getSyllableStructure(self.words[count+1]))
            except IndexError:
                result.append(word.getSyllableStructure())
        return result


class Hexameter(Verse):
    # CONSTANTS
    MAX_SYLL = 17
    MIN_SYLL = 12

    def __init__(self, text):
        super(Hexameter, self).__init__(text)
        self.max_syllables = Hexameter.MAX_SYLL
        self.min_syllables = Hexameter.MIN_SYLL
        self.feet = [None]*6
        self.flatList = []

    def preparse(self):
        layeredList = self.getSyllableLengths()
        for word in layeredList:
            # TODO: open monosyllables ? se me ne are all heavy
            for weight in word:
                if weight != SyllableWeights.NONE:
                    self.flatList.append(weight)

    def scan(self):
        self.preparse()
        if self.flatList[-3] == SyllableWeights.HEAVY or self.flatList[-4] == SyllableWeights.HEAVY or self.flatList[-5] == SyllableWeights.LIGHT:
            self.feet[4] = Feet.SPONDAEUS
            self.max_syllables -= 1
        else:
            self.feet[4] = Feet.DACTYLUS
            self.min_syllables += 1
        if self.flatList[-1] == SyllableWeights.HEAVY:
            self.feet[5] = Feet.SPONDAEUS
        else:
            self.feet[5] = Feet.TROCHAEUS
        if len(self.flatList) == self.min_syllables:
            self.hex = SpondaicHexameter(self.text)
        elif len(self.flatList) == self.min_syllables + 1:
            self.hex = SpondaicDominantHexameter(self.text)
        elif len(self.flatList) == self.max_syllables - 2:
            self.hex = BalancedHexameter(self.text)
        elif len(self.flatList) == self.max_syllables - 1:
            self.hex = DactylicDominantHexameter(self.text)
        elif len(self.flatList) == self.max_syllables:
            self.hex = DactylicHexameter(self.text)
        else:
            raise HexameterException("{0} is an illegal number of syllables in a Hexameter".format(len(self.flatList)))
        # TODO: not a very elegant solution
        self.hex.flatList = self.flatList
        self.hex.max_syllables = self.max_syllables
        self.hex.min_syllables = self.min_syllables
        self.hex.feet = self.feet
        self.hex.scanForReal()
        self.feet = self.hex.feet
        # control mechanism and syllable filler
        start = 0
        for feetNum, foot in enumerate(self.feet):
            if foot is None:
                raise ScansionException("impossible to determine foot number {0}".format(feetNum))
            for count, weight in enumerate(foot.getStructure()):
                if weight != SyllableWeights.ANCEPS and self.flatList[count+start] != SyllableWeights.ANCEPS and weight != self.flatList[count+start]:
                    raise ScansionException("weight #{0} was already {1}, tried to assign {2}".format(count+start, str(self.flatList[count+start]), str(weight)))
                self.flatList[count+start] = weight
            start += foot.getLength()

    def fillOtherFeet(self, fromFoot, toFoot):
        for count, foot in enumerate(self.feet):
            if count < 4 and foot != fromFoot:
                self.feet[count] = toFoot

    #TO OVERRIDE
    def scanForReal(self):
        pass

class SpondaicHexameter(Hexameter):
    def __init__(self, text):
        super(SpondaicHexameter, self).__init__(text)
    def scanForReal(self):
        for i in range (0, 4):
            self.feet[i] = Feet.SPONDAEUS

class DactylicHexameter(Hexameter):
    def __init__(self, text):
        super(DactylicHexameter, self).__init__(text)
    def scanForReal(self):
        for i in range (0, 4):
            self.feet[i] = Feet.DACTYLUS

class SpondaicDominantHexameter(Hexameter):
    def __init__(self, text):
        super(SpondaicDominantHexameter, self).__init__(text)
    def scanForReal(self):
        if len(self.flatList) != self.min_syllables + 1:
            """ avoid wrong use """
            raise HexameterException("a verse of {0} syllables cannot have exactly one dactylus in foot 1-4".format(len(self.flatList)))
        dact = False
        for count, weight in enumerate(self.flatList):
            if count > 0 and count < 9 and weight == SyllableWeights.LIGHT:
                self.feet[(count-1)//2] = Feet.DACTYLUS
                dact = True
                break
        if dact:
            self.fillOtherFeet(Feet.DACTYLUS, Feet.SPONDAEUS)
        else:
            
            for count, weight in enumerate(self.flatList):
                if count > 0 and count < 9 and weight == SyllableWeights.HEAVY:
                    self.feet[(count-1)//2] = Feet.SPONDAEUS
            heavies = 0
            for i in range (0, 4):
                if self.feet[i] == Feet.SPONDAEUS:
                    heavies += 1
            if heavies == 3:
                self.fillOtherFeet(Feet.SPONDAEUS, Feet.DACTYLUS)
            else:
                raise HexameterException("cannot determine full foot structure of single dactylus verse")

class DactylicDominantHexameter(Hexameter):
    def __init__(self, text):
        super(DactylicDominantHexameter, self).__init__(text)
    def scanForReal(self):
        if len(self.flatList) != self.max_syllables - 1:
            """ avoid wrong use """
            raise HexameterException("a verse of {0} syllables cannot have exactly one spondaeus in foot 1-4".format(len(self.flatList)))
        if self.flatList[1] == SyllableWeights.HEAVY or self.flatList[2] == SyllableWeights.HEAVY or self.flatList[3] == SyllableWeights.LIGHT:
            self.feet[0] = Feet.SPONDAEUS
        elif self.flatList[4] == SyllableWeights.HEAVY:
            self.feet[1] = Feet.SPONDAEUS
        elif self.flatList[7] == SyllableWeights.HEAVY:
            self.feet[2] = Feet.SPONDAEUS
        elif self.flatList[9] == SyllableWeights.HEAVY or self.flatList[10] == SyllableWeights.HEAVY or self.flatList[8] == SyllableWeights.LIGHT:
            self.feet[3] = Feet.SPONDAEUS
        for i in range (0, 4):
            if self.feet[i] == Feet.SPONDAEUS:
                self.fillOtherFeet(Feet.SPONDAEUS, Feet.DACTYLUS)
                return
        if self.flatList[1] == SyllableWeights.LIGHT or self.flatList[2] == SyllableWeights.LIGHT or self.flatList[3] == SyllableWeights.HEAVY:
            self.feet[0] = Feet.DACTYLUS
        if self.flatList[4] == SyllableWeights.LIGHT:
            self.feet[1] = Feet.DACTYLUS
        if self.flatList[7] == SyllableWeights.LIGHT:
            self.feet[2] = Feet.DACTYLUS
        if self.flatList[9] == SyllableWeights.LIGHT or self.flatList[10] == SyllableWeights.LIGHT or self.flatList[8] == SyllableWeights.HEAVY:
            self.feet[3] = Feet.DACTYLUS
        if self.flatList[5] == SyllableWeights.LIGHT or self.flatList[6] == SyllableWeights.HEAVY:
            self.feet[0] = Feet.DACTYLUS
            self.feet[1] = Feet.DACTYLUS
        if self.flatList[5] == SyllableWeights.HEAVY or self.flatList[6] == SyllableWeights.LIGHT:
            self.feet[1] = Feet.DACTYLUS
            self.feet[2] = Feet.DACTYLUS
        dactyls = 0
        for i in range (0, 4):
            if self.feet[i] == Feet.DACTYLUS:
                dactyls += 1
        if dactyls == 3:
            self.fillOtherFeet(Feet.DACTYLUS, Feet.SPONDAEUS)
        else:
            raise HexameterException("cannot determine full foot structure of single spondaeus verse")


class BalancedHexameter(Hexameter):
    def __init__(self, text):
        super(BalancedHexameter, self).__init__(text)
    def scanForReal(self):
        if len(self.flatList) != self.max_syllables - 2:
            """ avoid wrong use """
            raise HexameterException("a verse of {0} syllables cannot be balanced in foot 1-4".format(len(self.flatList)))
        if self.flatList[3] == SyllableWeights.HEAVY and self.flatList[5] == SyllableWeights.HEAVY and self.flatList[7] == SyllableWeights.HEAVY:
            self.feet[0] = Feet.DACTYLUS
            self.feet[1] = Feet.SPONDAEUS
            self.feet[2] = Feet.SPONDAEUS
            self.feet[3] = Feet.DACTYLUS
            return
        if self.flatList[1] == SyllableWeights.HEAVY or self.flatList[2] == SyllableWeights.HEAVY:
            self.feet[0] = Feet.SPONDAEUS
        elif self.flatList[1] == SyllableWeights.LIGHT or self.flatList[2] == SyllableWeights.LIGHT:
            self.feet[0] = Feet.DACTYLUS
        if self.flatList[3] == SyllableWeights.LIGHT:
            self.feet[0] = Feet.SPONDAEUS
            self.feet[1] = Feet.DACTYLUS
        if self.flatList[4] == SyllableWeights.LIGHT:
            self.feet[1] = Feet.DACTYLUS
        elif self.flatList[4] == SyllableWeights.HEAVY:
            self.feet[1] = Feet.SPONDAEUS
        if self.flatList[6] == SyllableWeights.LIGHT:
            self.feet[2] = Feet.DACTYLUS
        elif self.flatList[6] == SyllableWeights.HEAVY:
            self.feet[2] = Feet.SPONDAEUS
        if self.flatList[7] == SyllableWeights.LIGHT:
            self.feet[2] = Feet.DACTYLUS
            self.feet[3] = Feet.SPONDAEUS
        if self.flatList[8] == SyllableWeights.HEAVY or self.flatList[9] == SyllableWeights.HEAVY:
            self.feet[3] = Feet.SPONDAEUS
        elif self.flatList[8] == SyllableWeights.LIGHT or self.flatList[9] == SyllableWeights.LIGHT:
            self.feet[3] = Feet.DACTYLUS
            
        if self.calculate():
            return
        elif (self.flatList[3] == SyllableWeights.HEAVY and self.flatList[5] == SyllableWeights.HEAVY and self.flatList[7] == SyllableWeights.HEAVY):
            self.feet[0] = Feet.DACTYLUS
            self.feet[1] = Feet.SPONDAEUS
            self.feet[2] = Feet.SPONDAEUS
            self.feet[3] = Feet.DACTYLUS
        elif ((self.feet[0] == Feet.SPONDAEUS or self.feet[1] == Feet.SPONDAEUS or
                self.feet[2] == Feet.DACTYLUS or self.feet[3] == Feet.DACTYLUS) and
               self.flatList[5] == SyllableWeights.LIGHT):
            self.feet[0] = Feet.SPONDAEUS
            self.feet[1] = Feet.SPONDAEUS
            self.feet[2] = Feet.DACTYLUS
            self.feet[3] = Feet.DACTYLUS
     
        elif ((self.feet[0] == Feet.DACTYLUS or self.feet[1] == Feet.DACTYLUS or
                self.feet[2] == Feet.SPONDAEUS or self.feet[3] == Feet.SPONDAEUS)
               and self.flatList[5] == SyllableWeights.LIGHT):
            self.feet[0] = Feet.DACTYLUS
            self.feet[1] = Feet.DACTYLUS
            self.feet[2] = Feet.SPONDAEUS
            self.feet[3] = Feet.SPONDAEUS

        elif self.spondees == 1 and self.dactyls == 1:
            # sdxx, dsxx
            if (self.flatList[3] == SyllableWeights.HEAVY):
                self.feet[0] = Feet.DACTYLUS
                self.feet[1] = Feet.SPONDAEUS
    
            # xxsd,    xxds
            elif (self.feet[0] == Feet.SPONDAEUS and self.feet[2] == Feet.DACTYLUS):
                if (self.flatList[3] == SyllableWeights.HEAVY or self.flatList[7] == SyllableWeights.HEAVY):
                    self.feet[1] = Feet.SPONDAEUS
                    self.feet[3] = Feet.DACTYLUS
    
                elif (self.flatList[5] == SyllableWeights.HEAVY):
                    self.feet[1] = Feet.DACTYLUS
                    self.feet[3] = Feet.SPONDAEUS
    
                # sxdx
            elif (self.feet[0] == Feet.SPONDAEUS and self.feet[3] == Feet.DACTYLUS):
                if (self.flatList[3] == SyllableWeights.HEAVY):
                    self.feet[1] = Feet.SPONDAEUS
                    self.feet[2] = Feet.DACTYLUS
    
                elif (self.flatList[5] == SyllableWeights.HEAVY):
                    self.feet[1] = Feet.DACTYLUS
                    self.feet[2] = Feet.SPONDAEUS
    
                # sxxd
            elif (self.feet[1] == Feet.SPONDAEUS and self.feet[2] == Feet.DACTYLUS):
                if (self.flatList[7] == SyllableWeights.HEAVY):
                    self.feet[0] = Feet.SPONDAEUS
                    self.feet[3] = Feet.DACTYLUS
    
                elif (self.flatList[5] == SyllableWeights.HEAVY):
                    self.feet[0] = Feet.DACTYLUS
                    self.feet[3] = Feet.SPONDAEUS
    
                # xsdx
            elif (self.feet[1] == Feet.SPONDAEUS and self.feet[3] == Feet.DACTYLUS):
                if (self.flatList[5] == SyllableWeights.HEAVY):
                    self.feet[0] = Feet.DACTYLUS
                    self.feet[2] = Feet.SPONDAEUS
    
                # xsxd
            elif (self.feet[0] == Feet.DACTYLUS and self.feet[2] == Feet.SPONDAEUS):
                if (self.flatList[5] == SyllableWeights.HEAVY):
                    self.feet[1] = Feet.SPONDAEUS
                    self.feet[3] = Feet.DACTYLUS
    
                # dxsx
            elif (self.feet[0] == Feet.DACTYLUS and self.feet[3] == Feet.SPONDAEUS):
                if (self.flatList[7] == SyllableWeights.HEAVY):
                    self.feet[1] = Feet.DACTYLUS
                    self.feet[2] = Feet.SPONDAEUS
    
                elif (self.flatList[5] == SyllableWeights.HEAVY):
                    self.feet[1] = Feet.SPONDAEUS
                    self.feet[2] = Feet.DACTYLUS
    
                # dxxs
            elif (self.feet[1] == Feet.DACTYLUS and self.feet[2] == Feet.SPONDAEUS):
                if (self.flatList[3] == SyllableWeights.HEAVY):
                    self.feet[0] = Feet.DACTYLUS
                    self.feet[3] = Feet.SPONDAEUS
    
                elif (self.flatList[5] == SyllableWeights.HEAVY):
                    self.feet[0] = Feet.SPONDAEUS
                    self.feet[3] = Feet.DACTYLUS
    
                # xdsx
            elif (self.feet[1] == Feet.DACTYLUS and self.feet[3] == Feet.SPONDAEUS):
                if (self.flatList[3] == SyllableWeights.HEAVY or self.flatList[7] == SyllableWeights.HEAVY):
                    self.feet[0] = Feet.DACTYLUS
                    self.feet[2] = Feet.SPONDAEUS
    
                elif (self.flatList[5] == SyllableWeights.HEAVY):
                    self.feet[0] = Feet.SPONDAEUS
                    self.feet[2] = Feet.DACTYLUS
    
                # xdxs
        elif (self.dactyls+self.spondees == 1):
            if ((self.feet[0] == Feet.SPONDAEUS and self.flatList[3] == SyllableWeights.HEAVY) or
                (self.feet[2] == Feet.DACTYLUS and self.flatList[7] == SyllableWeights.HEAVY)):
                self.feet[0] = Feet.SPONDAEUS
                self.feet[1] = Feet.SPONDAEUS
                self.feet[2] = Feet.DACTYLUS
                self.feet[3] = Feet.DACTYLUS

            elif ((self.feet[1] == Feet.DACTYLUS and self.flatList[3] == SyllableWeights.HEAVY) or
                  (self.feet[3] == Feet.SPONDAEUS and self.flatList[7] == SyllableWeights.HEAVY)):
                self.feet[0] = Feet.DACTYLUS
                self.feet[1] = Feet.DACTYLUS
                self.feet[2] = Feet.SPONDAEUS
                self.feet[3] = Feet.SPONDAEUS

            elif (self.flatList[5] == SyllableWeights.HEAVY):
                if ((self.feet[2] == Feet.DACTYLUS or self.feet[3] == Feet.SPONDAEUS) and self.flatList[3] == SyllableWeights.HEAVY):
                    self.feet[0] = Feet.DACTYLUS
                    self.feet[1] = Feet.SPONDAEUS
                    self.feet[2] = Feet.DACTYLUS
                    self.feet[3] = Feet.SPONDAEUS
    
                elif ((self.feet[0] == Feet.SPONDAEUS or self.feet[1] == Feet.DACTYLUS) and self.flatList[5] == SyllableWeights.HEAVY):
                    self.feet[0] = Feet.SPONDAEUS
                    self.feet[1] = Feet.DACTYLUS
                    self.feet[2] = Feet.SPONDAEUS
                    self.feet[3] = Feet.DACTYLUS
    
                elif (((self.feet[2] == Feet.SPONDAEUS or self.feet[3] == Feet.DACTYLUS) and self.flatList[3] == SyllableWeights.HEAVY) or
                      ((self.feet[0] == Feet.DACTYLUS or self.feet[1] == Feet.SPONDAEUS) and self.flatList[7] == SyllableWeights.HEAVY)):
                    self.feet[0] = Feet.DACTYLUS
                    self.feet[1] = Feet.SPONDAEUS
                    self.feet[2] = Feet.SPONDAEUS
                    self.feet[3] = Feet.DACTYLUS
        self.calculate()

    def calculate(self):
        self.dactyls = 0
        self.spondees = 0
        for i in range (0, 4):
            if self.feet[i] == Feet.SPONDAEUS:
                self.spondees += 1
            if self.feet[i] == Feet.DACTYLUS:
                self.dactyls += 1
        if self.spondees > 2 or self.dactyls > 2:
            raise HexameterException("{0} spondaei and {1} dactyli in balanced verse".format(self.spondees, self.dactyls))
        if self.spondees == 2 and self.dactyls == 2:
            return True
        if self.spondees == 2:
            self.fillOtherFeet(Feet.SPONDAEUS, Feet.DACTYLUS)
            return True
        if self.dactyls == 2:
            self.fillOtherFeet(Feet.DACTYLUS, Feet.SPONDAEUS)
            return True

