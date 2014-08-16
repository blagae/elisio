from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.core import serializers
from Elisio.models import *
import json

context = {}

def index(request):
    context['authors'] = Author.objects.all()
    return render(request, 'index.html', context)

def batch(request):
    return render(request, 'batch.html', context)

def faq(request):
    return render(request, 'faq.html', context)

def help(request):
    return render(request, 'help.html', context)

def about(request):
    return render(request, 'about.html', context)

def jsonList(request, type, key):
    pk = int(key)
    if type == 'author':
        objects = Opus.objects.filter(author=pk)
    elif type == 'opus':
        objects = Book.objects.filter(opus=pk)
    elif type == 'book':
        objects = Poem.objects.filter(book=pk)
    elif type == 'poem':
        return HttpResponse(Db_Verse.getMaximumVerseNumber(poem=pk))
    else:
        raise Http404
    data = serializers.serialize('json', objects)
    return HttpResponse(data, mimetype='application/json')

def jsonVerse(request, poem, verse):
    pk = int(verse)
    poemPk = int(poem)
    object = Db_Verse.getVerseFromDb(poemPk, pk)
    data = json.dumps(object)
    return HttpResponse(data, mimetype='application/json')