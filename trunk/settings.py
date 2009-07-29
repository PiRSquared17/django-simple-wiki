from django.utils.translation import ugettext_lazy as _
from django.conf import settings

# Default settings.. overwrite in your own settings.py

# This should be a directory that's writable for the web server.
# It's relative to the MEDIA_ROOT.
WIKI_ATTACHMENTS = getattr(settings, 'SIMPLE_WIKI_ATTACHMENTS',
                           'simplewiki/attachments/')

# At the moment this variable should not be modified, because
# it breaks compatibility with the normal Django FileField and uploading
# from the admin interface.
WIKI_ATTACHMENTS_ROOT = settings.MEDIA_ROOT

# Bytes! Default: 1 MB.
WIKI_ATTACHMENTS_MAX = getattr(settings, 'SIMPLE_WIKI_ATTACHMENTS_MAX',
                               1 * 1024 * 1024)
WIKI_ALLOW_ATTACHMENTS      = getattr(settings, 'WIKI_ALLOW_ATTACHMENTS', True)

WIKI_ALLOW_ANON_ATTACHMENTS = getattr(settings, 'WIKI_ALLOW_ANON_ATTACHMENTS', False)
WIKI_ALLOW_ANON_READ        = getattr(settings, 'WIKI_ALLOW_ANON_READ', True)
WIKI_ALLOW_ANON_WRITE       = getattr(settings, 'WIKI_ALLOW_ANON_WRITE', True)

# Planned feature.
WIKI_USE_MARKUP_WIDGET = True

