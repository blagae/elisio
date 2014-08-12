from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.core import serializers
from Elisio.models import *

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

def json(request, type, key):
    pk = int(key)
    if type == 'author':
        objects = Opus.objects.filter(author=pk)
    elif type == 'opus':
        objects = Book.objects.filter(opus=pk)
    elif type == 'book':
        objects = Poem.objects.filter(book=pk)
    elif type == 'poem':
        pass
    elif type == 'verse':
        # requires info from poem, too ?
        pass
    else:
        raise Http404
    data = serializers.serialize('json', objects)
    return HttpResponse(data, mimetype='application/json')