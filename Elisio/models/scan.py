import enum
from functools import total_ordering

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Model, CharField, ForeignKey, IntegerField, DateTimeField, Q
from django.db.models.deletion import CASCADE
from enumfields import EnumField
from model_utils.managers import InheritanceManager

from elisio.engine.verse.VerseType import VerseType
from elisio.util.utils import get_commit
from .metadata import DatabaseVerse, Poem, Book, Opus, Author


class WordOccurrence(Model):
    verse = ForeignKey(DatabaseVerse, CASCADE, null=True)
    word = CharField(max_length=20)
    struct = CharField(max_length=10)


class Batch(Model):
    timing = DateTimeField(auto_now=True)
    user = ForeignKey(User, CASCADE, null=True)
    items_at_creation_time = IntegerField(null=True)
    name = CharField(max_length=30)

    def get_number_of_verses(self):
        return sum(x.get_number_of_verses() for x in self.batchitem_set.select_subclasses())

    def build_batch_query(self):
        query = None
        for item in self.batchitem_set.all():
            try:
                dbitem = item.databasebatchitem
                q = dbitem.get_verse_query()
                if query is None:
                    query = q
                elif dbitem.relation == RelationType.EXCEPT:
                    query &= ~dbitem.get_verse_query()
                else:
                    query |= dbitem.get_verse_query()
            except AttributeError:
                pass
        return query

    def get_verses(self):
        return DatabaseVerse.objects.filter(self.build_batch_query())

    def get_input_items(self):
        return (item for item in self.batchitem_set.all() if hasattr(item, "contents"))


class BatchItem(Model):
    batch = ForeignKey(Batch, CASCADE)
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
    dependent_on = ForeignKey("self", CASCADE, null=True)

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
        result = self.get_verses().count()
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

    def get_verse_query(self):
        if self.object_type == ObjectType.VERSE:
            return Q(id=self.object_id)
        if self.object_type == ObjectType.POEM:
            return Q(poem_id=self.object_id)
        if self.object_type == ObjectType.BOOK:
            return Q(poem__book_id=self.object_id)
        if self.object_type == ObjectType.OPUS:
            return Q(poem__book__opus_id=self.object_id)
        if self.object_type == ObjectType.AUTHOR:
            if self.object_id == 0:
                return Q()
            return Q(poem__book__opus__author_id=self.object_id)
        raise ValidationError("Incorrect object type")

    def get_verses(self):
        return DatabaseVerse.objects.filter(self.get_verse_query())


class InputBatchItem(BatchItem):
    contents = CharField(max_length=70)
    scanned_as = EnumField(VerseType, null=True)

    def get_number_of_verses(self):
        return 1


class ScanSession(Model):
    batch = ForeignKey(Batch, CASCADE, null=True, default=None)
    timing = DateTimeField(auto_now=True)
    initiator = CharField(max_length=80, default='')
    commit = CharField(max_length=80, default=get_commit)


class ScanVerseResult(Model):
    verse = ForeignKey(DatabaseVerse, CASCADE)
    session = ForeignKey(ScanSession, CASCADE)
    failure = CharField(max_length=70, blank=True)
    structure = CharField(max_length=8, blank=True)
    zeleny = CharField(max_length=17, blank=True)
    scanned_as = EnumField(VerseType)
