""" standard Django views module for back-end logic """
import json
from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseServerError, HttpResponseRedirect
from django.core import serializers
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from Elisio.exceptions import ScansionException
from Elisio.models import Author, Book, Opus, Poem, DatabaseVerse
from Elisio.engine.TextDecorator import TextDecorator
from Elisio.engine.VerseFactory import VerseFactory
from Elisio.engine.Hexameter import HexameterCreator
from random import randint
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

def inlog(request):
    redirecter = request.GET.get('next', '/')
    if 'login' in redirecter:
        redirecter = '/'
    if request.method == 'POST':
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
        return HttpResponseRedirect(redirecter)
    return render(request, 'login.html', CONTEXT)

def outlog(request):
    redirecter = request.GET.get('next', '/')
    if request.user.is_authenticated:
        logout(request)
    return HttpResponseRedirect(redirecter)

def register(request):
    if request.method == 'POST':
        try:
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            User.objects.create_user(username, email, password)
            user = authenticate(username=username, password=password)
            login(request, user)
            return index(request)
        except Exception as e:
            # TODO: handle in error message
            pass
    return render(request, 'register.html', CONTEXT)

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

def update_req_with_verse(request, data):
    if 'verses' not in request.session:
        request.session['verses'] = []
    request.session['verses'].append(data)
    # https://stackoverflow.com/questions/43904060/editing-session-variable-in-django
    request.session.modified = True


def json_verse(request, poem, verse):
    """ get a verse through a JSON request """
    primary = int(verse)
    poem_pk = int(poem)
    obj = DatabaseVerse.get_verse_from_db(poem_pk, primary)
    data = json.dumps(obj.contents)
    return HttpResponse(data, content_type='application/json')

def json_scan_rawtext(request, txt):
    # watch out before doing ANYTHING related to the db
    update_req_with_verse(request, txt)
    try:
        dict = 'disableDict' not in request.GET
        verse = VerseFactory.create(txt, False, dict, classes=HexameterCreator)
        s = TextDecorator(verse).decorate()
    except ScansionException as ex:
        s = str(ex)
    data = json.dumps(s)
    return HttpResponse(data, content_type='application/json')

def json_scan(request, poem, verse):
    """ get a verse through a JSON request """
    primary = int(verse)
    poem_pk = int(poem)
    obj = DatabaseVerse.get_verse_from_db(poem_pk, primary)
    return json_scan_rawtext(request, obj.contents)

def json_get_random_verse(request):
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
    content = {'verse': verse.contents,
               'number': verse.number,
               'poem': verse.poem.id,
               'book': verse.poem.book.id,
               'opus': verse.poem.book.opus.id,
               'author': verse.poem.book.opus.author.id
               }
    return HttpResponse(json.dumps(content), content_type='application/json')