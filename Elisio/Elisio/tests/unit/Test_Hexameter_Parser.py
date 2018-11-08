import unittest

from Elisio.engine.Syllable import Weight
from Elisio.engine.Verse import Foot
from Elisio.engine.exceptions import HexameterException, HexameterCreatorException
from Elisio.engine.verse.Hexameter import HexameterCreator


class TestParser(unittest.TestCase):
    """ testing specifically for the hexameter """

    @staticmethod
    def __parse(lst):
        hex_creator = HexameterCreator(lst)
        hex_class = hex_creator.get_subtype()
        hex_obj = hex_class('')
        hex_obj.flat_list = lst
        hex_obj.parse()
        return hex_obj.feet

    def test_hex_struct_toomany_firstpass(self):
        sylls = [Weight.ANCEPS] * 18
        with self.assertRaises(HexameterCreatorException):
            self.__parse(sylls)

    def test_hex_struct_toofew_firstpass(self):
        sylls = [Weight.ANCEPS] * 11
        with self.assertRaises(HexameterCreatorException):
            self.__parse(sylls)

    def test_hex_struct_toomany_secondpass(self):
        sylls = [Weight.HEAVY] * 17
        with self.assertRaises(HexameterCreatorException):
            self.__parse(sylls)

    def test_hex_struct_toofew_secondpass(self):
        sylls = [Weight.LIGHT] * 12
        with self.assertRaises(HexameterCreatorException):
            self.__parse(sylls)

    def test_hex_struct_notenoughinfo(self):
        sylls = [Weight.ANCEPS] * 14
        with self.assertRaises(HexameterException):
            self.__parse(sylls) #

    def test_hex_struct_trivial(self):
        sylls = [Weight.HEAVY, Weight.LIGHT, Weight.LIGHT,
                 Weight.HEAVY, Weight.LIGHT, Weight.LIGHT,
                 Weight.HEAVY, Weight.LIGHT, Weight.LIGHT,
                 Weight.HEAVY, Weight.LIGHT, Weight.LIGHT,
                 Weight.HEAVY, Weight.LIGHT, Weight.LIGHT,
                 Weight.HEAVY, Weight.LIGHT]
        feet = [Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.TROCHAEUS]
        self.assertEqual(self.__parse(sylls), feet)

    def test_hex_struct_final_anceps(self):
        sylls = [Weight.HEAVY, Weight.LIGHT, Weight.LIGHT,
                 Weight.HEAVY, Weight.LIGHT, Weight.LIGHT,
                 Weight.HEAVY, Weight.LIGHT, Weight.LIGHT,
                 Weight.HEAVY, Weight.LIGHT, Weight.LIGHT,
                 Weight.HEAVY, Weight.LIGHT, Weight.LIGHT,
                 Weight.HEAVY, Weight.ANCEPS]
        feet = [Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(self.__parse(sylls), feet)

    def test_hex_struct_spondaic_16(self):
        sylls = [Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.HEAVY,
                 Weight.ANCEPS, Weight.ANCEPS]
        feet = [Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.BINARY_ANCEPS]
        self.assertEqual(self.__parse(sylls), feet)

    def test_hex_struct_dactylic_17(self):
        sylls = [Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS]
        feet = [Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(self.__parse(sylls), feet)

    def test_hex_struct_dactylic_13(self):
        sylls = [Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS]
        feet = [Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(self.__parse(sylls), feet)

    def test_hex_struct_spondaic_12(self):
        sylls = [Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS,
                 Weight.HEAVY, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS]
        feet = [Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.BINARY_ANCEPS]
        self.assertEqual(self.__parse(sylls), feet)

    def test_hex_struct_bestclue_14(self):
        sylls = [Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.LIGHT, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS]
        feet = [Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(self.__parse(sylls), feet)

    def test_hex_struct_bestclue2_14(self):
        sylls = [Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.LIGHT, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS]
        feet = [Foot.SPONDAEUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(self.__parse(sylls), feet)

    def test_hex_struct_badclue_14(self):
        sylls = [Weight.ANCEPS, Weight.HEAVY,
                 Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.HEAVY, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.HEAVY,
                 Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS]
        feet = [Foot.SPONDAEUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(self.__parse(sylls), feet)
