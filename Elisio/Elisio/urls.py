""" standard Django module """
from django.conf.urls import patterns, include, url
from Elisio import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = ['',
                       # Examples:
                       url(r'^$', views.index),
                       url(r'^batch/$', views.batch),
                       url(r'^faq/$', views.faq),
                       url(r'^help/$', views.help_page),
                       url(r'^about/$', views.about),
                       url(r'^json/([a-zA-Z]+)/([0-9]+)$', views.json_list),
                       url(r'^json/verse/([0-9]+)/([0-9]+)$', views.json_verse),
                       url(r'^admin/', include(admin.site.urls)),
                      ]
