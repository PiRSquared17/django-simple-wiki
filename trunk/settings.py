from django.utils.translation import ugettext_lazy as _
from django.conf import settings

# Default settings.. overwrite in your own settings.py

# Base URL of wiki... with NO trailing slash. Not that it's harmful,
# which is exactly the reason for leaving it out... so that in the
# rest of the program we just assume it isn't there. No parsing or
# anything.
WIKI_BASE = getattr(settings, 'SIMPLE_WIKI_BASE', '/wiki')
WIKI_ATTACHMENTS = getattr(settings, 'SIMPLE_WIKI_ATTACHMENTS', 'simplewiki/attachments/')

# Bytes! Default: 1 MB
WIKI_ATTACHMENTS_MAX = getattr(settings, 'SIMPLE_WIKI_ATTACHMENTS_MAX', 1 * 1024 * 1024)

# Don't modify.. breaks compatibility with standard Django libs..
WIKI_ATTACHMENTS_ROOT = settings.MEDIA_ROOT

# TODO: Put all this rubbish in a proper template
WIKI_ERR_NOTFOUND = getattr(settings, 'SIMPLE_WIKI_ERR_NOTFOUND',
                            _("The page you requested could not be found. "
                              "Click <a href=""%(base)s/%(url)s/create"">here</a> to create it."))
WIKI_ERR_CREATE_PARENT = getattr(settings, 'SIMPLE_WIKI_ERR_CREATE_PARENT',
                                 _("You cannot create this page, because it's parent "
                                   "does not exist. Click "
                                   "<a href=""%(base)s/%(url)s/create"">here</a> to create it."))
WIKI_ERR_LOCKED = getattr(settings, 'SIMPLE_WIKI_ERR_LOCKED',
                          _("The article you are trying to modify is locked."))

WIKI_ERR_NOREAD = getattr(settings, 'SIMPLE_WIKI_ERR_NOREAD',
                          _("You do not have access to read this article."))

WIKI_ERR_NOEDIT = getattr(settings, 'SIMPLE_WIKI_ERR_NOEDIT',
                           _("You do not have access to edit this article."))

WIKI_ERR_NOCREATE = getattr(settings, 'SIMPLE_WIKI_ERR_NOCREATE',
                            _("You do not have access to create this article."))

WIKI_ERR_ENCODE = getattr(settings, 'SIMPLE_WIKI_ERR_ENCODE',
                          _("The url you requested could not be handled by the wiki. "
                            "Probably you used a bad character in the URL. "
                            "Only use digits, English letters, underscore and dash. For instance "
                            "/wiki/An_Article-1"))

WIKI_USE_MARKUP_WIDGET = True