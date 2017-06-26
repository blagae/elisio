import json
from django.http import HttpResponse, Http404, HttpResponseForbidden
from Elisio.models import Batch, DatabaseBatchItem, InputBatchItem, ScanSession, ObjectType
from random import randint
from Elisio.engine.VerseFactory import VerseType
from django.db.models import ObjectDoesNotExist

def clear_batch_session(request):
    request.session['verses'] = []
    request.session['batchitems'] = []
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

def save_batchitems(request, type, id):
    if not request.user.is_authenticated:
        return HttpResponseForbidden()
    if request.method != 'POST':
        return HttpResponse(status=405)
    if type not in ('all', 'author', 'opus', 'book', 'poem'):
        return HttpResponseForbidden()
    if not 'batchitems' in request.session:
        request.session['batchitems'] = []
    data = { 'type': type,
            'id': id,
            }
    if 'relation' in request.POST and len(request.session['batchitems']) > 0:
        data['relation'] = request.POST['relation']
    request.session['batchitems'].append(data)
    request.session.modified = True
    return HttpResponse(status=204) # empty response

def save_batch(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden()
    if request.method != 'POST':
        return HttpResponse(status=405)
    if ((not 'verses' in request.session or len(request.session['verses']) < 1) and
        (not 'batchitems' in request.session or len(request.session['batchitems']) < 1)):
        return Http404()
    sess = Batch()
    sess.user = request.user
    sess.name = request.user.username + str(randint(1,20))
    sess.save()
    if 'verses' in request.session:
        for verse in request.session['verses']:
            if 'id' in verse['verse']:
                res = DatabaseBatchItem()
                res.object_id = verse['verse']['id']
                res.object_type = ObjectType.VERSE
            else:
                res = InputBatchItem()
                res.contents = verse['verse']['text']
                res.scanned_as = VerseType[verse['verse']['type']]
            res.batch = sess
            res.save()
    if 'batchitems' in request.session:
        prev = None
        for item in request.session['batchitems']:
            res = DatabaseBatchItem()
            res.object_id = item['id']
            res.object_type = ObjectType[item['type'].upper()]
            res.batch = sess
            if prev:
                if not 'relation' in item:
                    continue
                res.dependent_on = prev
                res.relation = RelationType[item['relation'].upper()]
            res.save()
            prev = res
    sess.items_at_creation_time = sess.get_number_of_verses()
    sess.save()
    return clear_batch_session(request)

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
