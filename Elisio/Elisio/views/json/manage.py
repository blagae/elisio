from django.http import HttpResponse, HttpResponseForbidden
from Elisio.batchjob import syncDb, syncFiles
from django.contrib.auth.models import User
from Elisio.models import Author
from django.core import serializers

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

def get_member_list(request):
    if request.user.is_superuser:
        objects = User.objects.all()
        for d in objects:
            d.password = ''
        data = serializers.serialize('json', objects)
        return HttpResponse(data, content_type='application/json')
    return HttpResponseForbidden()