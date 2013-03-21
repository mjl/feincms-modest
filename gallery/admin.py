# ------------------------------------------------------------------------
# coding=utf-8
# ------------------------------------------------------------------------
#
#  Created by Martin J. Laubach on 2013-03-21
#  Copyright (c) 2013 Martin J. Laubach. All rights reserved.
#
# ------------------------------------------------------------------------

from __future__ import absolute_import

from django.contrib import admin

from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.utils.safestring import mark_safe

from feincms.module.medialibrary.models import MediaFile

from feincms.module.medialibrary.thumbnail import admin_thumbnail

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
class MediaFileWidget(ForeignKeyRawIdWidget):
    def render(self, name, value, attrs=None):
        html = super(MediaFileWidget, self).render(name, value, attrs)

        if value:
            try:
                mf = MediaFile.objects.get(pk=value)
            except MediaFile.DoesNotExist:
                return html

            image = admin_thumbnail(mf)
            if image:
                image = u'<img class="image-preview" src="%(url)s" />' % {'url': image}

                html = "<div class=\"field-mediafile-with-image-wrapper\">" + html + image + "</div>"
                return mark_safe(html)

        return html

# ------------------------------------------------------------------------
class MediaGalleryContentFilesAdminInlineBase(admin.TabularInline):
    ordering = ('ordering',)
    raw_id_fields = ('mediafile',)
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
    exclude = ('ordering', 'region', 'parent')

# ------------------------------------------------------------------------
