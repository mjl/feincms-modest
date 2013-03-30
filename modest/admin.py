# ------------------------------------------------------------------------
# coding=utf-8
# ------------------------------------------------------------------------
#
#  Created by Martin J. Laubach on 2013-03-21
#  Copyright (c) 2013 Martin J. Laubach. All rights reserved.
#
# ------------------------------------------------------------------------

from __future__ import absolute_import

from django.conf.urls import patterns, url
from django.contrib import admin
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.utils.safestring import mark_safe

from feincms.module.medialibrary.models import MediaFile
from feincms.module.medialibrary.thumbnail import admin_thumbnail

# ------------------------------------------------------------------------
class MediaFileWidget(ForeignKeyRawIdWidget):
    def render(self, name, value, attrs=None):
        html = super(MediaFileWidget, self).render(name, value, attrs)

        if value:
            try:
                id = int(value)
                mf = MediaFile.objects.get(pk=id)
            except (MediaFile.DoesNotExist, ValueError):
                return html

            image = admin_thumbnail(mf, dimensions="150x100")
            if image:
                image = u'<img class="image-preview" src="%(url)s" />' % {'url': image}
                html = html + image
                return mark_safe(html)

        return html

# ------------------------------------------------------------------------
class MediaGalleryContentFilesAdminInlineBase(admin.TabularInline):
    ordering = ('ordering',)
    raw_id_fields = ('mediafile', 'related_page')
    fields = ('mediafile', 'title', 'text', 'related_page', 'ordering')
    extra = 1

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(MediaGalleryContentFilesAdminInlineBase, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'mediafile':
            formfield.widget = MediaFileWidget(formfield.widget.rel,
                    formfield.widget.admin_site,
                    attrs=formfield.widget.attrs,
                    using=formfield.widget.db)

        return formfield

# ------------------------------------------------------------------------
class MediaGalleryAdminBase(admin.ModelAdmin):
    list_display = ('title', 'page')
    exclude = ('ordering', 'region', 'parent')
    drop_acceptor = None

    def page(self, object):
        return object.parent

    def has_add_permission(self, request):
        return False

    def get_urls(self):
        urls = super(MediaGalleryAdminBase, self).get_urls()
        my_urls = patterns('',
            url(r'^reverse-url/$', self.drop_acceptor, name='mediagallery-reverse-url')
        )
        return my_urls + urls

# ------------------------------------------------------------------------
