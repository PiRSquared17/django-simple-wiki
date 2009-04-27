# Create your views here.
from models import Article, Revision, RevisionForm, ShouldHaveExactlyOneRootSlug, CreateArticleForm
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseServerError, HttpResponseForbidden, HttpResponseNotAllowed
from django.utils import simplejson
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, Context, loader
from django.utils.translation import ugettext_lazy as _

from settings import *

def view(request, wiki_url):
    
    # Main page cannot be created, but is auto-populated
    # on syncdb
    try:
        root = Article.get_root()
    except:
        return not_found(request, wiki_url)

    url_path = get_url_path(wiki_url)

    path = Article.get_url_reverse(url_path, root)
    if not path:
        return not_found(request, '/'.join(url_path))
    article = path[-1]
    
    perm_err = check_permissions(request, article, check_read=True, errormsg=WIKI_ERR_NOREAD)
    if perm_err:
        return perm_err
    
    return render_to_response('simplewiki_view.html',
                              RequestContext(request, {'wiki_article': article,
                                                       'wiki_write': article.can_write_l(request.user),
                                                       'base': WIKI_BASE,} ) )

def create(request, wiki_url):
    
    url_path = get_url_path(wiki_url)

    # Lookup path
    import models
    try:
        # Ensure that the path exists...
        root = Article.get_root()
        path = Article.get_url_reverse(url_path[:-1], root)
        if not path:
            # TODO: Should have a message that the parent does not exist
            return not_found(request, wiki_url)
        perm_err = check_permissions(request, path[-1], check_locked=False, check_write=True, errormsg=WIKI_ERR_NOCREATE)
        if perm_err:
            return perm_err
        # Ensure doesn't already exist
        article = Article.get_url_reverse(url_path, root)
        if article:
            return HttpResponseRedirect(WIKI_BASE + article[-1].get_url())
    # TODO: Somehow this doesnt work... 
    #except ShouldHaveExactlyOneRootSlug, (e):
    except:
        # Root not found...
        path = []
        url_path = [""]

    if request.method == 'POST':
        f = CreateArticleForm(request.POST)
        if f.is_valid():
            article = Article()
            article.slug = url_path[-1]
            if not request.user.is_anonymous():
                article.created_by = request.user
            article.title = f.cleaned_data['title']
            if path != []:
                article.parent = path[-1]
            a = article.save()
            new_revision = f.save(commit=False)
            if not request.user.is_anonymous():
                new_revision.revision_user = request.user
            new_revision.article = article
            new_revision.save()
            import django.db as db
            return HttpResponseRedirect(WIKI_BASE + article.get_url())
    else:
        f = CreateArticleForm({'title':url_path[-1], 'contents':'Headline\n==='})
        
    c = RequestContext(request, {'wiki_form': f,
                                 'wiki_write': True,
                                 })

    return render_to_response('simplewiki_create.html', c)

def edit(request, wiki_url):

    url_path = get_url_path(wiki_url)

    # Lookup article
    path = Article.get_url_reverse(url_path, Article.get_root())

    if not path:
        return not_found(request, '/'.join(url_path))

    article = path[-1]

    # Check write permissions
    perm_err = check_permissions(request, article, check_write=True, errormsg=WIKI_ERR_NOEDIT)
    if perm_err:
        return perm_err

    # Is locked?
    if article.locked:
        err_msg = WIKI_ERR_LOCKED % {'url' : '/'.join(url_path), 'base': WIKI_BASE}
        return render_to_response('simplewiki_error.html',
                                  RequestContext(request, {'wiki_error': err_msg}))

    if request.method == 'POST':
        f = RevisionForm(request.POST)
        if f.is_valid():
            new_revision = f.save(commit=False)
            new_revision.article = article
            # Check that something has actually been changed...
            if new_revision.get_diff() == []:
                return HttpResponseRedirect(WIKI_BASE + article.get_url())
            if not request.user.is_anonymous():
                new_revision.revision_user = request.user
            new_revision.save()
            return HttpResponseRedirect(WIKI_BASE + article.get_url())
    else:
        f = RevisionForm({'contents': article.current_revision.contents})
    c = RequestContext(request, {'wiki_form': f,
                                 'wiki_write': True,
                                 'wiki_article': article})

    return render_to_response('simplewiki_edit.html', c)

def history(request, wiki_url, page=1):
    url_path = get_url_path(wiki_url)
    # Lookup article
    path = Article.get_url_reverse(url_path, Article.get_root())
    if not path:
        return not_found(request, '/'.join(url_path))

    article = path[-1]

    perm_err = check_permissions(request, article, check_read=True, errormsg=WIKI_ERR_NOEDIT)
    if perm_err:
        return perm_err

    page_size = 10
    
    try:
        p = int(page)
    except ValueError:
        p = 1
   
    history = Revision.objects.filter(article__exact = article).order_by('-counter')
    
    if request.method == 'POST':
        if request.POST.__contains__('revision'):
            perm_err = check_permissions(request, article, check_write=True, errormsg=WIKI_ERR_NOEDIT)
            if perm_err:
                return perm_err
            try:
                r = int(request.POST['revision'])
                article.current_revision = Revision.objects.get(id=r)
                article.save()
            except:
                pass
            finally:
                return HttpResponseRedirect(article.get_abs_url())
    
    page_count = (history.count()+(page_size-1)) / page_size
    if p > page_count:
        p = 1
    beginItem = (p-1) * page_size
    
    next_page = p + 1 if page_count > p else None
    prev_page = p - 1 if p > 1 else None
    
    c = RequestContext(request, {'wiki_page': p,
                                 'wiki_next_page': next_page,
                                 'wiki_prev_page': prev_page,
                                 'wiki_write': article.can_write_l(request.user),
                                 'wiki_article': article,
                                 'wiki_history': history[beginItem:beginItem+page_size],})

    return render_to_response('simplewiki_history.html', c)

def search_add_related(request, wiki_url):
    url_path = get_url_path(wiki_url)
    # Lookup article
    path = Article.get_url_reverse(url_path, Article.get_root())
    if not path:
        return not_found(request, '/'.join(url_path))

    article = path[-1]

    perm_err = check_permissions(request, article, check_read=True, errormsg=WIKI_ERR_NOEDIT)
    if perm_err:
        return perm_err

    if request.GET.__contains__('query'):
        search_string = request.GET['query']
        related = Article.objects.filter(title__istartswith = search_string)
        if related:
            related = related.exclude(related__in = article.related.all()).order_by('title')[:10]
        results = []
        for item in related:
            results.append({'id': str(item.id),
                            'value': item.title,
                            'info': item.get_url()})
    else:
        results = []
    
    json = simplejson.dumps({'results': results})
    return HttpResponse(json, mimetype='application/json')

def add_related(request, wiki_url):
    url_path = get_url_path(wiki_url)
    # Lookup article
    path = Article.get_url_reverse(url_path, Article.get_root())
    if not path:
        return not_found(request, '/'.join(url_path))

    article = path[-1]
    
    perm_err = check_permissions(request, article, check_write=True, errormsg=WIKI_ERR_NOEDIT)
    if perm_err:
        return perm_err
    
    try:
        related_id = request.POST['id']
        rel = Article.objects.get(id=related_id)
        has_already = article.related.filter(id=related_id).count()
        if has_already == 0:
            article.related.add(rel)
            article.save()
    except:
        pass
    finally:
        return HttpResponseRedirect(WIKI_BASE + article.get_url())

def remove_related(request, wiki_url, remove_url):
    url_path = get_url_path(wiki_url)
    # Lookup article
    path = Article.get_url_reverse(url_path, Article.get_root())
    if not path:
        return not_found(request, '/'.join(url_path))

    # Lookup relation
    rel_url_path = get_url_path(remove_url)
    rel_path = Article.get_url_reverse(rel_url_path, Article.get_root())
    if not rel_path:
        return not_found(request, '/'.join(rel_url_path))

    article = path[-1]
    relation = rel_path[-1]

    # Only require write permission on
    # one of the articles... otherwise the whole thing
    # explodes in complexity
    perm_err = check_permissions(request, article, check_write=True, errormsg=WIKI_ERR_NOEDIT)
    if perm_err:
        return perm_err
    try:
        article.related.remove(relation)
        article.save()
    except:
        pass
    finally:
        return HttpResponseRedirect(WIKI_BASE + article.get_url())

def encode_err(request, url):
    err_msg = WIKI_ERR_ENCODE % {'url' : url, 'base': WIKI_BASE}
    return render_to_response('simplewiki_error.html',
                              RequestContext(request, {'wiki_error': err_msg}))
    
def not_found(request, wiki_url):
    """Generate a NOT FOUND message for some URL"""
    err_msg = WIKI_ERR_NOTFOUND % {'url' : wiki_url, 'base': WIKI_BASE}
    return render_to_response('simplewiki_error.html',
                              RequestContext(request, {'wiki_error': err_msg}))

def get_url_path(url):
    """Return a list of all actual elements of a url, safely ignoring
    double-slashes (//) """
    return filter(lambda x: x!='', url.split('/'))

def check_permissions(request, article, check_read=False, check_write=False, errormsg="Perm err", check_locked=True):
    err = False
    if check_read:
        err = not article.can_read(request.user)
    if check_write and check_locked:
        err = err or not article.can_write_l(request.user)
    if check_write and not check_locked:
        err = err or not article.can_write(request.user)
    if err:
        return render_to_response('simplewiki_error.html',
                                  RequestContext(request, {'wiki_error': errormsg}))
    else:
        return None

            