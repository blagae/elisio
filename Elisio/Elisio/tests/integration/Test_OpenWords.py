import unittest
from open_words.parse import Parser


class TestOpenWords(unittest.TestCase):

    def test_basic_itr(self):
        parse = Parser()
        print(parse.parse("volvit"))
