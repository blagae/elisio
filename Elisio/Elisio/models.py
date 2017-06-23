""" standard Django module """
from django.db.models import *
import re
from Elisio.engine.Syllable import Weight, Syllable
from Elisio.exceptions import WordException
from enumfields import EnumField
from Elisio.utils import get_commit
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from Elisio.engine.VerseFactory import VerseType, VerseForm
from model_utils.managers import InheritanceManager

class DeviantWord(Model):
    """ model class for the Engine: highest level """
    words = []
    stem = CharField(max_length=25)

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

class DeviantSyllable(Model):
    """ model class for the Engine: lowest level """
    word = ForeignKey(DeviantWord)
    weight = EnumField(Weight)
    contents = CharField(max_length=8)
    sequence = IntegerField()
    index_together = [["word", "sequence"]]

class Period(Model):
    """ model class that contains a Period """
    name = CharField(max_length=20)
    start_year = IntegerField()
    end_year = IntegerField()
    description = CharField(max_length=200)

class Author(Model):
    """ model class that contains an Author """
    full_name = CharField(max_length=45)
    short_name = CharField(max_length=18)
    abbreviation = CharField(max_length=10)
    period = ForeignKey(Period)
    birth_year = IntegerField()
    dying_year = IntegerField()
    floruit_start = IntegerField()
    floruit_end = IntegerField()

class Genre(Model):
    """ model class that contains a Genre """
    name = CharField(max_length=20)
    description = CharField(max_length=200)

class Opus(Model):
    """ model class that contains an Opus """
    full_name = CharField(max_length=40)
    abbreviation = CharField(max_length=10)
    alternative_name = CharField(max_length=40)
    author = ForeignKey(Author)
    publication = IntegerField()
    genre = ForeignKey(Genre)

class Book(Model):
    """ model class that contains a Book """
    opus = ForeignKey(Opus)
    number = IntegerField()

class Poem(Model):
    """ model class that contains a Poem """
    book = ForeignKey(Book)
    number = IntegerField()
    nickname = CharField(max_length=20)
    verseForm = EnumField(VerseForm, default=VerseForm.HEXAMETRIC)

class DatabaseVerse(Model):
    """ model class that contains a Verse """
    poem = ForeignKey(Poem)
    number = IntegerField()
    alternative = CharField(max_length=1)
    contents = CharField(max_length=70)
    saved = BooleanField(default=False)
    verseType = EnumField(VerseType, default=VerseType.HEXAMETER)

    def get_verse(self):
        """ create a Verse object from this DatabaseVerse """
        return self.contents

    @classmethod
    def get_maximum_verse_num(cls, poem):
        """ get the highest verse number in this poem """
        return (DatabaseVerse.objects.filter(poem=poem)
                .aggregate(Max('number'))['number__max'])

    @classmethod
    def get_verse_from_db(cls, poem, verse):
        """ django.core.serializers requires this return value
        to be iterable (i.e. a resultset) """
        result = DatabaseVerse.objects.get(poem=poem, number=verse)
        return result

class WordOccurrence(Model):
    verse = ForeignKey(DatabaseVerse, null=True)
    word = CharField(max_length=20)
    struct = CharField(max_length=10)

class Batch(Model):
    timing = DateTimeField(auto_now=True)
    user = ForeignKey(User, null=True)
    items_at_creation_time = IntegerField(null=True)
    name = CharField(max_length=30)
    
    def get_number_of_verses(self):
        return sum(x.get_number_of_verses() for x in self.batchitem_set.select_subclasses())

class BatchItem(Model):
    batch = ForeignKey(Batch)
    dependent_on = ForeignKey("self", null=True)
    objects = InheritanceManager()

    def get_number_of_verses(self):
        raise Exception("must be overridden")

class DatabaseBatchItem(BatchItem):
    object_type = CharField(max_length=10)
    object_id = IntegerField(blank=True)
    relation = CharField(max_length=10)
    negation = BooleanField(default=False)
    
    def get_number_of_verses(self):
        if self.object_type == 'verse':
            return 1
        if self.object_type == 'poem':
            return DatabaseVerse.objects.filter(poem_id=self.object_id).count()
        if self.object_type == 'book':
            return DatabaseVerse.objects.filter(poem__book_id=self.object_id).count()
        if self.object_type == 'opus':
            return DatabaseVerse.objects.filter(poem__book__opus_id=self.object_id).count()
        if self.object_type == 'author':
            if self.object_id == 0:
                return DatabaseVerse.objects.count()
            return DatabaseVerse.objects.filter(poem__book__opus__author_id=self.object_id).count()
        return 0

class InputBatchItem(BatchItem):
    contents = CharField(max_length=70)
    scanned_as = EnumField(VerseType, null=True)
    
    def get_number_of_verses(self):
        return 1

class ScanSession(Model):
    batch = ForeignKey(Batch, null=True, default=None)
    timing = DateTimeField(auto_now=True)
    initiator = CharField(max_length=40, default='')
    commit = CharField(max_length=40, default=get_commit)

class ScanVerseResult(Model):
    verse = ForeignKey(DatabaseVerse)
    session = ForeignKey(ScanSession)
    batch_item = ForeignKey(BatchItem, null=True, default=None)
    failure = CharField(max_length=70, blank=True)
    structure = CharField(max_length=8, blank=True)
    zeleny = CharField(max_length=17, blank=True)
    scanned_as = EnumField(VerseType)
