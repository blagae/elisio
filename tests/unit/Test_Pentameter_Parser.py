import unittest

from elisio.verse.Pentameter import PentameterCreator, SpondaicPentameter, BalancedPentameter, DactylicPentameter
from elisio.exceptions import VerseCreatorException, PentameterException, VerseException
from elisio.Syllable import Weight
from elisio.verse.Verse import Foot


def get_subtype(lst):
    pent_creator = PentameterCreator(lst)
    return pent_creator.get_subtype()


def parse(lst):
    pent_class = get_subtype(lst)
    pent_obj = pent_class('')
    pent_obj.flat_list = lst
    pent_obj.parse()
    return pent_obj.feet


class TestPentameterCreator(unittest.TestCase):
    def test_pent_create_edgecase_empty(self):
        sylls = []
        with self.assertRaises(VerseCreatorException):
            get_subtype(sylls)

    def test_pent_create_toomany_firstpass(self):
        sylls = [Weight.ANCEPS] * 15
        with self.assertRaises(VerseCreatorException):
            get_subtype(sylls)

    def test_pent_create_toofew_firstpass(self):
        sylls = [Weight.ANCEPS] * 11
        with self.assertRaises(VerseCreatorException):
            get_subtype(sylls)

    def test_pent_create_ss(self):
        sylls = [Weight.ANCEPS] * 12
        self.assertEqual(get_subtype(sylls), SpondaicPentameter)

    def test_pent_create_sd(self):
        sylls = [Weight.ANCEPS] * 13
        self.assertEqual(get_subtype(sylls), BalancedPentameter)

    def test_pent_create_dd(self):
        sylls = [Weight.ANCEPS] * 14
        self.assertEqual(get_subtype(sylls), DactylicPentameter)


class TestDactylicPentameter(unittest.TestCase):
    def test_pent_dact_basic(self):
        sylls = [Weight.ANCEPS] * 14
        feet = [Foot.DACTYLUS, Foot.DACTYLUS, Foot.MACRON, Foot.DACTYLUS, Foot.DACTYLUS, Foot.MACRON]
        self.assertEqual(parse(sylls), feet)

    def test_pent_dact_fail_1a(self):
        sylls = [Weight.ANCEPS] * 14
        sylls[0] = Weight.LIGHT
        with self.assertRaises(PentameterException):
            parse(sylls)

    def test_pent_dact_fail_1b(self):
        sylls = [Weight.ANCEPS] * 14
        sylls[1] = Weight.HEAVY
        with self.assertRaises(PentameterException):
            parse(sylls)

    def test_pent_dact_fail_1c(self):
        sylls = [Weight.ANCEPS] * 14
        sylls[2] = Weight.HEAVY
        with self.assertRaises(PentameterException):
            parse(sylls)

    def test_pent_dact_fail_2a(self):
        sylls = [Weight.ANCEPS] * 14
        sylls[3] = Weight.LIGHT
        with self.assertRaises(PentameterException):
            parse(sylls)

    def test_pent_dact_fail_2b(self):
        sylls = [Weight.ANCEPS] * 14
        sylls[4] = Weight.HEAVY
        with self.assertRaises(PentameterException):
            parse(sylls)

    def test_pent_dact_fail_2c(self):
        sylls = [Weight.ANCEPS] * 14
        sylls[5] = Weight.HEAVY
        with self.assertRaises(PentameterException):
            parse(sylls)


class TestSpondaicPentameter(unittest.TestCase):
    def test_pent_spon_basic(self):
        sylls = [Weight.ANCEPS] * 12
        feet = [Foot.SPONDAEUS, Foot.SPONDAEUS, Foot.MACRON, Foot.DACTYLUS, Foot.DACTYLUS, Foot.MACRON]
        self.assertEqual(parse(sylls), feet)

    def test_pent_spon_fail_1a(self):
        sylls = [Weight.ANCEPS] * 12
        sylls[1] = Weight.LIGHT
        with self.assertRaises(PentameterException):
            parse(sylls)

    def test_pent_spon_fail_1b(self):
        sylls = [Weight.ANCEPS] * 12
        sylls[2] = Weight.LIGHT
        with self.assertRaises(PentameterException):
            parse(sylls)

    def test_pent_spon_fail_2a(self):
        sylls = [Weight.ANCEPS] * 12
        sylls[3] = Weight.LIGHT
        with self.assertRaises(PentameterException):
            parse(sylls)

    def test_pent_spon_fail_2b(self):
        sylls = [Weight.ANCEPS] * 12
        sylls[4] = Weight.LIGHT
        with self.assertRaises(PentameterException):
            parse(sylls)


class TestBalancedPentameter(unittest.TestCase):
    def test_pent_bal_basic_1a(self):
        sylls = [Weight.ANCEPS] * 13
        sylls[1] = Weight.LIGHT
        feet = [Foot.DACTYLUS, Foot.SPONDAEUS, Foot.MACRON, Foot.DACTYLUS, Foot.DACTYLUS, Foot.MACRON]
        self.assertEqual(parse(sylls), feet)

    def test_pent_bal_basic_1b(self):
        sylls = [Weight.ANCEPS] * 13
        sylls[2] = Weight.LIGHT
        feet = [Foot.DACTYLUS, Foot.SPONDAEUS, Foot.MACRON, Foot.DACTYLUS, Foot.DACTYLUS, Foot.MACRON]
        self.assertEqual(parse(sylls), feet)

    def test_pent_bal_basic_1c(self):
        sylls = [Weight.ANCEPS] * 13
        sylls[2] = Weight.HEAVY
        feet = [Foot.SPONDAEUS, Foot.DACTYLUS, Foot.MACRON, Foot.DACTYLUS, Foot.DACTYLUS, Foot.MACRON]
        self.assertEqual(parse(sylls), feet)

    def test_pent_bal_basic_2a(self):
        sylls = [Weight.ANCEPS] * 13
        sylls[3] = Weight.LIGHT
        feet = [Foot.SPONDAEUS, Foot.DACTYLUS, Foot.MACRON, Foot.DACTYLUS, Foot.DACTYLUS, Foot.MACRON]
        self.assertEqual(parse(sylls), feet)

    def test_pent_bal_basic_2b(self):
        sylls = [Weight.ANCEPS] * 13
        sylls[4] = Weight.LIGHT
        feet = [Foot.SPONDAEUS, Foot.DACTYLUS, Foot.MACRON, Foot.DACTYLUS, Foot.DACTYLUS, Foot.MACRON]
        self.assertEqual(parse(sylls), feet)

    def test_pent_bal_fail(self):
        sylls = [Weight.ANCEPS] * 13
        with self.assertRaises(PentameterException):
            parse(sylls)

    def test_pent_bal_fail_2(self):
        sylls = [Weight.ANCEPS] * 13
        sylls[1] = Weight.HEAVY
        sylls[3] = Weight.HEAVY
        with self.assertRaises(VerseException):
            parse(sylls)

    def test_pent_bal_fail_3(self):
        sylls = [Weight.ANCEPS] * 13
        sylls[1] = Weight.LIGHT
        sylls[3] = Weight.LIGHT
        with self.assertRaises(VerseException):
            parse(sylls)
