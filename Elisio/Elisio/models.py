from django.db import models
from Elisio.engine.wordProcessor import Weights, Syllable
from Elisio.engine.verseProcessor import Verse
from Elisio.exceptions import ScansionException
from enumfields import EnumField
import re

class DeviantWord(models.Model):
    words = []
    stem = models.CharField(max_length=25)

    @classmethod
    def find(cls, text):
        DeviantWord.get_list()
        result = [word for word in DeviantWord.words if re.compile(word.stem).match(text)]
        if len(result) > 1:
            raise ScansionException
        if not result:
            return None
        return result[0]

    def get_syllables(self):
        sylls = DeviantSyllable.objects.filter(word=self).order_by('sequence')
        result = []
        for syll in sylls:
            result.append(Syllable.create_syllable_from_database(syll))
        return result

    @classmethod
    def get_list(cls):
        if len(DeviantWord.words) < 1:
            DeviantWord.words = DeviantWord.objects.all()

class DeviantSyllable(models.Model):
    word = models.ForeignKey(DeviantWord)
    weight = EnumField(Weights)
    contents = models.CharField(max_length=8)
    sequence = models.IntegerField()
    index_together = [["word", "sequence"]]

class Period(models.Model):
    name = models.CharField(max_length=20)
    start_year = models.IntegerField()
    end_year = models.IntegerField()
    description = models.CharField(max_length=200)

class Author(models.Model):
    full_name = models.CharField(max_length=45)
    short_name = models.CharField(max_length=18)
    abbreviation = models.CharField(max_length=10)
    period = models.ForeignKey(Period)
    birth_year = models.IntegerField()
    dying_year = models.IntegerField()
    floruit_start = models.IntegerField()
    floruit_end = models.IntegerField()

class Genre(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=200)

class Opus(models.Model):
    full_name = models.CharField(max_length=40)
    abbreviation = models.CharField(max_length=10)
    alternative_name = models.CharField(max_length=40)
    author = models.ForeignKey(Author)
    publication = models.IntegerField()
    genre = models.ForeignKey(Genre)

class Book(models.Model):
    opus = models.ForeignKey(Opus)
    number = models.IntegerField()

class Poem(models.Model):
    book = models.ForeignKey(Book)
    number = models.IntegerField()
    nickname = models.CharField(max_length=20)

class DatabaseVerse(models.Model):
    poem = models.ForeignKey(Poem)
    number = models.IntegerField()
    alternative = models.CharField(max_length=1)
    contents = models.CharField(max_length=70)

    def get_verse(self):
        return Verse(self.contents)

    @classmethod
    def get_maximum_verse_number(cls, poem):
        from django.db.models import Max
        return DatabaseVerse.objects.all().aggregate(Max('number'))['number__max']

    @classmethod
    def get_verse_from_db(cls, poem, verse):
        """ django.core.serializers requires this return value to be iterable (i.e. a resultset) """
        result = DatabaseVerse.objects.get(poem=poem, number=verse)
        return result.contents
