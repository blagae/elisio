import re
import copy
import enum
from Elisio.exceptions import ScansionException, HexameterException

def setDjango():
    import os
    if not 'DJANGO_SETTINGS_MODULE' in os.environ or os.environ['DJANGO_SETTINGS_MODULE'] != 'Elisio.settings':
        os.environ['DJANGO_SETTINGS_MODULE'] = 'Elisio.settings'

vowels = ['a','e','o','y']
semivowels = ['i', 'u', 'j', 'v']
consonants = ['b','c','d','f','g','h','k','l','m','n','p','q','r','s','t']
heavyMakers = ['x','z']
shortEndVowels = ['a','e']
longEndVowels = ['i', 'o', 'u']

class Weights(enum.Enum):
    NONE = 0
    LIGHT = 1
    HEAVY = 2
    ANCEPS = 3

    labels = {
        NONE: 'None',
        LIGHT: 'Light',
        HEAVY: 'Heavy',
        ANCEPS: 'Anceps'
    }

class Feet(enum.Enum):
    DACTYLUS = 0
    SPONDAEUS = 1
    TROCHAEUS = 2
    UNKNOWN = 3

    def getLength(self):
        return len(self.getStructure())

    def getStructure(self):
        if self == Feet.DACTYLUS:
            return [Weights.HEAVY, Weights.LIGHT, Weights.LIGHT]
        elif self == Feet.SPONDAEUS:
            return [Weights.HEAVY, Weights.HEAVY]
        elif self == Feet.TROCHAEUS:
            return [Weights.HEAVY, Weights.LIGHT]
        raise ScansionException

class Verse(object):
    """ Verse class
    A verse is the representation of the Latin text of a verse
    It has no knowledge of its surroundings or context
    """
    text = ""
    words = []
    def __init__(self, text):
        """ construct a Verse by its contents """
        if not isinstance(text, str):
            raise ScansionException
        self.text = text
        self.words = []

    def split(self):
        """ Split a Verse into Words, remembering only the letter characters """
        s = self.text.strip()
        if self.words != []:
            return
        array = re.split('\W+', s)
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

HEXAMETER_MAX_SYLL = 17
HEXAMETER_MIN_SYLL = 12

class Hexameter(Verse):
    max_syllables = HEXAMETER_MAX_SYLL
    min_syllables = HEXAMETER_MIN_SYLL
    feet = []
    flatList = []

    def __init__(self, text):
        super().__init__(text)
        self.feet = [None]*6
        self.flatList = []

    def preparse(self):
        layeredList = self.getSyllableLengths()
        for word in layeredList:
            for weight in word:
                if weight != Weights.NONE:
                    self.flatList.append(weight)

    def scan(self):
        self.preparse()
        if self.flatList[-3] == Weights.HEAVY or self.flatList[-4] == Weights.HEAVY:
            self.feet[4] = Feet.SPONDAEUS
            self.max_syllables -= 1
        else:
            self.feet[4] = Feet.DACTYLUS
            self.min_syllables += 1
        if self.flatList[-1] == Weights.HEAVY:
            self.feet[5] = Feet.SPONDAEUS
        else:
            self.feet[5] = Feet.TROCHAEUS
        if len(self.flatList) == self.min_syllables:
            for i in range (0, 4):
                self.feet[i] = Feet.SPONDAEUS
        elif len(self.flatList) == self.min_syllables + 1:
            self.findOnlyDactylus()
        elif len(self.flatList) == self.max_syllables - 2:
            self.findSickAlgorithm()
        elif len(self.flatList) == self.max_syllables - 1:
            self.findOnlySpondaeus()
        elif len(self.flatList) == self.max_syllables:
            for i in range (0, 4):
                self.feet[i] = Feet.DACTYLUS
        else:
            raise HexameterException
        # control mechanism and syllable filler
        start = 0
        for foot in self.feet:
            if foot is None:
                raise ScansionException
            for count, weight in enumerate(foot.getStructure()):
                if weight != Weights.ANCEPS and self.flatList[count+start] != Weights.ANCEPS and weight != self.flatList[count+start]:
                    raise ScansionException
                self.flatList[count+start] = weight
            start += foot.getLength()

    def findOnlyDactylus(self):
        if len(self.flatList) != self.min_syllables + 1:
            """ avoid wrong use """
            raise HexameterException
        dact = False
        for count, weight in enumerate(self.flatList):
            if count > 0 and count < 9 and weight == Weights.LIGHT:
                self.feet[(count-1)//2] = Feet.DACTYLUS
                dact = True
                break
        if dact:
            self.fillOtherFeet(Feet.DACTYLUS, Feet.SPONDAEUS)
        else:
            heavies = 0
            for count, weight in enumerate(self.flatList):
                if count > 0 and count < 9 and weight == Weights.HEAVY:
                    self.feet[(count-1)//2] = Feet.SPONDAEUS
                    heavies += 1
            if heavies == 3:
                self.fillOtherFeet(Feet.SPONDAEUS, Feet.DACTYLUS)
            else:
                raise HexameterException

    def findOnlySpondaeus(self):
        if len(self.flatList) != self.max_syllables - 1:
            """ avoid wrong use """
            raise HexameterException
        if self.flatList[1] == Weights.HEAVY or self.flatList[2] == Weights.HEAVY or self.flatList[3] == Weights.LIGHT:
            self.feet[0] = Feet.SPONDAEUS
        elif self.flatList[4] == Weights.HEAVY:
            self.feet[1] = Feet.SPONDAEUS
        elif self.flatList[7] == Weights.HEAVY:
            self.feet[2] = Feet.SPONDAEUS
        elif self.flatList[9] == Weights.HEAVY or self.flatList[10] == Weights.HEAVY or self.flatList[8] == Weights.LIGHT:
            self.feet[3] = Feet.SPONDAEUS
        for foot in self.feet:
            if foot == Feet.SPONDAEUS:
                self.fillOtherFeet(Feet.SPONDAEUS, Feet.DACTYLUS)
                return
        dactyls = 0
        if self.flatList[1] == Weights.LIGHT or self.flatList[2] == Weights.LIGHT or self.flatList[3] == Weights.HEAVY:
            self.feet[0] = Feet.DACTYLUS
        if self.flatList[4] == Weights.LIGHT:
            self.feet[1] = Feet.DACTYLUS
        if self.flatList[7] == Weights.LIGHT:
            self.feet[2] = Feet.DACTYLUS
        if self.flatList[9] == Weights.LIGHT or self.flatList[10] == Weights.LIGHT or self.flatList[8] == Weights.HEAVY:
            self.feet[3] = Feet.DACTYLUS
        if self.flatList[5] == Weights.LIGHT or self.flatList[6] == Weights.HEAVY:
            self.feet[0] = Feet.DACTYLUS
            self.feet[1] = Feet.DACTYLUS
        if self.flatList[5] == Weights.HEAVY or self.flatList[6] == Weights.LIGHT:
            self.feet[1] = Feet.DACTYLUS
            self.feet[2] = Feet.DACTYLUS
        for foot in self.feet:
            if foot == Feet.DACTYLUS:
                dactyls += 1
        if dactyls == 3:
            self.fillOtherFeet(Feet.DACTYLUS, Feet.SPONDAEUS)
        else:
            raise HexameterException



    def findSickAlgorithm(self):
        if len(self.flatList) != self.max_syllables - 2:
            """ avoid wrong use """
            raise HexameterException
        if self.flatList[3] == Weights.HEAVY and self.flatList[5] == Weights.HEAVY and self.flatList[7] == Weights.HEAVY:
            self.feet[0] = Feet.DACTYLUS
            self.feet[1] = Feet.SPONDAEUS
            self.feet[2] = Feet.SPONDAEUS
            self.feet[3] = Feet.DACTYLUS
            return
        if self.flatList[1] == Weights.HEAVY or self.flatList[2] == Weights.HEAVY:
            self.feet[0] = Feet.SPONDAEUS
        elif self.flatList[1] == Weights.LIGHT or self.flatList[2] == Weights.LIGHT:
            self.feet[0] = Feet.DACTYLUS
        if self.flatList[3] == Weights.LIGHT:
            self.feet[0] = Feet.SPONDAEUS
            self.feet[1] = Feet.DACTYLUS
        if self.flatList[4] == Weights.LIGHT:
            self.feet[1] = Feet.DACTYLUS
        elif self.flatList[4] == Weights.HEAVY:
            self.feet[1] = Feet.SPONDAEUS
        if self.flatList[6] == Weights.LIGHT:
            self.feet[2] = Feet.DACTYLUS
        elif self.flatList[6] == Weights.HEAVY:
            self.feet[2] = Feet.SPONDAEUS
        if self.flatList[7] == Weights.LIGHT:
            self.feet[2] = Feet.DACTYLUS
            self.feet[3] = Feet.SPONDAEUS
        if self.flatList[8] == Weights.HEAVY or self.flatList[9] == Weights.HEAVY:
            self.feet[3] = Feet.SPONDAEUS
        elif self.flatList[8] == Weights.LIGHT or self.flatList[9] == Weights.LIGHT:
            self.feet[3] = Feet.DACTYLUS
        dactyls = 0
        spondees = 0
        for i in range (0, 4):
            if self.feet[i] == Feet.SPONDAEUS:
                spondees += 1
            if self.feet[i] == Feet.DACTYLUS:
                dactyls += 1
        if spondees > 2 or dactyls > 2:
            raise HexameterException
        if spondees == 2 and dactyls == 2:
            return
        if spondees == 2:
            self.fillOtherFeet(Feet.SPONDAEUS, Feet.DACTYLUS)
        elif dactyls == 2:
            self.fillOtherFeet(Feet.DACTYLUS, Feet.SPONDAEUS)
            
        elif (self.flatList[3] == Weights.HEAVY and self.flatList[5] == Weights.HEAVY and self.flatList[7] == Weights.HEAVY):
            self.feet[0] = Feet.DACTYLUS
            self.feet[1] = Feet.SPONDAEUS
            self.feet[2] = Feet.SPONDAEUS
            self.feet[3] = Feet.DACTYLUS
        elif ((self.feet[0] == Feet.SPONDAEUS or self.feet[1] == Feet.SPONDAEUS or
                self.feet[2] == Feet.DACTYLUS or self.feet[3] == Feet.DACTYLUS) and
               self.flatList[5] == Weights.LIGHT):
            self.feet[0] = Feet.SPONDAEUS
            self.feet[1] = Feet.SPONDAEUS
            self.feet[2] = Feet.DACTYLUS
            self.feet[3] = Feet.DACTYLUS
     
        elif ((self.feet[0] == Feet.DACTYLUS or self.feet[1] == Feet.DACTYLUS or
                self.feet[2] == Feet.SPONDAEUS or self.feet[3] == Feet.SPONDAEUS)
               and self.flatList[5] == Weights.LIGHT):
            self.feet[0] = Feet.DACTYLUS
            self.feet[1] = Feet.DACTYLUS
            self.feet[2] = Feet.SPONDAEUS
            self.feet[3] = Feet.SPONDAEUS

        elif spondees == 1 and dactyls == 1:
            # sdxx, dsxx
            if (self.flatList[3] == Weights.HEAVY):
                self.feet[0] = Feet.DACTYLUS
                self.feet[1] = Feet.SPONDAEUS
    
            # xxsd,    xxds
            elif (self.feet[0] == Feet.SPONDAEUS and self.feet[2] == Feet.DACTYLUS):
                if (self.flatList[3] == Weights.HEAVY or self.flatList[7] == Weights.HEAVY):
                    self.feet[1] = Feet.SPONDAEUS
                    self.feet[3] = Feet.DACTYLUS
    
                elif (self.flatList[5] == Weights.HEAVY):
                    self.feet[1] = Feet.DACTYLUS
                    self.feet[3] = Feet.SPONDAEUS
    
                # sxdx
            elif (self.feet[0] == Feet.SPONDAEUS and self.feet[3] == Feet.DACTYLUS):
                if (self.flatList[3] == Weights.HEAVY):
                    self.feet[1] = Feet.SPONDAEUS
                    self.feet[2] = Feet.DACTYLUS
    
                elif (self.flatList[5] == Weights.HEAVY):
                    self.feet[1] = Feet.DACTYLUS
                    self.feet[2] = Feet.SPONDAEUS
    
                # sxxd
            elif (self.feet[1] == Feet.SPONDAEUS and self.feet[2] == Feet.DACTYLUS):
                if (self.flatList[7] == Weights.HEAVY):
                    self.feet[0] = Feet.SPONDAEUS
                    self.feet[3] = Feet.DACTYLUS
    
                elif (self.flatList[5] == Weights.HEAVY):
                    self.feet[0] = Feet.DACTYLUS
                    self.feet[3] = Feet.SPONDAEUS
    
                # xsdx
            elif (self.feet[1] == Feet.SPONDAEUS and self.feet[3] == Feet.DACTYLUS):
                if (self.flatList[5] == Weights.HEAVY):
                    self.feet[0] = Feet.DACTYLUS
                    self.feet[2] = Feet.SPONDAEUS
    
                # xsxd
            elif (self.feet[0] == Feet.DACTYLUS and self.feet[2] == Feet.SPONDAEUS):
                if (self.flatList[5] == Weights.HEAVY):
                    self.feet[1] = Feet.SPONDAEUS
                    self.feet[3] = Feet.DACTYLUS
    
                # dxsx
            elif (self.feet[0] == Feet.DACTYLUS and self.feet[3] == Feet.SPONDAEUS):
                if (self.flatList[7] == Weights.HEAVY):
                    self.feet[1] = Feet.DACTYLUS
                    self.feet[2] = Feet.SPONDAEUS
    
                elif (self.flatList[5] == Weights.HEAVY):
                    self.feet[1] = Feet.SPONDAEUS
                    self.feet[2] = Feet.DACTYLUS
    
                # dxxs
            elif (self.feet[1] == Feet.DACTYLUS and self.feet[2] == Feet.SPONDAEUS):
                if (self.flatList[3] == Weights.HEAVY):
                    self.feet[0] = Feet.DACTYLUS
                    self.feet[3] = Feet.SPONDAEUS
    
                elif (self.flatList[5] == Weights.HEAVY):
                    self.feet[0] = Feet.SPONDAEUS
                    self.feet[3] = Feet.DACTYLUS
    
                # xdsx
            elif (self.feet[1] == Feet.DACTYLUS and self.feet[3] == Feet.SPONDAEUS):
                if (self.flatList[3] == Weights.HEAVY or self.flatList[7] == Weights.HEAVY):
                    self.feet[0] = Feet.DACTYLUS
                    self.feet[2] = Feet.SPONDAEUS
    
                elif (self.flatList[5] == Weights.HEAVY):
                    self.feet[0] = Feet.SPONDAEUS
                    self.feet[2] = Feet.DACTYLUS
    
                # xdxs
        elif (dactyls+spondees == 1):
            if ((self.feet[0] == Feet.SPONDAEUS and self.flatList[3] == Weights.HEAVY) or
                (self.feet[2] == Feet.DACTYLUS and self.flatList[7] == Weights.HEAVY)):
                self.feet[0] = Feet.SPONDAEUS
                self.feet[1] = Feet.SPONDAEUS
                self.feet[2] = Feet.DACTYLUS
                self.feet[3] = Feet.DACTYLUS

            elif ((self.feet[1] == Feet.DACTYLUS and self.flatList[3] == Weights.HEAVY) or
                  (self.feet[3] == Feet.SPONDAEUS and self.flatList[7] == Weights.HEAVY)):
                self.feet[0] = Feet.DACTYLUS
                self.feet[1] = Feet.DACTYLUS
                self.feet[2] = Feet.SPONDAEUS
                self.feet[3] = Feet.SPONDAEUS

            elif (self.flatList[5] == Weights.HEAVY):
                if ((self.feet[2] == Feet.DACTYLUS or self.feet[3] == Feet.SPONDAEUS) and self.flatList[3] == Weights.HEAVY):
                    self.feet[0] = Feet.DACTYLUS
                    self.feet[1] = Feet.SPONDAEUS
                    self.feet[2] = Feet.DACTYLUS
                    self.feet[3] = Feet.SPONDAEUS
    
                elif ((self.feet[0] == Feet.SPONDAEUS or self.feet[1] == Feet.DACTYLUS) and self.flatList[5] == Weights.HEAVY):
                    self.feet[0] = Feet.SPONDAEUS
                    self.feet[1] = Feet.DACTYLUS
                    self.feet[2] = Feet.SPONDAEUS
                    self.feet[3] = Feet.DACTYLUS
    
                elif (((self.feet[2] == Feet.SPONDAEUS or self.feet[3] == Feet.DACTYLUS) and self.flatList[3] == Weights.HEAVY) or
                      ((self.feet[0] == Feet.DACTYLUS or self.feet[1] == Feet.SPONDAEUS) and self.flatList[7] == Weights.HEAVY)):
                    self.feet[0] = Feet.DACTYLUS
                    self.feet[1] = Feet.SPONDAEUS
                    self.feet[2] = Feet.SPONDAEUS
                    self.feet[3] = Feet.DACTYLUS


    def fillOtherFeet(self, fromFoot, toFoot):
        for count, foot in enumerate(self.feet):
            if count < 4 and foot != fromFoot:
                self.feet[count] = toFoot


class Word(object):
    """ Word class
    A word is the representation of the Latin word
    It has extensive knowledge of its sounds, which it can join into syllables
    """
    text = ""
    syllables = []
    def __init__(self, text):
        """ construct a Word by its contents """
        self.syllables = []
        if not (isinstance(text, str) and text.isalpha()):
            raise ScansionException
        self.text = text.lower()
        
    def __repr__(self):
        return self.syllables
    def __str__(self):
        return self.syllables

    def split(self):
        """ splits a word into syllables by using a few static methods from the Syllable class """
        if self.splitFromDeviantWord():
            return
        sounds = self.findSounds()
        temporarySyllables = Word.joinIntoSyllables(sounds)
        self.syllables = Word.redistribute(temporarySyllables)
        self.checkConsistency()

    def splitFromDeviantWord(self):
        """ if the word can be found the repository of Deviant Words, we should use that instead """
        from Elisio.models import Deviant_Word
        deviant = Deviant_Word.find(self.text)
        if deviant:
            self.syllables = deviant.getSyllables()
            return True

    def findSounds(self):
        """ find the sequence of sounds from the textual representation of the word """
        return Word.findSoundsForText(self.text)
    
    def __eq__(self, other): 
        """ Words are equal if they have exactly the same characters
        Case insensitivity is enforced by the constructor
        """
        return self.__dict__ == other.__dict__

    def getSyllableStructure(self, nextWord = None):
        """ get the list of syllable weights based on the syllable list """
        ss = []
        if self.syllables == []:
            self.split()
        for count, syllable in enumerate(self.syllables):
            try:
                ss.append(syllable.getWeight(self.syllables[count+1]))
            except IndexError:
                ss.append(syllable.getWeight())
        if nextWord and isinstance(nextWord, Word):
        # new functionality: word contact
            lastSyllable = self.syllables[-1]
            nextWord.split()
            firstSyllable = nextWord.syllables[0]
            if lastSyllable.canElideIfFinal() and firstSyllable.startsWithVowel():
                # elision
                ss[-1] = Weights.NONE
            elif lastSyllable.endsWithConsonant() and firstSyllable.startsWithVowel():
                # consonant de facto redistributed
                ss[-1] = Weights.ANCEPS
            elif lastSyllable.endsWithVowel() and firstSyllable.startsWithConsonantCluster():
                ss[-1] = Weights.HEAVY
        return ss

    def checkConsistency(self):
        for syllable in self.syllables:
            if not syllable.isValid():
                word = Word(syllable.getText())
                word.split()
                index = self.syllables.index(syllable)
                self.syllables.remove(syllable)
                for syll in reversed(word.syllables):
                    self.syllables.insert(index, syll)
    
    @classmethod
    def findSoundsForText(cls, text):
        """ iteratively allocate all text to a sound
        """
        i = 0
        sounds = []
        while i < len(text):
            sound = Sound.createFromText(text[i:i+2])
            i += len(sound.letters)
            sounds.append(sound)
        return sounds

    @classmethod
    def joinIntoSyllables(cls, sounds):
        """ join a list of sounds into a preliminary syllables
        keep adding sounds to the syllable until it becomes illegal or the word ends
        at either point, save the syllable and count e new one
        """
        syllables = []
        currentSyllable = Syllable("", False)
        for sound in sounds:
            try:
                currentSyllable.addSound(sound)
            except ScansionException:
                syllables.append(currentSyllable)
                currentSyllable = Syllable("", False)
                currentSyllable.addSound(sound)
        syllables.append(currentSyllable)
        return syllables

    @classmethod
    def redistribute(cls, syllables):
        """ redistribute the sounds of a list of syllables
        in order to use the correct syllables, not the longest possible
        """
        for count in range(len(syllables)-1):
            if syllables[count].endsWithVowel() and syllables[count+1].startsWithConsonantCluster():
                Word.switchSound(syllables[count], syllables[count+1], True)
            elif syllables[count].endsWithConsonant() and syllables[count+1].startsWithVowel(False):
                # TODO: problem if same letter multiple times in one: 'memo' becomes 'em-mo' instead of 'me-mo'
                Word.switchSound(syllables[count], syllables[count+1], False)
        return syllables

    @classmethod
    def switchSound(cls, syllable1, syllable2, toFirst):
        """ switch sounds from one syllable to another
        if toFirst is True, switch from the second to the first
        if toFirst is False, switch from the first to the second
        """
        if toFirst:
            givenSound = syllable2.sounds[0]
            syllable2.sounds.remove(givenSound)
            syllable1.sounds.append(givenSound)
        else:
            givenSound = syllable1.sounds[-1]
            # TODO: check experiment
            syllable1.sounds.reverse()
            syllable1.sounds.remove(givenSound)
            syllable1.sounds.reverse()
            syllable2.sounds.insert(0, givenSound)

class Syllable(object):
    """ Syllable class
    A syllable knows its sounds and can determine if the specific combination of them is a valid one
    """
    syllable = ""
    sounds = []
    weight = None
    def __init__(self, syllable, test = True, weight = None):
        """ construct a Syllable by its contents """
        self.weight = weight
        self.syllable = syllable
        self.sounds = Word.findSoundsForText(syllable)
        if test and not self.isValid():
            raise ScansionException

    def __eq__(self, other):
        return self.sounds == other.sounds
    
    def __repr__(self):
        return str(self.sounds)

    def getText(self):
        result = ""
        for sound in self.sounds:
            result += sound.getText()
        return result

    def isValid(self):
        """ a syllable is valid if it contains:
            * at most one consonant after the vocalic sound, and
            * a single vowel or semivowel
            * a semivowel and a vowel in that order
        """
        containsFinalConsonant = containsVowel = containsSemivowel = False
        onlyConsonants = True
        for count, sound in enumerate(self.sounds):
            if sound.isConsonant():
                if containsFinalConsonant:
                    return False
                if containsVowel or containsSemivowel:
                    containsFinalConsonant = True
            elif sound.isVowel():
                if containsVowel or (containsFinalConsonant and containsSemivowel):
                    return False
                containsVowel = True
                onlyConsonants = False
            elif sound.isSemivowel():
                if containsVowel or (containsFinalConsonant and containsSemivowel):
                    return False
                if count > 0:
                    containsVowel = True
                containsSemivowel = True
                onlyConsonants = False
        return containsVowel or containsSemivowel or onlyConsonants

    def endsWithConsonant(self):
        """ last sound of the syllable is consonantal """
        return self.sounds[-1].isConsonant()

    def canElideIfFinal(self):
        return (self.endsWithVowel() or
                (self.sounds[-1] == Sound('m') and 
                (self.sounds[-2].isVowel() or self.sounds[-2].isSemivowel()))
               )

    def endsWithVowel(self):
        """ last sound of the syllable is vocalic
        a final semivowel is always vocalic """
        return self.sounds[-1].isVowel() or self.sounds[-1].isSemivowel()
    
    def startsWithVowel(self, initial=True):
        """ first sound of the syllable is vocalic
        an initial semivowel is only vocalic if it is the syllable's only sound
        or if it is followed directly by a consonant
        """
        return (self.sounds[0].isVowel() or
                self.sounds[0].isH() or 
                (self.sounds[0].isSemivowel() and 
                 (not initial or len(self.sounds) == 1 or self.sounds[1].isConsonant()))
               )
    def startsWithConsonant(self):
        """ first sound of the syllable is consonantal 
        an initial semivowel is consonantal if it is followed by a consonant
        """
        return self.sounds[0].isConsonant() or (self.sounds[0].isSemivowel() and len(self.sounds) > 1 and self.sounds[1].isVowel())

    def startsWithConsonantCluster(self):
        """ first sounds of the syllable are all consonants """
        return (self.startsWithConsonant() and
                ((len(self.sounds) > 1 and self.sounds[1].isConsonant()) or
                 self.makesPreviousHeavy()
                )
               )

    def makesPreviousHeavy(self):
        """ first sound of the syllable is one of the double consonant letters """
        return self.sounds[0].isHeavyMaking()

    def getVowel(self):
        """ get the vocalic sound from a syllable """
        semivowel = None
        for sound in reversed(self.sounds):
            if sound.isVowel():
                return sound
            if sound.isSemivowel():
                if semivowel:
                    return semivowel
                semivowel = sound
        if semivowel:
            return semivowel
        raise ScansionException

    def isHeavy(self, nextSyllable = None):
        """ determines whether the syllable is inherently heavy or not
        a syllable is heavy if it ends in a consonant
        or if the next syllable starts with a heavy-making consonant
        or if it contains a final diphthong which isn't shortened by the next syllable (with vocalic start)
        final syllables are long if they are O, U, or I, or a diphthong
        """
        vowel = self.getVowel()
        if nextSyllable and isinstance(nextSyllable, Syllable):
            return ((self.endsWithConsonant() or nextSyllable.makesPreviousHeavy()) or
                    (not self.isLight(nextSyllable) and vowel.isDiphthong()))
        return self.endsWithConsonant() or vowel.isDiphthong() or vowel.letters[0] in longEndVowels

    def isLight(self, nextSyllable = None):
        """ determines whether the syllable is inherently light or not
        a syllable is always light if it is followed by a vowel in the next syllable
        final vowels are usually short if they are A or E
        """
        if nextSyllable and isinstance(nextSyllable, Syllable):
            return self.endsWithVowel() and nextSyllable.startsWithVowel()
        return (self.endsWithVowel() and
                not self.getVowel().isDiphthong() and
                self.getVowel().letters[0] in shortEndVowels
                )

    def addSound(self, sound):
        """ add a sound to a syllable if the syllable stays valid by the addition """
        testSyllable = copy.deepcopy(self)
        testSyllable.sounds.append(sound)
        if testSyllable.isValid():
            self.sounds.append(sound)
        else:
            raise ScansionException

    def getWeight(self, nextSyllable = None):
        """ try to determine the weight of the syllable, in the light of the next syllable
        if this doesn't succeed, assign the weight ANCEPS = undetermined
        """
        if self.weight:
            return self.weight
        if self.isLight(nextSyllable):
            return Weights.LIGHT
        elif self.isHeavy(nextSyllable):
            return Weights.HEAVY
        else:
            return Weights.ANCEPS

    @classmethod
    def createFromDatabase(cls, syll):
        from Elisio.models import Deviant_Syllable
        if not isinstance(syll, Deviant_Syllable):
            raise ScansionException
        result = Syllable(syll.contents, False, syll.weight)
        return result

class Sound(object):
    """ Sound class
    A sound is composed of one or several letters
    """
    letters = []
    def __init__(self, *letters):
        """ construct a Sound from a list of letters, or (a list of) text(s) """
        self.letters = []
        for letter in letters:
            if isinstance(letter, Letter):
                self.letters.append(letter)
            else:
                if isinstance(letter, str) and len(letter) > 1:
                    for let in letter:
                        self.letters.append(Letter(let))
                else:
                    self.letters.append(Letter(letter))
        if not self.isValidSound():
            raise ScansionException

    def getText(self):
        result = ""
        for letter in self.letters:
            result += letter.__str__()
        return result

    def isValidSound(self):
        """ is a given sound a valid sound
        this is determined by the number of letters
        in case that number is 2, it must be one of a fixed list of combinations
        """
        if len(self.letters) < 1 or len(self.letters) > 2:
            raise ScansionException(self.letters)
        elif len(self.letters) == 1:
            return True
        else:
            return self.isValidDoubleSound()

    def isValidDoubleSound(self):
        """ the fixed list of combinations
        * QU
        * muta cum liquida
        * an aspirated voiceless stop
        * a diphthong
        """
        if len(self.letters) < 2:
            return False
        first = self.letters[0]
        second = self.letters[1]
        return ((first == 'q' and second == 'u') or
                self.isMutaCumLiquida() or
               ((first == 't' or first == 'p' or first == 'c' ) and second == 'h') or
               self.isDiphthong())

    def isMutaCumLiquida(self):
        if len(self.letters) < 2:
            return False
        first = self.letters[0]
        second = self.letters[1]
        return ((second == 'r' or second == 'l') and
                (first == 't' or first == 'd' or first == 'p' or first == 'b' or first == 'c' or first == 'g')
               )


    def isDiphthong(self):
        """ the possible diphthongs
        AE AU
        EI EU
        OE
        """
        if len(self.letters) == 1:
            return False
        first = self.letters[0]
        second = self.letters[1]
        return ((first == 'a' and (second == 'e' or second == 'u')) or
                (first == 'e' and second == 'u') or
                (first == 'o' and second == 'e'))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    
    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.letters)

    @classmethod
    def createFromText(cls, text):
        """ try to create a Sound from given text string of maximally 2 syllables
        """
        if len(text) > 2:
            raise ScansionException
        try:
            sound = Sound(text[0:2])
        except ScansionException:
            sound = Sound(text[0])
        return sound
    
    def isVowel(self):
        """ determine whether a sound is unambiguously vocalic """
        return self.isDiphthong() or self.letters[0].isVowel()
    def isSemivowel(self):
        """ it is impossible to determine on the sound level
        whether or not a semivowel is vocalic or consonantal
        therefore we keep the semivowel category separate
        """
        return self.letters[0].isSemivowel()
    def isConsonant(self):
        """ does a sound contain a consonantal letter """
        return self.letters[0].isConsonant()
    def isHeavyMaking(self):
        """ does a sound contain a cluster-forming consonant letter """
        return self.letters[0].isHeavyMaking()
    def isH(self):
        return self.letters[0] == Letter('h')

class Letter(object):
    """ Letter class
    commit 1 (blagae): BLI 10
    reason: creation of stub for interaction with Word
    """
    letter = ""
    def __init__(self, letter):
        """ construct a Letter by its contents """
        if not (len(letter) == 1 and isinstance(letter, str) and letter.isalpha()):
            raise ScansionException
        self.letter = letter.lower()
        if self.letter == 'v':
            self.letter = 'u'
        elif self.letter == 'j':
            self.letter = 'i'
        if not self.isValidLetter():
            raise ScansionException

    def __eq__(self, other): 
        """ Letters are equal if they have exactly the same character
        Case insensitivity is enforced by the constructor
        """
        return self.__str__() == other.__str__()
    
    def __str__(self):
        return self.letter
    def __repr__(self):
        return self.letter

    def isValidLetter(self):
        """ a letter is only valid if it figures in one of the lists of legal characters
        currently the only invalid letter is W
        """
        return (self.isVowel() or self.isSemivowel() or self.isConsonant())
    
    def isVowel(self):
        """ only the non-semivowel vowel letters """
        return self.letter in vowels
    def isSemivowel(self):
        """ specifically non-semivowel letters """
        return self.letter in semivowels
    def isVocalic(self):
        """ all potentially vocalic letters """
        return self.isVowel() or self.isSemivowel()
    def isConsonant(self):
        """ all single consonantal letters """
        return self.letter in consonants or self.isHeavyMaking()
    def isHeavyMaking(self):
        """ the heavymakers """
        return self.letter in heavyMakers