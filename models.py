from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models import signals
from django.contrib.auth.models import User
from markdown import markdown
from django import forms
from django.core.urlresolvers import reverse
import difflib
import os
from settings import *

class ShouldHaveExactlyOneRootSlug(Exception):
    pass

class Article(models.Model):
    """Wiki article referring to Revision model for actual content.
       'slug' and 'parent' field should be maintained centrally, since users
       aren't allowed to change them, anyways.
    """
    
    title = models.CharField(max_length=512, verbose_name=_('Article title'),
                             blank=False)
    slug = models.SlugField(max_length=100, verbose_name=_('slug'),
                            help_text=_('Letters, numbers, underscore and hyphen.'
                                        ' Do not use reserved words \'create\','
                                        ' \'history\' and \'edit\'.'),
                            blank=True)
    created_by = models.ForeignKey(User, verbose_name=_('Created by'), blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add = 1)
    modified_on = models.DateTimeField(auto_now_add = 1)
    parent = models.ForeignKey('self', verbose_name=_('Parent article slug'), 
                               help_text=_('Affects URL structure and possibly inherits permissions'),
                               null=True, blank=True)
    locked = models.BooleanField(default=False, verbose_name=_('Locked for editing'))
    permissions = models.ForeignKey('Permission', verbose_name=_('Permissions'),
                                    blank=True, null=True,
                                    help_text=_('Permission group'))
    current_revision = models.OneToOneField('Revision', related_name='current_rev',
                                            blank=True, null=True, editable=True)
    related = models.ManyToManyField('self', verbose_name=_('Related articles'), symmetrical=True,
                                     help_text=_('Sets a symmetrical relation other articles'),
                                     blank=True, null=True)

    def attachments(self):
        return ArticleAttachment.objects.filter(article__exact = self)

    @classmethod
    def get_root(cls):
        """Return the root article, which should ALWAYS exist..
        except the very first time the wiki is loaded, in which
        case the user is prompted to create this article."""
        try:
            return Article.objects.get(slug__exact = '', parent__exact = None)
        except:
            raise ShouldHaveExactlyOneRootSlug()

    def get_url(self):
        """Return the Wiki URL for an article"""
        if self.parent:
            return self.parent.get_url() + '/' + self.slug
        else:
            return self.slug

    def get_abs_url(self):
        """Return the absolute path for an article. This is necessary in cases
        where the template system isn't used for generating URLs..."""
        # TODO: Remove and create a reverse() lookup.
        return WIKI_BASE + self.get_url()

    @classmethod
    def get_url_reverse(cls, path, article, return_list=[]):
        """Lookup a URL and return the corresponding set of articles
        in the path."""
        if path == []:
            return return_list + [article]
        # Lookup next child in path
        try:
            a = Article.objects.get(parent__exact = article, slug__exact=str(path[0]))
            return cls.get_url_reverse(path[1:], a, return_list+[article])
        except Exception, e:
            print article.id, path[0], e
            return None
    
    def can_read(self, user):
        """ Check read permissions and return True/False."""
        if self.permissions:
            perms = self.permissions.can_read.all()
            return perms.count() == 0 or perms.filter(read__exact = user.id).count() > 0
        else:
            return self.parent.can_read(user) if self.parent else True

    def can_write(self, user):
        """ Check write permissions and return True/False."""
        if self.permissions:
            perms = self.permissions.can_write.all()
            return perms.count() == 0 or perms.filter(write__exact = user.id).count() > 0
        else:
            return self.parent.can_write(user) if self.parent else True

    def can_write_l(self, user):
        """Check write permissions and locked status"""
        return not self.locked and self.can_write(user)

    def __unicode__(self):
        if self.slug == '' and not self.parent:
            return unicode(_('Root article'))
        else:
            return self.get_url()
    
    class Meta:
        unique_together = (('slug', 'parent'),)
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')

def get_attachment_filepath(instance, filename):
    """Store file, appending new extension for added security"""
    dir_ = WIKI_ATTACHMENTS + instance.article.get_url()
    dir_ = '/'.join(filter(lambda x: x!='', dir_.split('/')))
    if not os.path.exists(WIKI_ATTACHMENTS_ROOT + dir_):
        os.makedirs(WIKI_ATTACHMENTS_ROOT + dir_)
    return dir_ + '/' + filename + '.upload'

class ArticleAttachment(models.Model):
    article = models.ForeignKey(Article, verbose_name=_('Article'))
    file = models.FileField(max_length=255, upload_to=get_attachment_filepath, verbose_name=_('Attachment'))
    uploaded_by = models.ForeignKey(User, blank=True, verbose_name=_('Uploaded by'))
    uploaded_on = models.DateTimeField(auto_now_add = True, verbose_name=_('Upload date'))
    
    def download_url(self):
        return reverse('wiki_view_attachment', args=(self.article.get_url(), self.filename()))
    
    def filename(self):
        return '.'.join(self.file.name.split('/')[-1].split('.')[:-1])
    
    def __unicode__(self):
        return self.filename()
    
class Revision(models.Model):
    
    article = models.ForeignKey(Article, verbose_name=_('Article'))
    revision_text = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Description of change'))
    revision_user = models.ForeignKey(User, verbose_name=_('Modified by'), blank=True, null=True)
    revision_date = models.DateTimeField(auto_now_add = True, verbose_name=_('Revision date'))
    contents = models.TextField(verbose_name=_('Contents (Use MarkDown format)'))
    contents_parsed = models.TextField(editable=False, blank=True, null=True)
    counter = models.IntegerField(verbose_name=_('Revision#'), default=1, editable=False)
    previous_revision = models.OneToOneField('self', related_name='previous_rev',
                                            blank=True, null=True, editable=False)
    
    def get_user(self):
        return self.revision_user if self.revision_user else _('Anonymous')
    
    def save(self, **kwargs):
        # Check if contents have changed... if not, silently ignore save
        if self.article and self.article.current_revision and self.article.current_revision.contents == self.contents:
            return
        # Increment counter according to previous revision
        previous_revision = Revision.objects.filter(article__exact=self.article).order_by('-counter')
        if previous_revision:
            self.counter = previous_revision[0].counter + 1
        else:
            self.counter = 1
        self.previous_revision = self.article.current_revision
        # Create pre-parsed contents - no need to parse on-the-fly
        self.contents_parsed = markdown(self.contents,
                                        extensions=['footnotes',
                                                    "wikilinks(base_url=%s/)" % WIKI_BASE, 
                                                    'tables', 'headerid',
                                                    'fenced_code', 'def_list',
                                                    'codehilite', 'abbr','toc'],
                                        safe_mode='escape',)
        super(Revision, self).save(**kwargs)
        
    def delete(self, **kwargs):
        """If a current revision is deleted, then regress to the previous
        revision or insert a stub, if no other revisions are available"""
        article = self.article
        if article.current_revision == self:
            prev_revision = Revision.objects.filter(article__exact = article,
                                                    pk__not = self.pk).order_by('-counter')
            if prev_revision:
                article.current_revision = prev_revision[0]
                article.save()
            else:
                r = Revision(article=article, 
                             revision_user = article.created_by)
                r.contents = unicode(_('Auto-generated stub'))
                r.revision_text= unicode(_('Auto-generated stub'))
                r.save()
                article.current_revision = r
                article.save()
        super(Revision, self).delete(**kwargs)
    
    def get_diff(self):
        if self.previous_revision:
            previous = self.previous_revision.contents.splitlines(1)
        else:
            previous = []
        diff = difflib.ndiff(previous, self.contents.splitlines(1))
        for d in diff:
            yield d
    
    def __unicode__(self):
        return "r%d" % self.counter

    class Meta:
        unique_together = (('article', 'counter'),)
        verbose_name = _('article revision')
        verbose_name_plural = _('article revisions')

class Permission(models.Model):
    permission_name = models.CharField(max_length = 255, verbose_name=_('Permission name'))
    can_write = models.ManyToManyField(User, blank=True, null=True, related_name='write',
                                       help_text=_('Select none to grant anonymous access.'))
    can_read = models.ManyToManyField(User, blank=True, null=True, related_name='read',
                                       help_text=_('Select none to grant anonymous access.'))
    def __unicode__(self):
        return self.permission_name
    class Meta:
        verbose_name = _('Article permission')
        verbose_name_plural = _('Article permissions')

class RevisionForm(forms.ModelForm):
    contents = forms.CharField(label=_('Contents'), widget=forms.Textarea(attrs={'rows':8, 'cols':50}))
    class Meta:
        model = Revision
        fields = ['contents', 'revision_text']
class CreateArticleForm(RevisionForm):
    title = forms.CharField(label=_('Title'))
    class Meta:
        model = Revision
        fields = ['title', 'contents',]

def set_revision(sender, *args, **kwargs):
    """Signal handler to ensure that a new revision is always chosen as the
    current revision - automatically. It simplifies stuff greatly. Also
    stores previous revision for diff-purposes"""
    instance = kwargs['instance']
    created = kwargs['created']
    if created and instance.article:
        instance.article.current_revision = instance
        instance.article.save()

signals.post_save.connect(set_revision, Revision)