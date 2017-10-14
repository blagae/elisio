from django.contrib.auth.models import User
from django.core import serializers
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from Elisio.models import Author, Opus, Book, Poem
import Elisio.batchjob


def sync_files(request):
    if request.user.is_superuser:
        Elisio.batchjob.sync_files()
        return HttpResponse(status=204)
    return HttpResponseForbidden()


def sync_db(request):
    if request.user.is_superuser:
        Elisio.batchjob.sync_db()
        return HttpResponse(status=204)
    return HttpResponseForbidden()


def get_member_list(request):
    if request.user.is_superuser:
        objects = User.objects.all()
        for d in objects:
            d.password = ''
        data = serializers.serialize('json', objects)
        return HttpResponse(data, content_type='application/json')
    return HttpResponseForbidden()


def upload_text(request):
    if not (request.user.is_superuser and request.method == 'POST'):
        return HttpResponseForbidden()
    poem_name = request.POST['poem']
    try:
        poem = Elisio.batchjob.find_poem(poem_name)
    except Author.DoesNotExist:
        return HttpResponseNotFound("author not found")
    except Opus.DoesNotExist:
        return HttpResponseNotFound("opus not found")
    except Book.DoesNotExist:
        return HttpResponseNotFound("book not found")
    except Poem.DoesNotExist:
        return HttpResponseNotFound("poem not found")
    lines = request.POST['fulltext'].replace('\r\n', '\n').split('\n')
    Elisio.batchjob.create_verses(poem, lines)
    return HttpResponse(status=204)
