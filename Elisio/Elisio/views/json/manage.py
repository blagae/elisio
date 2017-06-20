from django.http import HttpResponse, HttpResponseForbidden
from Elisio.batchjob import syncDb, syncFiles


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
