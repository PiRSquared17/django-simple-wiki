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

# Planned feature.
WIKI_USE_MARKUP_WIDGET = True