""" standard Django module """
from django.db import models
from Elisio.engine.Syllable import Weight, Syllable
from Elisio.engine.Verse import Verse
from Elisio.exceptions import WordException
from enumfields import EnumField
import re

class DeviantWord(models.Model):
    """ model class for the Engine: highest level """
    words = []
    stem = models.CharField(max_length=25)

    @classmethod
    def find(cls, text):
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
            result.append(Syllable.create_syllable_from_database(syll))
        return result

    @classmethod
    def get_list(cls):
        """ get full list of deviant words in memory """
        if len(DeviantWord.words) < 1:
            DeviantWord.words = DeviantWord.objects.all()

class DeviantSyllable(models.Model):
    """ model class for the Engine: lowest level """
    word = models.ForeignKey(DeviantWord)
    weight = EnumField(Weight)
    contents = models.CharField(max_length=8)
    sequence = models.IntegerField()
    index_together = [["word", "sequence"]]

class Period(models.Model):
    """ model class that contains a Period """
    name = models.CharField(max_length=20)
    start_year = models.IntegerField()
    end_year = models.IntegerField()
    description = models.CharField(max_length=200)

class Author(models.Model):
    """ model class that contains an Author """
    full_name = models.CharField(max_length=45)
    short_name = models.CharField(max_length=18)
    abbreviation = models.CharField(max_length=10)
    period = models.ForeignKey(Period)
    birth_year = models.IntegerField()
    dying_year = models.IntegerField()
    floruit_start = models.IntegerField()
    floruit_end = models.IntegerField()

class Genre(models.Model):
    """ model class that contains a Genre """
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=200)

class Opus(models.Model):
    """ model class that contains an Opus """
    full_name = models.CharField(max_length=40)
    abbreviation = models.CharField(max_length=10)
    alternative_name = models.CharField(max_length=40)
    author = models.ForeignKey(Author)
    publication = models.IntegerField()
    genre = models.ForeignKey(Genre)

class Book(models.Model):
    """ model class that contains a Book """
    opus = models.ForeignKey(Opus)
    number = models.IntegerField()

class Poem(models.Model):
    """ model class that contains a Poem """
    book = models.ForeignKey(Book)
    number = models.IntegerField()
    nickname = models.CharField(max_length=20)

class DatabaseVerse(models.Model):
    """ model class that contains a Verse """
    poem = models.ForeignKey(Poem)
    number = models.IntegerField()
    alternative = models.CharField(max_length=1)
    contents = models.CharField(max_length=70)
    saved = models.BooleanField(default=False)
    structure = models.CharField(max_length=10)

    def get_verse(self):
        """ create a Verse object from this DatabaseVerse """
        return self.contents# Verse(self.contents, self.saved)

    @classmethod
    def get_maximum_verse_num(cls, poem):
        """ get the highest verse number in this poem """
        from django.db.models import Max
        return (DatabaseVerse.objects.all()
                .aggregate(Max('number'))['number__max'])

    @classmethod
    def get_verse_from_db(cls, poem, verse):
        """ django.core.serializers requires this return value
        to be iterable (i.e. a resultset) """
        result = DatabaseVerse.objects.get(poem=poem, number=verse)
        return result.contents

class WordOccurrence(models.Model):
    verse = models.ForeignKey(DatabaseVerse, null=True)
    word = models.CharField(max_length=20)
    struct = models.CharField(max_length=10)