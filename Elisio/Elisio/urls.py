""" standard Django module """
from django.conf.urls import include, url
from django.contrib import admin
admin.autodiscover()
from Elisio import views

urlpatterns = [#'',
    # Examples:
    url(r'^$', views.index),
    url(r'^batch/$', views.batch),
    url(r'^help/$', views.help_page),
    url(r'^about/$', views.about),
    url(r'^login/$', views.inlog),
    url(r'^logout/$', views.outlog),
    url(r'^register/$', views.register),
    url(r'^profile/$', views.profile),
    url(r'^json/([a-zA-Z]+)/([0-9]+)$', views.json_list),
    url(r'^json/verse/([0-9]+)/([0-9]+)$', views.json_verse),
    url(r'^json/scan/([0-9]+)/([0-9]+)$', views.json_scan),
    url(r'^json/scanraw/(.+)$', views.json_scan_rawtext),
    url(r'^json/random/$', views.json_get_random_verse),
    url(r'^json/clearsession/$', views.json_clear_session),
    url(r'^json/deleteverse/([a-f0-9]{64})$', views.json_delete_hash),
    url(r'^admin/', admin.site.urls),
]
