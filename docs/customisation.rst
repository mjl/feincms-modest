Customisation
=============
XXX describe implementation own drop acceptor, adding other layouts

.. _label-customisation-templates:

Templates
---------
To customise the look of a media gallery, you will have to create a template
that matches the layout ``key`` as defined during configuration in
:ref:`LAYOUT_CHOICES<label-installation-layout-choices>`.
The render phase will try to use the following templates:
:file:`content/media-gallery/content-%(layout_key)s.html`
and, as fall back only, :file:`content/media-gallery/content.html`.

Included are a simple :file:`content.html` to illustration how to access
the gallery items, and a more elaborate :file:`content-media-list.html`
that displays a simple list of media assets for downloading:

.. figure:: images/example_media_list.png
   :align: center




Extending drag and drop
-----------------------

