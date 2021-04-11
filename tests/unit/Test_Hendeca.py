import unittest
from copy import deepcopy

from elisio.exceptions import VerseCreatorException
from elisio.parser.hendeca import (AlcaicHendeca, HendecaCreator,
                                   HendecaException, PhalaecianHendeca,
                                   SapphicHendeca)
from elisio.syllable import Weight


def get_subtype(lst):
    hen_creator = HendecaCreator(lst)
    return hen_creator.get_subtype()


def parse(lst):
    hen_class = get_subtype(lst)
    hen_obj = hen_class('')
    hen_obj.flat_list = lst
    hen_obj.parse()
    return hen_obj.flat_list


class TestHendecaCreator(unittest.TestCase):
    def test_hen_create_edgecase_empty(self):
        sylls = []
        with self.assertRaises(VerseCreatorException):
            get_subtype(sylls)

    def test_hen_create_toomany(self):
        sylls = [Weight.ANCEPS] * 12
        with self.assertRaises(VerseCreatorException):
            get_subtype(sylls)

    def test_hen_create_toofew(self):
        sylls = [Weight.ANCEPS] * 10
        with self.assertRaises(VerseCreatorException):
            get_subtype(sylls)

    def test_hen_create_noinfo(self):
        sylls = [Weight.ANCEPS] * 11
        with self.assertRaises(VerseCreatorException):
            get_subtype(sylls)

    def test_hen_create_pha_easy(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[10] = Weight.LIGHT
        self.assertEqual(get_subtype(sylls), PhalaecianHendeca)

    def test_hen_create_sap_easy(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[5] = Weight.LIGHT
        self.assertEqual(get_subtype(sylls), SapphicHendeca)

    def test_hen_create_alc_easy_1(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[2] = Weight.LIGHT
        self.assertEqual(get_subtype(sylls), AlcaicHendeca)

    def test_hen_create_alc_easy_2(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[7] = Weight.LIGHT
        self.assertEqual(get_subtype(sylls), AlcaicHendeca)

    def test_hen_create_alc_easy_3(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[8] = Weight.HEAVY
        self.assertEqual(get_subtype(sylls), AlcaicHendeca)

    def test_hen_create_alc_easy_4(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[9] = Weight.LIGHT
        self.assertEqual(get_subtype(sylls), AlcaicHendeca)

    def test_hen_create_sap_hard_1a(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[3] = Weight.HEAVY
        sylls[1] = Weight.LIGHT
        self.assertEqual(get_subtype(sylls), SapphicHendeca)

    def test_hen_create_sap_hard_2a(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[3] = Weight.HEAVY
        sylls[2] = Weight.HEAVY
        self.assertEqual(get_subtype(sylls), SapphicHendeca)

    def test_hen_create_sap_hard_3a(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[3] = Weight.HEAVY
        sylls[7] = Weight.HEAVY
        self.assertEqual(get_subtype(sylls), SapphicHendeca)

    def test_hen_create_sap_hard_4a(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[3] = Weight.HEAVY
        sylls[8] = Weight.LIGHT
        self.assertEqual(get_subtype(sylls), SapphicHendeca)

    def test_hen_create_sap_hard_5a(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[3] = Weight.HEAVY
        sylls[9] = Weight.HEAVY
        self.assertEqual(get_subtype(sylls), SapphicHendeca)

    def test_hen_create_sap_hard_1b(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[4] = Weight.HEAVY
        sylls[1] = Weight.LIGHT
        self.assertEqual(get_subtype(sylls), SapphicHendeca)

    def test_hen_create_sap_hard_2b(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[4] = Weight.HEAVY
        sylls[2] = Weight.HEAVY
        self.assertEqual(get_subtype(sylls), SapphicHendeca)

    def test_hen_create_sap_hard_3b(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[3] = Weight.LIGHT
        sylls[4] = Weight.HEAVY
        self.assertEqual(get_subtype(sylls), SapphicHendeca)

    def test_hen_create_sap_hard_4b(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[4] = Weight.HEAVY
        sylls[7] = Weight.HEAVY
        self.assertEqual(get_subtype(sylls), SapphicHendeca)

    def test_hen_create_sap_hard_5b(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[4] = Weight.HEAVY
        sylls[8] = Weight.LIGHT
        self.assertEqual(get_subtype(sylls), SapphicHendeca)

    def test_hen_create_sap_hard_6(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[3] = Weight.HEAVY
        sylls[9] = Weight.HEAVY
        self.assertEqual(get_subtype(sylls), SapphicHendeca)

    def test_hen_create_pha_hard_1a(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[0] = Weight.LIGHT
        sylls[1] = Weight.LIGHT
        self.assertEqual(get_subtype(sylls), PhalaecianHendeca)

    def test_hen_create_pha_hard_2a(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[0] = Weight.LIGHT
        sylls[2] = Weight.HEAVY
        self.assertEqual(get_subtype(sylls), PhalaecianHendeca)

    def test_hen_create_pha_hard_3a(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[0] = Weight.LIGHT
        sylls[3] = Weight.LIGHT
        self.assertEqual(get_subtype(sylls), PhalaecianHendeca)

    def test_hen_create_pha_hard_4a(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[0] = Weight.LIGHT
        sylls[7] = Weight.HEAVY
        self.assertEqual(get_subtype(sylls), PhalaecianHendeca)

    def test_hen_create_pha_hard_5a(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[0] = Weight.LIGHT
        sylls[8] = Weight.LIGHT
        self.assertEqual(get_subtype(sylls), PhalaecianHendeca)

    def test_hen_create_pha_hard_6a(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[0] = Weight.LIGHT
        sylls[9] = Weight.HEAVY
        self.assertEqual(get_subtype(sylls), PhalaecianHendeca)

    def test_hen_create_pha_hard_1b(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[4] = Weight.LIGHT
        sylls[1] = Weight.LIGHT
        self.assertEqual(get_subtype(sylls), PhalaecianHendeca)

    def test_hen_create_pha_hard_2b(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[4] = Weight.LIGHT
        sylls[2] = Weight.HEAVY
        self.assertEqual(get_subtype(sylls), PhalaecianHendeca)

    def test_hen_create_pha_hard_3b(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[4] = Weight.LIGHT
        sylls[3] = Weight.LIGHT
        self.assertEqual(get_subtype(sylls), PhalaecianHendeca)

    def test_hen_create_pha_hard_4b(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[4] = Weight.LIGHT
        sylls[7] = Weight.HEAVY
        self.assertEqual(get_subtype(sylls), PhalaecianHendeca)

    def test_hen_create_pha_hard_5b(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[4] = Weight.LIGHT
        sylls[8] = Weight.LIGHT
        self.assertEqual(get_subtype(sylls), PhalaecianHendeca)

    def test_hen_create_pha_hard_6b(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[4] = Weight.LIGHT
        sylls[9] = Weight.HEAVY
        self.assertEqual(get_subtype(sylls), PhalaecianHendeca)

    def test_hen_create_pha_hard_1c(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[5] = Weight.HEAVY
        sylls[1] = Weight.LIGHT
        self.assertEqual(get_subtype(sylls), PhalaecianHendeca)

    def test_hen_create_pha_hard_2c(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[5] = Weight.HEAVY
        sylls[2] = Weight.HEAVY
        self.assertEqual(get_subtype(sylls), PhalaecianHendeca)

    def test_hen_create_pha_hard_3c(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[5] = Weight.HEAVY
        sylls[3] = Weight.LIGHT
        self.assertEqual(get_subtype(sylls), PhalaecianHendeca)

    def test_hen_create_pha_hard_4c(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[5] = Weight.HEAVY
        sylls[7] = Weight.HEAVY
        self.assertEqual(get_subtype(sylls), PhalaecianHendeca)

    def test_hen_create_pha_hard_5c(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[5] = Weight.HEAVY
        sylls[8] = Weight.LIGHT
        self.assertEqual(get_subtype(sylls), PhalaecianHendeca)

    def test_hen_create_pha_hard_6c(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[5] = Weight.HEAVY
        sylls[9] = Weight.HEAVY
        self.assertEqual(get_subtype(sylls), PhalaecianHendeca)

    def test_hen_create_alc_hard_1(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[3] = Weight.HEAVY
        sylls[0] = Weight.LIGHT
        self.assertEqual(get_subtype(sylls), AlcaicHendeca)

    def test_hen_create_alc_hard_2(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[3] = Weight.HEAVY
        sylls[4] = Weight.LIGHT
        self.assertEqual(get_subtype(sylls), AlcaicHendeca)

    def test_hen_create_alc_hard_3(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[3] = Weight.HEAVY
        sylls[5] = Weight.HEAVY
        self.assertEqual(get_subtype(sylls), AlcaicHendeca)

    def test_hen_create_alc_hard_4(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[4] = Weight.HEAVY
        sylls[0] = Weight.LIGHT
        self.assertEqual(get_subtype(sylls), AlcaicHendeca)

    def test_hen_create_alc_hard_5(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[4] = Weight.HEAVY
        sylls[5] = Weight.HEAVY
        self.assertEqual(get_subtype(sylls), AlcaicHendeca)

    def test_hen_create_ambiguous_fail(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[4] = Weight.HEAVY
        with self.assertRaises(VerseCreatorException):
            get_subtype(sylls)

    def test_hen_create_conflicting_fail(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[2] = Weight.HEAVY
        sylls[3] = Weight.HEAVY
        sylls[5] = Weight.HEAVY
        with self.assertRaises(VerseCreatorException):
            get_subtype(sylls)


class TestAlcaicHendecaParser(unittest.TestCase):

    # always deepcopy these to preserve atomicity of unit tests
    default = [Weight.ANCEPS, Weight.HEAVY, Weight.LIGHT, Weight.HEAVY, Weight.ANCEPS, Weight.HEAVY,
               Weight.LIGHT, Weight.LIGHT, Weight.HEAVY, Weight.LIGHT, Weight.HEAVY]

    def test_hen_alc_parse_easy(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[2] = Weight.LIGHT
        comp = deepcopy(TestAlcaicHendecaParser.default)
        self.assertEqual(parse(sylls), comp)

    def test_hen_alc_parse_easy_subs(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[0] = Weight.HEAVY
        sylls[2] = Weight.LIGHT
        comp = deepcopy(TestAlcaicHendecaParser.default)
        comp[0] = Weight.HEAVY
        self.assertEqual(parse(sylls), comp)

    def test_hen_alc_parse_easy_conflict_light(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[1] = Weight.LIGHT
        sylls[2] = Weight.LIGHT
        with self.assertRaises(HendecaException):
            parse(sylls)

    def test_hen_alc_parse_easy_conflict_heavy(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[2] = Weight.LIGHT
        sylls[6] = Weight.HEAVY
        with self.assertRaises(HendecaException):
            parse(sylls)


class TestPhalaecianHendecaParser(unittest.TestCase):

    # always deepcopy these to preserve atomicity of unit tests
    default = [Weight.ANCEPS, Weight.ANCEPS, Weight.HEAVY, Weight.LIGHT, Weight.LIGHT, Weight.HEAVY,
               Weight.LIGHT, Weight.HEAVY, Weight.LIGHT, Weight.HEAVY, Weight.ANCEPS]

    def test_hen_pha_parse_easy(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[10] = Weight.LIGHT
        comp = deepcopy(TestPhalaecianHendecaParser.default)
        comp[10] = Weight.LIGHT
        self.assertEqual(parse(sylls), comp)

    def test_hen_pha_parse_easy_subs(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[1] = Weight.HEAVY
        sylls[10] = Weight.LIGHT
        comp = deepcopy(TestPhalaecianHendecaParser.default)
        comp[1] = Weight.HEAVY
        comp[10] = Weight.LIGHT
        self.assertEqual(parse(sylls), comp)

    def test_hen_pha_parse_easy_start_1(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[1] = Weight.LIGHT
        sylls[10] = Weight.LIGHT
        comp = deepcopy(TestPhalaecianHendecaParser.default)
        comp[0] = Weight.HEAVY
        comp[1] = Weight.LIGHT
        comp[10] = Weight.LIGHT
        self.assertEqual(parse(sylls), comp)

    def test_hen_pha_parse_easy_start_2(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[0] = Weight.LIGHT
        sylls[10] = Weight.LIGHT
        comp = deepcopy(TestPhalaecianHendecaParser.default)
        comp[0] = Weight.LIGHT
        comp[1] = Weight.HEAVY
        comp[10] = Weight.LIGHT
        self.assertEqual(parse(sylls), comp)

    def test_hen_pha_parse_easy_conflict_light(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[2] = Weight.LIGHT
        sylls[10] = Weight.LIGHT
        with self.assertRaises(HendecaException):
            parse(sylls)

    def test_hen_pha_parse_easy_conflict_heavy(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[3] = Weight.HEAVY
        sylls[10] = Weight.LIGHT
        with self.assertRaises(HendecaException):
            parse(sylls)

    def test_hen_pha_parse_easy_conflict_start(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[0] = Weight.LIGHT
        sylls[1] = Weight.LIGHT
        sylls[10] = Weight.LIGHT
        with self.assertRaises(HendecaException):
            parse(sylls)


class TestSapphicHendecaParser(unittest.TestCase):

    # always deepcopy these to preserve atomicity of unit tests
    default = [Weight.HEAVY, Weight.ANCEPS, Weight.HEAVY, Weight.ANCEPS, Weight.HEAVY, Weight.LIGHT,
               Weight.LIGHT, Weight.HEAVY, Weight.LIGHT, Weight.HEAVY, Weight.HEAVY]

    def test_hen_sap_parse_easy(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[5] = Weight.LIGHT
        comp = deepcopy(TestSapphicHendecaParser.default)
        self.assertEqual(parse(sylls), comp)

    def test_hen_sap_parse_easy_subs(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[3] = Weight.HEAVY
        sylls[5] = Weight.LIGHT
        comp = deepcopy(TestSapphicHendecaParser.default)
        comp[3] = Weight.HEAVY
        self.assertEqual(parse(sylls), comp)

    def test_hen_sap_parse_easy_conflict_light(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[2] = Weight.LIGHT
        sylls[5] = Weight.LIGHT
        with self.assertRaises(HendecaException):
            parse(sylls)

    def test_hen_sap_parse_easy_conflict_heavy(self):
        sylls = [Weight.ANCEPS] * 11
        sylls[5] = Weight.LIGHT
        sylls[6] = Weight.HEAVY
        with self.assertRaises(HendecaException):
            parse(sylls)
