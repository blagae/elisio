""" standard Django views module for back-end logic """
import json
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.core import serializers
from Elisio.models import Author, Book, Opus, Poem, DatabaseVerse
from Elisio.engine.TextDecorator import TextDecorator
from Elisio.engine.VerseFactory import VerseFactory
from Elisio.engine.Hexameter import HexameterCreator
#from Elisio.models import *

CONTEXT = {}

def index(request):
    """ return index page """
    CONTEXT['authors'] = Author.objects.filter(opus__book__gt=0).distinct()
    return render(request, 'index.html', CONTEXT)

def batch(request):
    """ return batch page """
    return render(request, 'batch.html', CONTEXT)

def faq(request):
    """ return FAQ page """
    return render(request, 'faq.html', CONTEXT)

def help_page(request):
    """ return help page """
    return render(request, 'help.html', CONTEXT)

def about(request):
    """ return about page """
    return render(request, 'about.html', CONTEXT)

def json_list(request, obj_type, key):
    """ get a list of the requested Object Type """
    primary = int(key)
    if obj_type == 'author':
        objects = Opus.objects.filter(author=primary)
    elif obj_type == 'opus':
        objects = Book.objects.filter(opus=primary)
    elif obj_type == 'book':
        objects = Poem.objects.filter(book=primary)
    elif obj_type == 'poem':
        return HttpResponse(DatabaseVerse.get_maximum_verse_num(poem=primary))
    else:
        raise Http404
    data = serializers.serialize('json', objects)
    return HttpResponse(data, content_type='application/json')

def json_verse(request, poem, verse):
    """ get a verse through a JSON request """
    primary = int(verse)
    poem_pk = int(poem)
    obj = DatabaseVerse.get_verse_from_db(poem_pk, primary)
    data = json.dumps(obj)
    return HttpResponse(data, content_type='application/json')

def json_scan(request, poem, verse):
    """ get a verse through a JSON request """
    primary = int(verse)
    poem_pk = int(poem)
    obj = DatabaseVerse.get_verse_from_db(poem_pk, primary)
    verse = VerseFactory.create(obj, False, True, classes=HexameterCreator)
    s = TextDecorator(verse).decorate()
    data = json.dumps(s)
    return HttpResponse(data, content_type='application/json')
