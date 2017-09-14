import unittest
from Elisio.engine.Verse import Foot
from Elisio.engine.Syllable import Weight
from Elisio.engine.Hexameter import HexameterCreator


class TestHexameter(unittest.TestCase):
    """ testing specifically for the hexameter """

    @staticmethod
    def __parse(lst):
        hex_creator = HexameterCreator(lst)
        hex_class = hex_creator.get_subtype()
        hexa = hex_class('')
        hexa.flat_list = lst
        hexa.parse()
        return hexa.feet

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
