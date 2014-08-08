from django.db import models
from Elisio.engine import Weights, Syllable
from django.core import validators
from Elisio.exceptions import ScansionException
from django_enumfield import enum
import re

class Deviant_Word(models.Model):
    words = []
    stem = models.CharField(max_length=25)
    
    @classmethod
    def find(cls, text):
        Deviant_Word.getList()
        result = [word for word in Deviant_Word.words if re.compile(word.stem).match(text)]
        if len(result) > 1:
            raise ScansionException
        if not result:
            return None
        return result[0]

    def getSyllables(self):
        sylls = Deviant_Syllable.objects.filter(word=self).order_by('sequence')
        result = []
        for syll in sylls:
            result.append(Syllable.createFromDatabase(syll))
        return result

    @classmethod
    def getList(cls):
        if len(Deviant_Word.words) < 1:
            Deviant_Word.words = Deviant_Word.objects.all()
    
class Deviant_Syllable(models.Model):
    word = models.ForeignKey(Deviant_Word)
    weight = enum.EnumField(Weights, default=Weights.ANCEPS)
    contents = models.CharField(max_length=8)
    sequence = models.IntegerField()
    index_together = [["word", "sequence"]]