""" standard Django module """
from django.conf.urls import include, url
from django.contrib import admin
admin.autodiscover()
from Elisio.views import json, page

urlpatterns = [
    url(r'^$', page.index),
    url(r'^batch/$', page.batch),
    url(r'^help/$', page.help_page),
    url(r'^about/$', page.about),
    url(r'^login/$', page.inlog),
    url(r'^logout/$', page.outlog),
    url(r'^register/$', page.register),
    url(r'^profile/$', page.profile),
    url(r'^admin/', admin.site.urls),
    url(r'^manage/', page.manage),
    url(r'^json/([a-zA-Z]+)/([0-9]+)$', json.list),
    url(r'^json/verse/([0-9]+)/([0-9]+)$', json.verse),
    url(r'^json/scan/([0-9]+)/([0-9]+)$', json.scan),
    url(r'^json/scanraw/(.+)$', json.scan_rawtext),
    url(r'^json/random/$', json.get_random_verse),
    url(r'^json/clearsession/$', json.clear_session),
    url(r'^json/deleteverse/([a-f0-9]{64})$', json.delete_hash),
    url(r'^json/admin/syncFiles/$', json.syncFiles),
    url(r'^json/admin/syncDb/$', json.syncDb),
]
