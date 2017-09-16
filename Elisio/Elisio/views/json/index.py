""" standard Django views module for back-end logic """
import hashlib
import json
import time
from random import randint

from django.core import serializers
from django.http import HttpResponse, Http404

from Elisio.engine.TextDecorator import TextDecorator
from Elisio.engine.VerseFactory import VerseFactory, VerseType
from Elisio.exceptions import ScansionException
from Elisio.models import Author, Book, Opus, Poem, DatabaseVerse
from Elisio.numerals import int_to_roman


def get_list_type(request, obj_type, key):
    """ get a list of the requested Object Type """
    primary = int(key)
    if obj_type == 'author':
        objects = Opus.objects.filter(author=primary).order_by('publication')
    elif obj_type == 'opus':
        objects = Book.objects.filter(opus=primary).order_by('number')
    elif obj_type == 'book':
        objects = Poem.objects.filter(book=primary).order_by('number')
    else:
        raise Http404
    return wrap_in_response(objects)


def get_poem_length(request, key):
    primary = int(key)
    return HttpResponse(DatabaseVerse.get_maximum_verse_num(poem=primary))


def get_authors(request):
    objects = Author.objects.filter(opus__book__gt=0).order_by('floruit_start').distinct()
    return wrap_in_response(objects)


def wrap_in_response(objects):
    data = serializers.serialize('json', objects)
    return HttpResponse(data, content_type='application/json')


def update_req_with_verse(request, metadata):
    if 'verses' not in request.session:
        request.session['verses'] = []
    prehash = metadata["verse"]["text"] + (str(time.time() * 1000))
    prehash = prehash.encode('utf-8')
    metadata["id"] = hashlib.sha256(prehash).hexdigest()
    request.session['verses'].append(metadata)
    # https://stackoverflow.com/questions/43904060/editing-session-variable-in-django
    request.session.modified = True


def get_verse(request, poem, verse):
    """ get a verse through a JSON request """
    obj = get_verse_object(poem, verse)
    data = get_metadata(obj)
    return HttpResponse(json.dumps(data), content_type='application/json')


def get_verse_object(poem, verse):
    primary = int(verse)
    poem_pk = int(poem)
    return DatabaseVerse.get_verse_from_db(poem_pk, primary)


def scan_verse_text(request, txt, metadata=None):
    # watch out before doing ANYTHING related to the db
    if not metadata:
        metadata = {'verse': {'text': txt}}
    data = {}
    try:
        dic = 'disableDict' not in request.GET
        try:
            verse_type = VerseType[request.GET['type'].upper()]
        except KeyError:
            verse_type = VerseType.UNKNOWN
        metadata['verse']['type'] = verse_type.name
        update_req_with_verse(request, metadata)
        verse = VerseFactory.create(txt, dic, classes=verse_type)
        s = TextDecorator(verse).decorate()
        data["text"] = s
        data["zeleny"] = verse.get_zeleny_score()
    except ScansionException as ex:
        data["error"] = str(ex)
    return HttpResponse(json.dumps(data), content_type='application/json')


def scan_verse(request, poem, verse):
    """ get a verse through a JSON request """
    primary = int(verse)
    poem_pk = int(poem)
    obj = DatabaseVerse.get_verse_from_db(poem_pk, primary)
    metadata = get_metadata(obj)
    return scan_verse_text(request, obj.contents, metadata)


def get_random_verse(request):
    count = DatabaseVerse.objects.count()
    if count < 2:
        return Http404()
    verse = None
    while verse is None:
        verse_num = randint(1, count)
        try:
            verse = DatabaseVerse.objects.get(id=verse_num)
        except Exception:
            pass
    metadata = get_metadata(verse)
    return HttpResponse(json.dumps(metadata), content_type='application/json')


def get_metadata(verse):
    if isinstance(verse, DatabaseVerse):
        metadata = {'verse': {'text': verse.contents,
                              'number': verse.number,
                              'id': verse.id,
                              'type': verse.verseType.name},
                    'poem': {'id': verse.poem.id,
                             'number': verse.poem.number},
                    'book': {'id': verse.poem.book.id,
                             'number': int_to_roman(verse.poem.book.number)},
                    'opus': {'id': verse.poem.book.opus.id,
                             'name': verse.poem.book.opus.full_name},
                    'author': {'id': verse.poem.book.opus.author.id,
                               'name': verse.poem.book.opus.author.short_name}
                    }
        return metadata
    return None
