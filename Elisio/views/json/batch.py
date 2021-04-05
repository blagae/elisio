import json
from django.http import HttpResponse, Http404, HttpResponseForbidden

from elisio.util.batchutils import scan_session
from elisio.models.scan import Batch, DatabaseBatchItem, InputBatchItem, ScanSession, ObjectType, RelationType
from random import randint
from elisio.engine.VerseFactory import VerseType
from django.db.models import ObjectDoesNotExist
from django.core.exceptions import ValidationError


def clear_batch_session(request):
    request.session['verses'] = []
    request.session['batchitems'] = []
    return HttpResponse(status=204)  # empty response


def get_batches(request):
    if request.user.is_authenticated:
        batches = Batch.objects.filter(user=request.user).order_by('timing')
        objects = []
        for batch in batches:
            data = {'id': batch.id,
                    'timing': str(batch.timing),
                    'itemsAtCreation': batch.items_at_creation_time,
                    'itemsNow': batch.get_number_of_verses(),
                    'name': batch.name
                    }
            scans = ScanSession.objects.filter(batch=batch).order_by('timing')
            if scans.count() > 0:
                data['scans'] = {'number': scans.count(),
                                 'recent': str(scans[scans.count() - 1].timing)
                                 }
            objects.append(data)
        return HttpResponse(json.dumps(objects), content_type='application/json')
    return HttpResponseForbidden()


def save_batchitems(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden()
    if request.method != 'POST':
        return HttpResponse(status=405)
    if 'batchitems' not in request.session:
        request.session['batchitems'] = []
    for item in json.loads(request.body):
        itemtype = item["type"]
        itemid = item["id"]
        relation = item.get("relation", None)
        if itemtype not in ('all', 'author', 'opus', 'book', 'poem'):
            return HttpResponseForbidden()
        if itemtype == 'all' and relation == 'except':
            continue
        data = {'type': itemtype,
                'id': itemid,
                'relation': relation
                }
        request.session['batchitems'].append(data)
    request.session.modified = True
    return HttpResponse(status=204)  # empty response


def save_batch(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden()
    if request.method != 'POST':
        return HttpResponse(status=405)
    if (('verses' not in request.session or len(request.session['verses']) < 1) and
            ('batchitems' not in request.session or len(request.session['batchitems']) < 1)):
        return Http404()
    sess = Batch()
    sess.user = request.user
    sess.name = request.user.username + str(randint(1, 20))
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
                if 'relation' not in item:
                    continue
                res.dependent_on = prev
                res.relation = RelationType[item['relation'].upper()]
            try:
                res.save()
                prev = res
            except ValidationError:
                pass  # TODO: investigate whether to pass
    sess.items_at_creation_time = sess.get_number_of_verses()
    sess.save()
    return clear_batch_session(request)


def run_batch(request, batchid):
    if not request.user.is_authenticated:
        return HttpResponseForbidden()
    if request.method != 'POST':
        return HttpResponse(status=405)
    batch = Batch.objects.get(pk=batchid)
    if request.user != batch.user:
        return HttpResponseForbidden()
    verses = batch.get_verses()
    session = ScanSession()
    session.batch = batch
    session.initiator = batch.user.username
    session.save()
    worked, failed, wwd = scan_session(verses, session)
    objects = {"worked": worked, "failed": failed, "wwd": wwd}
    return HttpResponse(json.dumps(objects), content_type='application/json')


def delete_batch(request, batchid):
    if not request.user.is_authenticated:
        return HttpResponseForbidden()
    if request.method != 'DELETE':
        return HttpResponse(status=405)
    try:
        sess = Batch.objects.get(pk=batchid)
        if sess.user != request.user:
            return HttpResponse(status=401)
        sess.delete()
        return HttpResponse(status=204)
    except ObjectDoesNotExist:
        return HttpResponse(status=404)


def delete_verse_hash(request, hashvalue):
    result = False
    for verse in request.session['verses']:
        if verse["id"] == hashvalue:
            result = verse
            break
    if result:
        request.session['verses'].remove(result)
        request.session.modified = True
    return HttpResponse(status=204)  # empty response
