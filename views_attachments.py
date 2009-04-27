from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, Context
from django.db.models.fields.files import FieldFile
from django.core.servers.basehttp import FileWrapper
from models import Article, ArticleAttachment, get_attachment_filepath
from views import not_found, check_permissions, get_url_path
import os
from settings import *

def add_attachment(request, wiki_url):

    url_path = get_url_path(wiki_url)
    path = Article.get_url_reverse(url_path, Article.get_root())
    if not path:
        return not_found(request, '/'.join(url_path))

    article = path[-1]
    
    perm_err = check_permissions(request, article, check_write=True, errormsg=WIKI_ERR_NOEDIT)
    if perm_err:
        return perm_err
    
    if request.method == 'POST':
        if request.FILES.__contains__('attachment'):
            
            attachment = ArticleAttachment()
            attachment.uploaded_by = request.user
            attachment.article = article

            file = request.FILES['attachment']
            file_rel_path = get_attachment_filepath(attachment, file.name)
            chunk_size = request.upload_handlers[0].chunk_size

            filefield = FieldFile(attachment, attachment.file, file_rel_path)
            attachment.file = filefield
            
            file_path = WIKI_ATTACHMENTS_ROOT + attachment.file.name

            if not request.POST.__contains__('overwrite') and os.path.exists(file_path):
                c = Context({'overwrite_warning' : True,
                             'wiki_article': article,
                             'filename': file.name})
                t = loader.get_template('simplewiki_updateprogressbar.html')
                return HttpResponse(t.render(c))

            if file.size > WIKI_ATTACHMENTS_MAX:
                c = Context({'too_big' : True,
                             'max_size': WIKI_ATTACHMENTS_MAX,
                             'wiki_article': article,
                             'file': file})
                t = loader.get_template('simplewiki_updateprogressbar.html')
                return HttpResponse(t.render(c))
                

            # Remove existing attachments
            # TODO: Move this until AFTER having removed file.
            # Current problem is that Django's FileField delete() method
            # automatically deletes files
            for a in article.attachments():
                if file_rel_path == a.file.name:
                    print file_rel_path
                    a.delete()
            def receive_file():
                destination = open(file_path, 'wb+')
                size = file.size
                cnt = 0
                c = Context({'started' : True,})
                t = loader.get_template('simplewiki_updateprogressbar.html')
                yield t.render(c)
                for chunk in file.chunks():
                    cnt += 1
                    destination.write(chunk)
                    c = Context({'progress_width' : (cnt*chunk_size) / size,
                                 'wiki_article': article,})
                    t = loader.get_template('simplewiki_updateprogressbar.html')
                    yield t.render(c)
                c = Context({'finished' : True,
                             'wiki_article': article,})
                t = loader.get_template('simplewiki_updateprogressbar.html')
                destination.close()
                attachment.save()
                yield t.render(c)
    
            return HttpResponse(receive_file())
    
    return HttpResponse('')

# Taken from http://www.djangosnippets.org/snippets/365/
def send_file(request, filepath):
    """                                                                         
    Send a file through Django without loading the whole file into              
    memory at once. The FileWrapper will turn the file object into an           
    iterator for chunks of 8KB.                                                 
    """
    filename =  filepath
    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, content_type='text/plain')
    response['Content-Length'] = os.path.getsize(filename)
    return response

def view_attachment(request, wiki_url, file_name):
    
    url_path = get_url_path(wiki_url)
    path = Article.get_url_reverse(url_path, Article.get_root())
    if not path:
        return not_found(request, '/'.join(url_path))

    article = path[-1]
    
    perm_err = check_permissions(request, article, check_read=True, errormsg=WIKI_ERR_NOEDIT)
    if perm_err:
        return perm_err
    
    attachment = None
    for a in article.attachments():
        if get_attachment_filepath(a, file_name) == a.file.name:
            attachment = a
    
    if attachment:
        filepath = WIKI_ATTACHMENTS_ROOT + attachment.file.name
        if os.path.exists(filepath):
            return send_file(request, filepath)
    return not_found(request, '/'.join(url_path))
    
