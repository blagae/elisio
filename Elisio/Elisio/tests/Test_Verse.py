import unittest
from Elisio.models import Verse, Word

words = ['Arma', 'virumque', 'cano', 'Troiae', 'qui', 'primus', 'ab', 'oris']
expected_word_list = []
for word in words:
    expected_word_list.append(Word(word))


class Test_Verse(unittest.TestCase):
    """ Test_Verse class
    Unit tests for splitting a verse into words
    commit 1 (blagae): BLI 9
    reason: creation
    """
    def constructVerse(self, text = "Arma virumque cano, Troiae qui primus ab oris"):
        """ Construct a verse object from a given text """
        constructedVerse = Verse(text)
        return constructedVerse

    def test_constructVerse(self):
        """ constructing a Verse must work """
        self.assertTrue(isinstance(self.constructVerse(), Verse))

    def test_eqVerse(self):
        """ Two separate verses are equal if they carry the exact same text """
        verse1 = self.constructVerse()
        verse2 = self.constructVerse()
        verse1.split()
        self.assertEqual(verse1, verse2)

    def test_splitVerse(self):
        """ A normal verse must be split into words correctly """
        verse = self.constructVerse()
        verse.split()
        self.assertEqual(verse.words, expected_word_list)

    def test_punctuationVerse(self):
        """ A verse with unusual and heavy punctuation must be split into words correctly """
        verse = self.constructVerse("""(Arma'virumque,%cano.!Troiae^$qui";primus/ab oris)""")
        verse.split()
        self.assertEqual(verse.words, expected_word_list)

    def test_spacesVerse(self):
        """ A verse with unusual and heavy spacing must be split into words correctly """
        verse = self.constructVerse("""      Arma\tvirumque\rcano\nTroiae\r\nqui\n\rprimus  \b \r   ab    oris.  """)
        verse.split()
        self.assertEqual(verse.words, expected_word_list)


if __name__ == '__main__':
    unittest.main()
