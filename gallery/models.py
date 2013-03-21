# ------------------------------------------------------------------------
# coding=utf-8
# ------------------------------------------------------------------------
#
#  Created by Martin J. Laubach on 2013-03-20
#  Copyright (c) 2013 Martin J. Laubach. All rights reserved.
#
# ------------------------------------------------------------------------

from __future__ import absolute_import

import logging

from django.contrib import admin
from django.db import models
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from feincms.module.medialibrary.models import MediaFile

from .admin import MediaGalleryAdminBase, MediaGalleryContentFilesAdminInlineBase

# ------------------------------------------------------------------------
app_label = 'mediagallery'
logger = logging.getLogger(app_label)

# ------------------------------------------------------------------------
class MediaGalleryContent(models.Model):
    class Meta:
        abstract            = True
        verbose_name        = _('media gallery')
        verbose_name_plural = _('media galleries')

    LAYOUT_CHOICES = ( ('', _('default list')), )

    title   = models.CharField(_('title'), max_length=80, blank=True)
    options = models.CharField(_('options'), max_length=80, blank=True)

    @classmethod
    def initialize_type(cls, LAYOUT_CHOICES=None):
        if LAYOUT_CHOICES is None:
            LAYOUT_CHOICES = ( ('default', _('default gallery')), )

        cls.add_to_class('layout', models.CharField(_('layout'),
                         choices=LAYOUT_CHOICES, max_length=15,
                         default=LAYOUT_CHOICES[0][0],)
        )

        class MediaGalleryContentFiles(models.Model):
            class Meta:
                app_label           = cls._meta.app_label
                unique_together     = (('gallery', 'mediafile'), )
                verbose_name        = _('media gallery content file')
                verbose_name_plural = _('media gallery content files')
                ordering            = ('ordering',)

            gallery   = models.ForeignKey(cls, related_name="item_set")
            mediafile = models.ForeignKey(MediaFile, related_name="+")
            ordering  = models.IntegerField(default=0)
            title     = models.CharField(_('title'), blank=True, max_length=80)
            text      = models.TextField(_('text'), blank=True)

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

        class MediaGalleryContentFilesAdminInline(MediaGalleryContentFilesAdminInlineBase):
            model = MediaGalleryContentFiles

        class MediaGalleryAdmin(MediaGalleryAdminBase):
            inlines = (MediaGalleryContentFilesAdminInline,)

        admin.site.register(MediaGalleryContentFiles) # REMOVE THIS LATER
        admin.site.register(cls, MediaGalleryAdmin)

    def __unicode__(self):
        return self.title

    def items(self):
        return self.item_set.all()

    def render(self, request, **kwargs):
        return render_to_string((
                'content/media-gallery/content-%s.html' % self.layout,
                'content/media-gallery/content.html',
            ),
            { 'feincms_page': self.parent, 'object': self, 'gallery': self, },
            context_instance=RequestContext(request)
            )

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
