""" standard Django views module for back-end logic """
import json
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.core import serializers
from Elisio.exceptions import ScansionException
from Elisio.models import Author, Book, Opus, Poem, DatabaseVerse, ScanSession, ScanVerseResult
from Elisio.engine.TextDecorator import TextDecorator
from Elisio.engine.VerseFactory import VerseFactory, VerseType
from random import randint
from Elisio.numerals import int_to_roman
import hashlib
import time
from Elisio.batchjob import syncDb, syncFiles

def clear_batch_session(request):
    request.session['verses'] = []
    return HttpResponse(status=204) # empty response

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

def get_batches(request):
    if request.user.is_authenticated:
        objects = ScanSession.objects.filter(user=request.user).order_by('timing')
        return wrap_in_response(objects)
    return HttpResponseForbidden()

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
    obj = get_verse_local(poem, verse)
    data = get_metadata(obj)
    return HttpResponse(json.dumps(data), content_type='application/json')

def get_verse_local(poem, verse):
    primary = int(verse)
    poem_pk = int(poem)
    return DatabaseVerse.get_verse_from_db(poem_pk, primary)

def save_batch(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden()
    if not request.session['verses'] or len(request.session['verses']) < 1:
        return Http404()
    sess = ScanSession()
    sess.user = request.user
    sess.save()
    for verse in request.session['verses']:
        res = ScanVerseResult()
        res.session = sess
        res.verse = get_verse_local(verse['poem']['id'], verse['verse']['number'])
        res.scanned_as = VerseType[verse['verse']['type']]
        res.save()
    request.session['verses'] = []
    return HttpResponse(status=204)

def scan_verse_text(request, txt, metadata=None):
    # watch out before doing ANYTHING related to the db
    if not metadata:
        metadata = {'verse': {'text': txt}}
    data = {}
    try:
        dict = 'disableDict' not in request.GET
        try:
            verseType = VerseType[request.GET['type'].upper()]
        except:
            verseType = VerseType.UNKNOWN
        metadata['verse']['type'] = verseType.name
        update_req_with_verse(request, metadata)
        verse = VerseFactory.create(txt, dict, classes=verseType)
        s = TextDecorator(verse).decorate()
        data["text"] = s
        data["zeleny"] = verse.get_zeleny_score()
    except ScansionException as ex:
        data["error"] = str(ex)
    return HttpResponse(json.dumps(data), content_type='application/json')

def delete_verse_hash(request, hash):
    result = False
    for verse in request.session['verses']:
        if verse["id"] == hash:
            result = verse
            break
    if result:
        request.session['verses'].remove(result)
        request.session.modified = True
    return HttpResponse(status=204) # empty response

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
        verseNum = randint(1, count)
        try:
            verse = DatabaseVerse.objects.get(id=verseNum)
        except Exception:
            pass
    metadata = get_metadata(verse)
    return HttpResponse(json.dumps(metadata), content_type='application/json')

def get_metadata(verse):
    if isinstance(verse, DatabaseVerse):
        metadata = {'verse': {'text': verse.contents,
                               'number': verse.number,
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

def sync_files(request):
    if request.user.is_superuser:
        syncFiles()
        return HttpResponse(status=204)
    return HttpResponseForbidden()

def sync_db(request):
    if request.user.is_superuser:
        syncDb()
        return HttpResponse(status=204)
    return HttpResponseForbidden()
