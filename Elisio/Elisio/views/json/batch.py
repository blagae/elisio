import json
from django.http import HttpResponse, Http404, HttpResponseForbidden
from Elisio.models import Batch, DatabaseBatchItem, InputBatchItem, ScanSession
from random import randint
from Elisio.engine.VerseFactory import VerseType
from django.db.models import ObjectDoesNotExist

def clear_batch_session(request):
    request.session['verses'] = []
    return HttpResponse(status=204) # empty response

def get_batches(request):
    if request.user.is_authenticated:
        batches = Batch.objects.filter(user=request.user).order_by('timing')
        objects = []
        for batch in batches:
            data = { 'id': batch.id,
                    'timing': str(batch.timing),
                    'itemsAtCreation': batch.items_at_creation_time,
                    'itemsNow': batch.get_number_of_verses(),
                    'name': batch.name
                    }
            scans = ScanSession.objects.filter(batch=batch).order_by('timing')
            if scans.count() > 0:
                data['scans'] = {'number': scans.count(),
                                'recent': scans[-1].timing
                                }
            objects.append(data)
        return HttpResponse(json.dumps(objects), content_type='application/json')
    return HttpResponseForbidden()

def save_batch(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden()
    if request.method != 'POST':
        return HttpResponse(status=405)
    if not request.session['verses'] or len(request.session['verses']) < 1:
        return Http404()
    sess = Batch()
    sess.user = request.user
    sess.name = request.user.username + str(randint(1,20))
    sess.save()
    for verse in request.session['verses']:
        if 'id' in verse['verse']:
            res = DatabaseBatchItem()
            res.object_id = verse['verse']['id']
            res.object_type = 'verse'
        else:
            res = InputBatchItem()
            res.contents = verse['verse']['text']
            res.scanned_as = VerseType[verse['verse']['type']]
        res.batch = sess
        res.save()
    sess.items_at_creation_time = sess.get_number_of_verses()
    sess.save()
    request.session['verses'] = []
    return HttpResponse(status=204)

def run_batch(request, id):
    if not request.user.is_authenticated:
        return HttpResponseForbidden()
    if request.method != 'POST':
        return HttpResponse(status=405)
    # dummy method for now
    return HttpResponse(status=204)

def delete_batch(request, id):
    if not request.user.is_authenticated:
        return HttpResponseForbidden()
    if request.method != 'DELETE':
        return HttpResponse(status=405)
    try:
        sess = Batch.objects.get(pk=id)
        if sess.user == request.user:
            sess.delete()
            code = 204
        else:
            code = 401
    except ObjectDoesNotExist:
        code = 404
    return HttpResponse(status=code)

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
