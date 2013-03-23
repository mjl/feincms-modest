===============
FeinCMS Gallery
===============

This package provides a gallery content type for FeinCMS. It can be used
to present a collection of other content types. It is very flexible about
what it can actually present and how it is presented, so the framework
can be used to produce image galleries, pdf file download links or even
product presentations.

It comes with integration for the MediaFile CT and a set of templates to
render MediaFiles. Configuration is made easy by supporting drag and drop
operations out of the MediaFile admin list.

XXX sample screen shots

Usage
-----
This content type is added to FeinCMS as any other content type::

    from gallery.models import MediaGalleryContent
    Page.create_content_type(MediaGalleryContent,
                         LAYOUT_CHOICES=(('', 'default'),
                                         ('media-list', 'Media-List')
                         ))

Options
-------
On creation, the MediaGalleryContent accpepts the following additional
parameters:

* LAYOUT_CHOICES:
  A list of tuples describing what presentation styles should be available.

* DROP_ACCEPTOR:
  A filter responsible for taking a URL and converting it to a MediaFile.
  Used for the drag and drop operation.

Admin Interface
---------------
XXX describe options, drag&drop, screen shots

Customisation
-------------
XXX describe implementation own drop acceptor, adding other layouts

Installation
------------

To install this module, simply: ::

	$ pip install feincms-media-gallery
