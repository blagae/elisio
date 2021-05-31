import unittest

from elisio.parser.hendeca import Hendeca, PhalaecianHendeca
from elisio.parser.verse import Foot, Verse
from elisio.parser.versefactory import VerseFactory, VerseType


def construct_hendeca(text="doctis, Iuppiter, et laboriosis."):
    """ Construct a Hendeca object from a given text """
    constructed_verse = VerseFactory.create(text, creators=VerseType.HENDECASYLLABUS)
    return constructed_verse


class TestHendeca(unittest.TestCase):
    """ testing specifically for the hendeca """

    def test_hendeca_construct(self):
        """ constructing a Hendeca must work """
        self.assertTrue(isinstance(construct_hendeca(), Verse))
        self.assertTrue(isinstance(construct_hendeca(), Hendeca))
        self.assertTrue(isinstance(construct_hendeca(), PhalaecianHendeca))
