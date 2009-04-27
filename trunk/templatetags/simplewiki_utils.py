from django import template
from django.template.defaultfilters import stringfilter
from simplewiki.settings import *
from django.conf import settings

@stringfilter
def prepend_media_url(value):
    """Prepend user defined media root to url"""
    return settings.MEDIA_URL + value

def prepend_wiki_url(value):
    return WIKI_BASE + '/' + value

register = template.Library()
register.filter('prepend_media_url', prepend_media_url)
register.filter('prepend_wiki_url', prepend_wiki_url)
