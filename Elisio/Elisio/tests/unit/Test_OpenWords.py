import unittest
from open_words.parse import Parse


class TestOpenWords(unittest.TestCase):
    def test_basic_itr(self):
        parse = Parse()
        print(parse.parse("volvit"))
