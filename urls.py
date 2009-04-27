from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^/?([a-zA-Z\d/_-]*)/edit/?$', 'simplewiki.views.edit', name='wiki_edit'),
    url(r'^/?([a-zA-Z\d/_-]*)/create/?$', 'simplewiki.views.create', name='wiki_create'),
    url(r'^/?([a-zA-Z\d/_-]*)/history/([0-9]*)/?$', 'simplewiki.views.history', name='wiki_history'),
    url(r'^/?([a-zA-Z\d/_-]*)/history/?$', 'simplewiki.views.history', {'page':1}, name='wiki_history'),
    url(r'^/?([a-zA-Z\d/_-]*)/search_related/?$', 'simplewiki.views.search_add_related', name='search_related'),
    url(r'^/?([a-zA-Z\d/_-]*)/add_related/?$', 'simplewiki.views.add_related', name='add_related'),
    url(r'^/?([a-zA-Z\d/_-]*)/remove_related([a-zA-Z\d/_-]*)$', 'simplewiki.views.remove_related', name='wiki_remove_relation'),
    url(r'^/?([a-zA-Z\d/_-]*)/add_attachment/?$', 'simplewiki.views_attachments.add_attachment', name='add_attachment'),
    url(r'^/?([a-zA-Z\d/_-]*)/view_attachment/(.+)?$', 'simplewiki.views_attachments.view_attachment', name='wiki_view_attachment'),
    url(r'^/?([a-zA-Z\d/_-]*)$', 'simplewiki.views.view', name='wiki_view'),
    url(r'^(.*)$', 'simplewiki.views.encode_err', name='wiki_encode_err')
)
