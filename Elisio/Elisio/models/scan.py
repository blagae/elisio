from django.db.models import Model, CharField, ForeignKey, IntegerField, DateTimeField
from enumfields import EnumField
from Elisio.utils import get_commit
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from Elisio.engine.VerseType import VerseType
from model_utils.managers import InheritanceManager
import enum
from functools import total_ordering
from .metadata import DatabaseVerse, Poem, Book, Opus, Author


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
        super().save(*args, **kwargs)

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
