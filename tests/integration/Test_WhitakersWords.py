import unittest

from whitakers_words.parser import Parser


class TestWhitakersWords(unittest.TestCase):

    def test_basic_itr(self):
        parse = Parser()
        result = parse.parse("conderet")
        self.assertNotEqual(result, None)
