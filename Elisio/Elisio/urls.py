""" standard Django module """
from django.conf.urls import include, url
from django.contrib import admin
admin.autodiscover()
from Elisio.views import pages
from Elisio.views.json import index, manage, batch

urlpatterns = [
    url(r'^$', pages.index_page),
    url(r'^batch/$', pages.batch_page),
    url(r'^help/$', pages.help_page),
    url(r'^about/$', pages.about_page),
    url(r'^login/$', pages.login_page),
    url(r'^logout/$', pages.logout_page),
    url(r'^register/$', pages.register_page),
    url(r'^profile/$', pages.profile_page),
    url(r'^manage/', pages.manage_page),
    url(r'^admin/', admin.site.urls),
    url(r'^json/poem/([0-9]+)$', index.get_poem_length),
    url(r'^json/([a-zA-Z]+)/([0-9]+)$', index.get_list_type), # author, opus, book
    url(r'^json/authors/$', index.get_authors),
    url(r'^json/verse/([0-9]+)/([0-9]+)$', index.get_verse),
    url(r'^json/verse/random/$', index.get_random_verse),
    url(r'^json/scan/dbverse/([0-9]+)/([0-9]+)$', index.scan_verse),
    url(r'^json/scan/text/(.+)$', index.scan_verse_text),
    url(r'^json/batch/clearcurrentsession$', batch.clear_batch_session),
    url(r'^json/batch/save', batch.save_batch),
    url(r'^json/batch/delete/([0-9]+)$', batch.delete_batch),
    url(r'^json/batch/run/([0-9]+)$', batch.run_batch),
    url(r'^json/batch/deleteverse/([a-f0-9]{64})$', batch.delete_verse_hash),
    url(r'^json/batches/$', batch.get_batches),
    url(r'^json/admin/sync/files/$', manage.sync_files),
    url(r'^json/admin/sync/db/$', manage.sync_db),
]
