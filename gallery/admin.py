# ------------------------------------------------------------------------
# coding=utf-8
# ------------------------------------------------------------------------
#
#  Created by Martin J. Laubach on 2013-03-21
#  Copyright (c) 2013 Martin J. Laubach. All rights reserved.
#
# ------------------------------------------------------------------------

from __future__ import absolute_import

from urlparse import urlparse

from django.conf import settings
from django.conf.urls import patterns, url
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseNotFound
from django.utils import simplejson
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
@staff_member_required
def media_reverse_url(request):
    if not request.is_ajax():
        return HttpResponseNotFound()

    out = { 'status': 404 }

    try:
        mediafile = None
        u = request.REQUEST.get('url')
        p = urlparse(u)

        if p.netloc == request.META.get('HTTP_HOST', None):
            mediaurl = urlparse(settings.MEDIA_URL)
            mediachange_url = reverse("admin:medialibrary_mediafile_change", args=(0,)).replace('0/', '')
            if p.path.startswith(mediachange_url):
                rest = p.path[len(mediachange_url):-1]
                mediafile = MediaFile.objects.get(pk=int(rest))
            elif p.path.startswith(mediaurl.path):
                path = p.path[len(mediaurl.path):]
                mediafile = MediaFile.objects.get(file=path)

        if mediafile is not None:
            image = admin_thumbnail(mediafile, dimensions="150x100")

            out['mediafile_id']      = mediafile.id
            out['mediafile_type']    = mediafile.type
            out['mediafile_caption'] = unicode(mediafile)
            out['mediafile_url']     = image
            out['status']            = 200

    except Exception, e:
        print "@@", e

    r = HttpResponse(simplejson.dumps(out), content_type='application/json')
    print r.content
    return r

class MediaGalleryAdminBase(admin.ModelAdmin):
    exclude = ('ordering', 'region', 'parent')

    def get_urls(self):
        urls = super(MediaGalleryAdminBase, self).get_urls()
        my_urls = patterns('',
            url(r'^reverse-url/$', media_reverse_url, name='mediagallery-reverse-url')
        )
        return my_urls + urls

# ------------------------------------------------------------------------
