from django.db.models import Model, CharField, ForeignKey, IntegerField
from enumfields import EnumField
import re
from Elisio.engine.Syllable import Weight, Syllable
from Elisio.exceptions import WordException


class DeviantWord(Model):
    """ model class for the Engine: highest level """
    words = []
    stem = CharField(max_length=25)

    @staticmethod
    def find(text):
        """ check for a regex in the db that matches this word """
        DeviantWord.get_list()
        result = [word for word in DeviantWord.words
                  if re.compile(word.stem).match(text)]
        if len(result) > 1:
            raise WordException
        if not result:
            return None
        return result[0]

    def get_syllables(self):
        """ get the syllables for this deviant word """
        sylls = DeviantSyllable.objects.filter(word=self).order_by('sequence')
        result = []
        for syll in sylls:
            result.append(Syllable(syll.contents, False, syll.weight))
        return result

    @staticmethod
    def get_list():
        """ get full list of deviant words in memory """
        if len(DeviantWord.words) < 1:
            DeviantWord.words = DeviantWord.objects.all()


class DeviantSyllable(Model):
    """ model class for the Engine: lowest level """
    word = ForeignKey(DeviantWord)
    weight = EnumField(Weight)
    contents = CharField(max_length=8)
    sequence = IntegerField()
    index_together = [["word", "sequence"]]
