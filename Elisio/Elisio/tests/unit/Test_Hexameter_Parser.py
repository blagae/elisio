import unittest

from Elisio.engine.Syllable import Weight
from Elisio.engine.Verse import Foot
from Elisio.engine.exceptions import HexameterException, HexameterCreatorException, VerseException
from Elisio.engine.verse.Hexameter import HexameterCreator, SpondaicHexameter, SpondaicDominantHexameter, \
    DactylicDominantHexameter, DactylicHexameter, BalancedHexameter


def get_subtype(lst):
    hex_creator = HexameterCreator(lst)
    return hex_creator.get_subtype()


def parse(lst):
    hex_class = get_subtype(lst)
    hex_obj = hex_class('')
    hex_obj.flat_list = lst
    hex_obj.parse()
    return hex_obj.feet


class TestHexameterCreator(unittest.TestCase):

    def test_hex_create_edgecase_empty(self):
        sylls = []
        with self.assertRaises(HexameterCreatorException):
            get_subtype(sylls)

    def test_hex_create_toomany_firstpass(self):
        sylls = [Weight.ANCEPS] * 18
        with self.assertRaises(HexameterCreatorException):
            get_subtype(sylls)

    def test_hex_create_toofew_firstpass(self):
        sylls = [Weight.ANCEPS] * 11
        with self.assertRaises(HexameterCreatorException):
            get_subtype(sylls)

    def test_hex_create_toomany_secondpass(self):
        sylls = [Weight.HEAVY] * 17
        with self.assertRaises(HexameterCreatorException):
            get_subtype(sylls)

    def test_hex_create_toofew_secondpass(self):
        sylls = [Weight.LIGHT] * 12
        sylls[-5] = Weight.HEAVY
        with self.assertRaises(HexameterCreatorException):
            get_subtype(sylls)

    def test_hex_create_toofew_secondpass2(self):
        sylls = [Weight.ANCEPS] * 12
        with self.assertRaises(HexameterCreatorException):
            get_subtype(sylls)

    def test_hex_create_sssss(self):
        sylls = [Weight.HEAVY] * 12
        self.assertEqual(get_subtype(sylls), SpondaicHexameter)

    def test_hex_create_ssssd(self):
        sylls = [Weight.LIGHT] * 13
        sylls[-5] = Weight.HEAVY
        self.assertEqual(get_subtype(sylls), SpondaicHexameter)

    def test_hex_create_ssssd2(self):
        sylls = [Weight.ANCEPS] * 13
        self.assertEqual(get_subtype(sylls), SpondaicHexameter)

    def test_hex_create_sssds(self):
        sylls = [Weight.HEAVY] * 13
        self.assertEqual(get_subtype(sylls), SpondaicDominantHexameter)

    def test_hex_create_sssdd(self):
        sylls = [Weight.LIGHT] * 14
        sylls[-5] = Weight.HEAVY
        self.assertEqual(get_subtype(sylls), SpondaicDominantHexameter)

    def test_hex_create_sssdd2(self):
        sylls = [Weight.ANCEPS] * 14
        self.assertEqual(get_subtype(sylls), SpondaicDominantHexameter)

    def test_hex_create_ssdds(self):
        sylls = [Weight.HEAVY] * 14
        self.assertEqual(get_subtype(sylls), BalancedHexameter)

    def test_hex_create_ssddd(self):
        sylls = [Weight.LIGHT] * 15
        sylls[-5] = Weight.HEAVY
        self.assertEqual(get_subtype(sylls), BalancedHexameter)

    def test_hex_create_ssddd2(self):
        sylls = [Weight.ANCEPS] * 15
        self.assertEqual(get_subtype(sylls), BalancedHexameter)

    def test_hex_create_sddds(self):
        sylls = [Weight.HEAVY] * 15
        self.assertEqual(get_subtype(sylls), DactylicDominantHexameter)

    def test_hex_create_sdddd(self):
        sylls = [Weight.LIGHT] * 16
        sylls[-5] = Weight.HEAVY
        self.assertEqual(get_subtype(sylls), DactylicDominantHexameter)

    def test_hex_create_sdddd2(self):
        sylls = [Weight.ANCEPS] * 16
        self.assertEqual(get_subtype(sylls), DactylicDominantHexameter)

    def test_hex_create_dddds(self):
        sylls = [Weight.HEAVY] * 16
        self.assertEqual(get_subtype(sylls), DactylicHexameter)

    def test_hex_create_ddddd(self):
        sylls = [Weight.LIGHT] * 17
        sylls[-5] = Weight.HEAVY
        self.assertEqual(get_subtype(sylls), DactylicHexameter)

    def test_hex_create_ddddd2(self):
        sylls = [Weight.ANCEPS] * 17
        self.assertEqual(get_subtype(sylls), DactylicHexameter)


class TestHexameterBasicCases(unittest.TestCase):

    def test_hex_parse_notenoughinfo(self):
        sylls = [Weight.ANCEPS] * 14
        with self.assertRaises(HexameterException):
            parse(sylls)

    def test_hex_parse_impossible(self):
        sylls = [Weight.LIGHT] * 15
        with self.assertRaises(VerseException):
            parse(sylls)

    def test_hex_parse_trivial_final_troch(self):
        sylls = [Weight.HEAVY, Weight.LIGHT, Weight.LIGHT,
                 Weight.HEAVY, Weight.LIGHT, Weight.LIGHT,
                 Weight.HEAVY, Weight.LIGHT, Weight.LIGHT,
                 Weight.HEAVY, Weight.LIGHT, Weight.LIGHT,
                 Weight.HEAVY, Weight.LIGHT, Weight.LIGHT,
                 Weight.HEAVY, Weight.LIGHT]
        feet = [Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.TROCHAEUS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_trivial_final_anceps(self):
        sylls = [Weight.HEAVY, Weight.LIGHT, Weight.LIGHT,
                 Weight.HEAVY, Weight.LIGHT, Weight.LIGHT,
                 Weight.HEAVY, Weight.LIGHT, Weight.LIGHT,
                 Weight.HEAVY, Weight.LIGHT, Weight.LIGHT,
                 Weight.HEAVY, Weight.LIGHT, Weight.LIGHT,
                 Weight.HEAVY, Weight.ANCEPS]
        feet = [Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)


class TestDactylicHexameter(unittest.TestCase):

    def test_hex_parse_dactylic_16(self):
        sylls = [Weight.ANCEPS] * 16
        sylls[-3] = Weight.HEAVY
        feet = [Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_dactylic_17(self):
        sylls = [Weight.ANCEPS] * 17
        feet = [Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_dactylic_17_fail_light(self):
        sylls = [Weight.ANCEPS] * 17
        sylls[3] = Weight.LIGHT
        with self.assertRaises(VerseException):
            parse(sylls)

    def test_hex_parse_dactylic_17_fail_heavy(self):
        sylls = [Weight.ANCEPS] * 17
        sylls[2] = Weight.HEAVY
        with self.assertRaises(VerseException):
            parse(sylls)


class TestSpondaicHexameter(unittest.TestCase):

    def test_hex_parse_spondaic_13(self):
        sylls = [Weight.ANCEPS] * 13
        feet = [Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_spondaic_12(self):
        sylls = [Weight.ANCEPS] * 12
        sylls[-4] = Weight.HEAVY
        feet = [Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_spondaic_13_fail_light(self):
        sylls = [Weight.ANCEPS] * 13
        sylls[3] = Weight.LIGHT
        with self.assertRaises(VerseException):
            parse(sylls)


class TestSpondaicDominantHexameter(unittest.TestCase):

    def test_hex_parse_spondaic_dom_light_1a(self):
        sylls = [Weight.ANCEPS] * 14
        sylls[1] = Weight.LIGHT
        feet = [Foot.DACTYLUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_spondaic_dom_light_1b(self):
        sylls = [Weight.ANCEPS] * 14
        sylls[2] = Weight.LIGHT
        feet = [Foot.DACTYLUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_spondaic_dom_light_2a(self):
        sylls = [Weight.ANCEPS] * 14
        sylls[3] = Weight.LIGHT
        feet = [Foot.SPONDAEUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_spondaic_dom_light_2b(self):
        sylls = [Weight.ANCEPS] * 14
        sylls[4] = Weight.LIGHT
        feet = [Foot.SPONDAEUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_spondaic_dom_light_3a(self):
        sylls = [Weight.ANCEPS] * 14
        sylls[5] = Weight.LIGHT
        feet = [Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_spondaic_dom_light_3b(self):
        sylls = [Weight.ANCEPS] * 14
        sylls[6] = Weight.LIGHT
        feet = [Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_spondaic_dom_light_4a(self):
        sylls = [Weight.ANCEPS] * 14
        sylls[7] = Weight.LIGHT
        feet = [Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_spondaic_dom_light_4b(self):
        sylls = [Weight.ANCEPS] * 14
        sylls[8] = Weight.LIGHT
        feet = [Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_spondaic_dom_heavy_1(self):
        sylls = [Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.HEAVY,
                 Weight.HEAVY, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.HEAVY,
                 Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS]
        feet = [Foot.DACTYLUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_spondaic_dom_heavy_2(self):
        sylls = [Weight.ANCEPS, Weight.HEAVY,
                 Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.HEAVY,
                 Weight.HEAVY, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS]
        feet = [Foot.SPONDAEUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_spondaic_dom_heavy_3(self):
        sylls = [Weight.ANCEPS, Weight.HEAVY,
                 Weight.ANCEPS, Weight.ANCEPS,
                 Weight.HEAVY, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.HEAVY,
                 Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS]
        feet = [Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_spondaic_dom_heavy_4(self):
        sylls = [Weight.ANCEPS, Weight.HEAVY,
                 Weight.ANCEPS, Weight.HEAVY,
                 Weight.ANCEPS, Weight.HEAVY,
                 Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS]
        feet = [Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_spondaic_dom_fail_info_1(self):
        sylls = [Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS,
                 Weight.HEAVY, Weight.HEAVY,
                 Weight.HEAVY, Weight.HEAVY,
                 Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS]
        with self.assertRaises(HexameterException):
            # not enough info, we may have dsss or sdss
            parse(sylls)

    def test_hex_parse_spondaic_dom_fail_info_2(self):
        sylls = [Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.HEAVY, Weight.HEAVY,
                 Weight.ANCEPS, Weight.ANCEPS,
                 Weight.HEAVY, Weight.HEAVY,
                 Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS]
        with self.assertRaises(HexameterException):
            # not enough info, we may have dsss or ssds
            parse(sylls)

    def test_hex_parse_spondaic_dom_fail_info_3(self):
        sylls = [Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.HEAVY, Weight.HEAVY,
                 Weight.HEAVY, Weight.HEAVY,
                 Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS]
        with self.assertRaises(HexameterException):
            # not enough info, we may have dsss or sssd
            parse(sylls)

    def test_hex_parse_spondaic_dom_fail_info_4(self):
        sylls = [Weight.ANCEPS, Weight.HEAVY,
                 Weight.HEAVY, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.HEAVY, Weight.HEAVY,
                 Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS]
        with self.assertRaises(HexameterException):
            # not enough info, we may have sdss or ssds
            parse(sylls)

    def test_hex_parse_spondaic_dom_fail_info_5(self):
        sylls = [Weight.ANCEPS, Weight.HEAVY,
                 Weight.HEAVY, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.HEAVY,
                 Weight.HEAVY, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS]
        with self.assertRaises(HexameterException):
            # not enough info, we may have sdss or sssd
            parse(sylls)

    def test_hex_parse_spondaic_dom_fail_info_6(self):
        sylls = [Weight.ANCEPS, Weight.HEAVY,
                 Weight.HEAVY, Weight.HEAVY,
                 Weight.HEAVY, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS, Weight.ANCEPS,
                 Weight.ANCEPS, Weight.ANCEPS]
        with self.assertRaises(HexameterException):
            # not enough info, we may have ssds or sssd
            parse(sylls)


class TestDactylicDominantHexameter(unittest.TestCase):

    def test_hex_parse_dactylic_dom_heavy_1a(self):
        sylls = [Weight.ANCEPS] * 16
        sylls[1] = Weight.HEAVY
        feet = [Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_dactylic_dom_heavy_1b(self):
        sylls = [Weight.ANCEPS] * 16
        sylls[2] = Weight.HEAVY
        feet = [Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_dactylic_dom_heavy_2(self):
        sylls = [Weight.ANCEPS] * 16
        sylls[4] = Weight.HEAVY
        feet = [Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_dactylic_dom_heavy_3a(self):
        sylls = [Weight.ANCEPS] * 16
        sylls[7] = Weight.HEAVY
        feet = [Foot.DACTYLUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_dactylic_dom_heavy_4a(self):
        sylls = [Weight.ANCEPS] * 16
        sylls[9] = Weight.HEAVY
        feet = [Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_dactylic_dom_heavy_4b(self):
        sylls = [Weight.ANCEPS] * 16
        sylls[10] = Weight.HEAVY
        feet = [Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_dactylic_dom_light_1(self):
        sylls = [Weight.ANCEPS] * 16
        sylls[3] = Weight.LIGHT
        feet = [Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_dactylic_dom_light_4(self):
        sylls = [Weight.ANCEPS] * 16
        sylls[8] = Weight.LIGHT
        feet = [Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_dactylic_dom_fallback_1(self):
        sylls = [Weight.ANCEPS] * 16
        sylls[1] = Weight.LIGHT
        sylls[4] = Weight.LIGHT
        sylls[7] = Weight.LIGHT
        feet = [Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_dactylic_dom_fallback_2(self):
        sylls = [Weight.ANCEPS] * 16
        sylls[6] = Weight.HEAVY
        sylls[9] = Weight.LIGHT
        feet = [Foot.DACTYLUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_dactylic_dom_combo_1(self):
        sylls = [Weight.ANCEPS] * 16
        sylls[4] = Weight.LIGHT
        sylls[6] = Weight.LIGHT
        feet = [Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_dactylic_dom_combo_2a(self):
        sylls = [Weight.ANCEPS] * 16
        sylls[4] = Weight.HEAVY
        sylls[6] = Weight.LIGHT
        feet = [Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_dactylic_dom_combo_2b(self):
        sylls = [Weight.ANCEPS] * 16
        sylls[4] = Weight.HEAVY
        sylls[7] = Weight.LIGHT
        feet = [Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_dactylic_dom_combo_2c(self):
        sylls = [Weight.ANCEPS] * 16
        sylls[3] = Weight.HEAVY
        sylls[5] = Weight.HEAVY
        feet = [Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_dactylic_dom_combo_3a(self):
        sylls = [Weight.ANCEPS] * 16
        sylls[5] = Weight.LIGHT
        sylls[7] = Weight.HEAVY
        feet = [Foot.DACTYLUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_dactylic_dom_combo_3b(self):
        sylls = [Weight.ANCEPS] * 16
        sylls[3] = Weight.HEAVY
        sylls[7] = Weight.HEAVY
        feet = [Foot.DACTYLUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_dactylic_dom_combo_3c(self):
        sylls = [Weight.ANCEPS] * 16
        sylls[6] = Weight.HEAVY
        sylls[8] = Weight.HEAVY
        feet = [Foot.DACTYLUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_dactylic_dom_combo_4(self):
        sylls = [Weight.ANCEPS] * 16
        sylls[6] = Weight.HEAVY
        sylls[8] = Weight.LIGHT
        feet = [Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_dactylic_dom_fail_info(self):
        sylls = [Weight.ANCEPS] * 16
        sylls[6] = Weight.HEAVY
        with self.assertRaises(HexameterException):
            parse(sylls)


class TestBalancedHexameter(unittest.TestCase):

    def test_hex_parse_bal_12a(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[1] = Weight.HEAVY
        sylls[3] = Weight.HEAVY
        feet = [Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_12b(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[2] = Weight.HEAVY
        sylls[3] = Weight.HEAVY
        feet = [Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_12c(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[1] = Weight.HEAVY
        sylls[4] = Weight.HEAVY
        feet = [Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_12d(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[2] = Weight.HEAVY
        sylls[4] = Weight.HEAVY
        feet = [Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_12e(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[1] = Weight.HEAVY
        sylls[5] = Weight.LIGHT
        feet = [Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_12f(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[2] = Weight.HEAVY
        sylls[5] = Weight.LIGHT
        feet = [Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_12g(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[5] = Weight.LIGHT
        sylls[6] = Weight.LIGHT
        feet = [Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_12h(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[5] = Weight.LIGHT
        sylls[8] = Weight.LIGHT
        feet = [Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_12i(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[6] = Weight.LIGHT
        sylls[8] = Weight.LIGHT
        feet = [Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_12j(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[5] = Weight.LIGHT
        sylls[9] = Weight.LIGHT
        feet = [Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_12k(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[6] = Weight.LIGHT
        sylls[9] = Weight.LIGHT
        feet = [Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_12l(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[6] = Weight.LIGHT
        sylls[7] = Weight.HEAVY
        feet = [Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_13a(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[1] = Weight.HEAVY
        sylls[6] = Weight.HEAVY
        feet = [Foot.SPONDAEUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_13b(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[2] = Weight.HEAVY
        sylls[6] = Weight.HEAVY
        feet = [Foot.SPONDAEUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_13c(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[3] = Weight.LIGHT
        sylls[6] = Weight.HEAVY
        feet = [Foot.SPONDAEUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_13d(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[3] = Weight.LIGHT
        sylls[8] = Weight.LIGHT
        feet = [Foot.SPONDAEUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_13e(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[3] = Weight.LIGHT
        sylls[9] = Weight.LIGHT
        feet = [Foot.SPONDAEUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_13f(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[4] = Weight.LIGHT
        sylls[8] = Weight.LIGHT
        feet = [Foot.SPONDAEUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_13g(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[4] = Weight.LIGHT
        sylls[9] = Weight.LIGHT
        feet = [Foot.SPONDAEUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_14a(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[1] = Weight.HEAVY
        sylls[7] = Weight.LIGHT
        feet = [Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_14b(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[1] = Weight.HEAVY
        sylls[8] = Weight.HEAVY
        feet = [Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_14c(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[2] = Weight.HEAVY
        sylls[7] = Weight.LIGHT
        feet = [Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_14d(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[2] = Weight.HEAVY
        sylls[8] = Weight.HEAVY
        feet = [Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_14e(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[3] = Weight.LIGHT
        sylls[6] = Weight.LIGHT
        feet = [Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_14f(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[3] = Weight.LIGHT
        sylls[7] = Weight.LIGHT
        feet = [Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_14g(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[4] = Weight.LIGHT
        sylls[6] = Weight.LIGHT
        feet = [Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_14h(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[4] = Weight.LIGHT
        sylls[7] = Weight.LIGHT
        feet = [Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_14i(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[3] = Weight.LIGHT
        sylls[8] = Weight.HEAVY
        feet = [Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_14j(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[3] = Weight.LIGHT
        sylls[9] = Weight.HEAVY
        feet = [Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_23a(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[1] = Weight.LIGHT
        sylls[8] = Weight.LIGHT
        feet = [Foot.DACTYLUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_23b(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[1] = Weight.LIGHT
        sylls[9] = Weight.LIGHT
        feet = [Foot.DACTYLUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_23c(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[2] = Weight.LIGHT
        sylls[8] = Weight.LIGHT
        feet = [Foot.DACTYLUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_23d(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[2] = Weight.LIGHT
        sylls[9] = Weight.LIGHT
        feet = [Foot.DACTYLUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_23e(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[4] = Weight.HEAVY
        sylls[6] = Weight.HEAVY
        feet = [Foot.DACTYLUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_24a(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[1] = Weight.LIGHT
        sylls[6] = Weight.LIGHT
        feet = [Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_24b(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[1] = Weight.LIGHT
        sylls[7] = Weight.LIGHT
        feet = [Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_24c(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[2] = Weight.LIGHT
        sylls[6] = Weight.LIGHT
        feet = [Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_24d(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[2] = Weight.LIGHT
        sylls[7] = Weight.LIGHT
        feet = [Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_24e(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[4] = Weight.HEAVY
        sylls[7] = Weight.LIGHT
        feet = [Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_24f(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[4] = Weight.HEAVY
        sylls[8] = Weight.HEAVY
        feet = [Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_24g(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[4] = Weight.HEAVY
        sylls[9] = Weight.HEAVY
        feet = [Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_34a(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[1] = Weight.LIGHT
        sylls[4] = Weight.LIGHT
        feet = [Foot.DACTYLUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_34b(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[1] = Weight.LIGHT
        sylls[5] = Weight.LIGHT
        feet = [Foot.DACTYLUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_34c(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[2] = Weight.LIGHT
        sylls[4] = Weight.LIGHT
        feet = [Foot.DACTYLUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_34d(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[2] = Weight.LIGHT
        sylls[5] = Weight.LIGHT
        feet = [Foot.DACTYLUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_34e(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[4] = Weight.LIGHT
        sylls[5] = Weight.LIGHT
        feet = [Foot.DACTYLUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_34f(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[5] = Weight.LIGHT
        sylls[6] = Weight.HEAVY
        feet = [Foot.DACTYLUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_34g(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[7] = Weight.HEAVY
        sylls[8] = Weight.HEAVY
        feet = [Foot.DACTYLUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_34h(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[7] = Weight.HEAVY
        sylls[9] = Weight.HEAVY
        feet = [Foot.DACTYLUS, Foot.DACTYLUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_stab(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[3] = Weight.HEAVY
        sylls[5] = Weight.HEAVY
        sylls[7] = Weight.HEAVY
        feet = [Foot.DACTYLUS, Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.DACTYLUS, Foot.DACTYLUS, Foot.BINARY_ANCEPS]
        self.assertEqual(parse(sylls), feet)

    def test_hex_parse_bal_fail_info_1(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[1] = Weight.HEAVY
        sylls[5] = Weight.HEAVY
        with self.assertRaises(VerseException):
            parse(sylls)

    def test_hex_parse_bal_last_resort_1(self):
        sylls = [Weight.ANCEPS] * 15
        sylls[4] = Weight.HEAVY
        sylls[5] = Weight.HEAVY
        with self.assertRaises(VerseException):
            parse(sylls)
