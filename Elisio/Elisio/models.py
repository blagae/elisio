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
import enum
from functools import total_ordering


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
            result.append(Syllable.create_syllable_from_database(syll))
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


class Period(Model):
    """ model class that contains a Period """
    name = CharField(max_length=20)
    start_year = IntegerField()
    end_year = IntegerField()
    description = CharField(max_length=200)

    def __str__(self):
        return self.name


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

    def get_parent(self):
        return None

    def __str__(self):
        return self.short_name


class Genre(Model):
    """ model class that contains a Genre """
    name = CharField(max_length=20)
    description = CharField(max_length=200)

    def __str__(self):
        return self.name


class Opus(Model):
    class Meta:
        verbose_name_plural = "opera"

    """ model class that contains an Opus """
    full_name = CharField(max_length=40)
    abbreviation = CharField(max_length=10)
    alternative_name = CharField(max_length=40)
    author = ForeignKey(Author)
    publication = IntegerField()
    genre = ForeignKey(Genre)

    def get_parent(self):
        return self.author

    def __str__(self):
        return self.full_name


class Book(Model):
    """ model class that contains a Book """
    opus = ForeignKey(Opus)
    number = IntegerField()

    def get_parent(self):
        return self.opus

    def __str__(self):
        return self.opus.__str__() + " " + str(self.number)


class Poem(Model):
    """ model class that contains a Poem """
    book = ForeignKey(Book)
    number = IntegerField()
    nickname = CharField(max_length=20)
    verseForm = EnumField(VerseForm, default=VerseForm.HEXAMETRIC)

    def get_parent(self):
        return self.book

    def __str__(self):
        return self.number


class DatabaseVerse(Model):
    """ model class that contains a Verse """
    poem = ForeignKey(Poem)
    number = IntegerField()
    alternative = CharField(max_length=1)
    contents = CharField(max_length=70)
    saved = BooleanField(default=False)
    verseType = EnumField(VerseType, default=VerseType.HEXAMETER)

    def get_parent(self):
        return self.poem

    def get_verse(self):
        """ create a Verse object from this DatabaseVerse """
        return self.contents

    @staticmethod
    def get_maximum_verse_num(poem):
        """ get the highest verse number in this poem """
        return (DatabaseVerse.objects.filter(poem=poem)
                .aggregate(Max('number'))['number__max'])

    @staticmethod
    def get_verse_from_db(poem, verse):
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
    objects = InheritanceManager()

    class Meta:
        base_manager_name = 'objects'

    def get_number_of_verses(self):
        raise Exception("must be overridden")


@total_ordering
class ObjectType(enum.Enum):
    VERSE = 1
    POEM = 2
    BOOK = 3
    OPUS = 4
    AUTHOR = 5
    ALL = 9  # keep leeway for intermediate types

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


class RelationType(enum.Enum):
    EXCEPT = 1
    AND = 2
    OR = 3


class DatabaseBatchItem(BatchItem):
    object_type = EnumField(ObjectType, null=True)
    object_id = IntegerField(blank=True)
    relation = EnumField(RelationType, null=True)
    dependent_on = ForeignKey("self", null=True)

    def save(self, *args, **kwargs):
        self.pre_save_hook()
        super(DatabaseBatchItem, self).save(*args, **kwargs)

    def pre_save_hook(self):
        # rules for relations
        if self.relation == RelationType.AND:
            raise ValidationError("cannot have corpus conditions in an AND relation")
        if self.relation and not self.dependent_on:
            # redeem impossible "[] except self"
            inter = DatabaseBatchItem()
            inter.object_type = ObjectType.ALL
            inter.save()
            self.dependent_on = inter
            self.relation = RelationType.EXCEPT
        if self.dependent_on and not self.relation:
            raise ValidationError("must have a relationship to its master")
        if self.relation == RelationType.EXCEPT:
            if self.dependent_on.object_type <= self.object_type:
                raise ValidationError("the except clause must be more specific than its master")
            if not self.__is_in(self.dependent_on):
                raise ValidationError("the except clause must be part of its master")
        if self.relation == RelationType.OR and self.__is_in(self.dependent_on):
            raise ValidationError("the or clause must be distinct from its master")
        try:
            self.get_object()
        except Exception:
            raise ValidationError("the object you're trying to save a BatchItem for doesn't exist")

    def __is_in(self, other):
        if self.object_type > other.object_type:
            # only look one way
            return other.__is_in(self)
        if self.object_type == other.object_type:
            return self.object_id == other.object_id
        if other.object_type == ObjectType.ALL:
            return True
        me = self.get_object()
        you = other.get_object()
        while me:
            if me == you:
                return True
            me = me.get_parent()
        return False

    def get_number_of_verses(self):
        result = self.get_verse_count()
        if self.relation == RelationType.EXCEPT:
            result *= -1
        return result

    def get_object(self):
        if self.get_object_manager():
            return self.get_object_manager().get(pk=self.object_id)
        return None

    def get_object_manager(self):
        if self.object_type == ObjectType.VERSE:
            return DatabaseVerse.objects
        if self.object_type == ObjectType.POEM:
            return Poem.objects
        if self.object_type == ObjectType.BOOK:
            return Book.objects
        if self.object_type == ObjectType.OPUS:
            return Opus.objects
        if self.object_type == ObjectType.AUTHOR:
            return Author.objects
        if self.object_type == ObjectType.ALL:
            return None
        raise ValidationError("Incorrect object type")

    def get_verse_count(self):
        if self.object_type == ObjectType.VERSE:
            return 1
        if self.object_type == ObjectType.POEM:
            return DatabaseVerse.objects.filter(poem_id=self.object_id).count()
        if self.object_type == ObjectType.BOOK:
            return DatabaseVerse.objects.filter(poem__book_id=self.object_id).count()
        if self.object_type == ObjectType.OPUS:
            return DatabaseVerse.objects.filter(poem__book__opus_id=self.object_id).count()
        if self.object_type == ObjectType.AUTHOR:
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
