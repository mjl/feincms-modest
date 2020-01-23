# coding=utf-8
# ------------------------------------------------------------------------
#  Created by Martin J. Laubach on 2013-03-20
#  Copyright (c) 2013 Martin J. Laubach. All rights reserved.
# ------------------------------------------------------------------------

from __future__ import absolute_import

import json
import logging
try:
    from urllib.parse import urlparse
except ImportError:  # py2
    from urlparse import urlparse

from django.conf import settings
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
try:
    from django.urls import reverse
except ImportError:  # dj 1.x
    from django.core.urlresolvers import reverse

from django.db import models
from django.http import HttpResponse, HttpResponseNotFound
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _

from feincms.admin.item_editor import FeinCMSInline
from feincms.module.medialibrary.models import MediaFile
from feincms.module.medialibrary.thumbnail import admin_thumbnail

from .admin import MediaGalleryAdminBase, MediaGalleryContentFilesAdminInlineBase

# ------------------------------------------------------------------------
app_label = 'mediagallery'
logger = logging.getLogger(app_label)

# ------------------------------------------------------------------------
class MediaGalleryContentAdminInline(FeinCMSInline):
    template = "admin/modest_content_inline.html"

class MediaGalleryContent(models.Model):

    class Meta:
        abstract = True
        verbose_name = _('media gallery')
        verbose_name_plural = _('media galleries')

    template_prefix = 'content/modest/'

    LAYOUT_CHOICES = (('', _('default list')), )
    ORDER_CHOICES = (('', _('ascending')),
                     ('-', _('descending')),
                     ('?', _('random')))
    CLICK_CHOICES = (('', _('do nothing')),
                     ('R', _('redirect to page')),
                     ('Z', _('zoom image')))

    # ----- django fields ----- #
    title = models.CharField(_('title'), max_length=80, blank=True)
    options = models.CharField(_('options'), max_length=80, blank=True)

    order = models.CharField(_('order'), max_length=1, blank=True,
                    choices=ORDER_CHOICES)
    limit = models.SmallIntegerField(_('limit'), blank=True, null=True,
                    help_text=_('show how many items, leave empty for no limit')
    )
    click = models.CharField(_('on click'), max_length=1, blank=True,
                    choices=CLICK_CHOICES)

    # Implement admin_urlname templatetag protocol
    @property
    def app_label(self):
        return self._meta.app_label

    # Implement admin_urlname templatetag protocol
    @property
    def module_name(self):
        return self.__class__.__name__.lower()

    @classmethod
    def initialize_type(cls,
                        LAYOUT_CHOICES=None,
                        DROP_ACCEPTOR=None,
                        EXTRA_CONTEXT=None,
                        MEDIA_DEFS=None,
                        ITEM_CLASS=MediaFile):
        if LAYOUT_CHOICES is None:
            LAYOUT_CHOICES = (('default', _('default gallery')), )

        cls.add_to_class('layout', models.CharField(_('layout'),
                         choices=LAYOUT_CHOICES, max_length=15,
                         default=LAYOUT_CHOICES[0][0],)
        )
        cls.extra_context = EXTRA_CONTEXT
        cls.media_defs = MEDIA_DEFS

        cls.feincms_item_editor_inline = MediaGalleryContentAdminInline

        class MediaGalleryContentFiles(models.Model):

            class Meta:
                app_label = cls._meta.app_label
                unique_together = (('gallery', 'mediafile'), )
                verbose_name = _('media gallery content file')
                verbose_name_plural = _('media gallery content files')
                ordering = ('ordering',)

            gallery = models.ForeignKey(cls, related_name="item_set",
                                on_delete=models.CASCADE)
            mediafile = models.ForeignKey(ITEM_CLASS, related_name="+",
                                on_delete=models.CASCADE)
            related_page = models.ForeignKey(cls._feincms_content_class,
                                verbose_name=_('related page'),
                                blank=True, null=True,
                                related_name="+", on_delete=models.SET_NULL)

            ordering = models.IntegerField(default=0)
            title = models.CharField(_('title'), blank=True, max_length=80)
            text = models.TextField(_('text'), blank=True)

            def __unicode__(self):
                return u'Media Gallery %s - %s' % (self.gallery, self.mediafile)

            def caption(self):
                if self.title:
                    return self.title
                if self.mediafile and self.mediafile.translation:
                    return self.mediafile.translation.caption
                return ""

            def description(self):
                if self.text:
                    return self.text
                if self.mediafile and self.mediafile.translation:
                    return self.mediafile.translation.description
                return ""

            def copyright(self):
                return self.mediafile.copyright

            def file(self):
                return self.mediafile.file

        if DROP_ACCEPTOR is None:
            DROP_ACCEPTOR = MediaGalleryDropAcceptor()

        class MediaGalleryContentFilesAdminInline(MediaGalleryContentFilesAdminInlineBase):
            model = MediaGalleryContentFiles

        class MediaGalleryAdmin(MediaGalleryAdminBase):
            inlines = (MediaGalleryContentFilesAdminInline,)

        MediaGalleryAdmin.drop_acceptor = DROP_ACCEPTOR

        admin.site.register(cls, MediaGalleryAdmin)

    @property
    def media(self):
        return self.media_defs.get(self.layout, None)

    def __unicode__(self):
        return self.title

    def items(self):
        qs = self.item_set

        m = {'-': '-ordering', '?': '?'}
        qs = qs.order_by(m.get(self.order, 'ordering'))

        if self.limit:
            qs = qs[:self.limit]

        return qs.all()

    def render(self, request, **kwargs):
        ctx = {'have_icon_files': ('pdf', 'zip')}

        if self.extra_context is not None:
            if callable(self.extra_context):
                ctx = self.extra_context()
            else:
                ctx = dict(self.extra_context())

        ctx.update({'feincms_page': self.parent, 'object': self, 'gallery': self})

        return render_to_string((
            '%scontent-%s.html' % (self.template_prefix, self.layout),
            '%scontent.html' % (self.template_prefix),
        ), ctx, request=request)

    # Accessor for admin_url templatetag
    def parent_opts(self):
        return self.parent._meta

    def opts(self):
        return self._meta

# ------------------------------------------------------------------------
class MediaGalleryDropAcceptor(object):

    def __init__(self, *args, **kwargs):
        self.mediaurl = urlparse(settings.MEDIA_URL)
        self.mediachange_url = None  # deferred until init is done

    def reverse_url(self, request, url, ctx):
        """
        This takes what url the user dropped onto the drop zone and
        tries to intuit what she meant. Currently implements dropping
        a MediaLibrary item (see below, `mediafile_reverse_url`), but
        could be extended to handle Pages or Products from a catalogue.

        This method takes the url and fills out the context dictionary
        as it seems fit.

        Override to this to customize.
        """
        return self.mediafile_reverse_url(url, ctx)

    @method_decorator(staff_member_required)
    def __call__(self, request):
        if not request.is_ajax():
            return HttpResponseNotFound()

        # Delayed init, url dict is not ready in __init__
        if self.mediachange_url is None:
            self.mediachange_url = reverse("admin:medialibrary_mediafile_change", args=(0,)).replace('0/', '')

        out = {'status': 404}
        inurl = request.REQUEST.get('url')
        try:
            url = urlparse(inurl)
            # Security check: only allow urls that come from this site
            if self.is_valid_drop_url(request, url):
                self.reverse_url(request, url, out)
        except Exception as e:
            logger.exception("%s raised exception for url \"%s\": %s", self.__class__.__name__, inurl, e)
            out['status'] = 500

        return self.build_response(out)

    def build_response(self, ctx):
        r = HttpResponse(json.dumps(ctx), content_type='application/json')
        r.status_code = ctx['status']
        return r

    def is_valid_drop_url(self, request, url):
        return url.netloc == request.META.get('HTTP_HOST', None)

    def mediafile_reverse_url(self, url, ctx):
        """
        Tries to intuit what the user dropped onto us. This might be
        a link to a MediaFile in case she dragged the "Title" column
        over, or it might be a link to a file in the media library
        if she dragged the image itself.
        """
        mediafile = None

        try:
            if url.path.startswith(self.mediachange_url):
                # Dropped a MediaFile url
                rest = url.path[len(self.mediachange_url):-1]
                mediafile = MediaFile.objects.get(pk=int(rest))
            elif url.path.startswith(self.mediaurl.path):
                # Dropped an image url (from media library)
                file_path = url.path[len(self.mediaurl.path):]
                mediafile = MediaFile.objects.get(file=file_path)
        except MediaFile.DoesNotExist:
            pass
        else:
            if mediafile is not None:
                logger.debug("%s converted \"%s\" into %s(pk=%d)",
                             self.__class__.__name__, url.path, mediafile.__class__.__name__, mediafile.pk)

                image = admin_thumbnail(mediafile, dimensions="150x100")

                ctx['mediafile_id'] = mediafile.id
                ctx['mediafile_type'] = mediafile.type
                ctx['mediafile_caption'] = unicode(mediafile)
                ctx['mediafile_url'] = image
                ctx['status'] = 200

# ------------------------------------------------------------------------
