from django.contrib.auth.models import User
from django.core import serializers
from django.http import HttpResponse, HttpResponseForbidden

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
