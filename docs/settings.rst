Settings
========

SORTER_DEFAULT_QUERY_NAME
-------------------------

Default: ``'sort'``

The name of the querystring used by default when looking
at the current request path or generating links and or forms.

SORTER_ALLOWED_CRITERIA
-----------------------

Default: ``{}``

A mapping of query names to order field names that are checked before
ordering is applied.

The given names support Unix shell-style wildcards and define those
that are *allowed*, e.g. ``'author__*'``.

.. warning::

    If the setting is empty, **no fields** will be allowed which renders
    the template tags useless. Hence, it's an **configuration error** to
    not define this setting.

An example, which would apply to sort links like ``'/path/?sort=created'``
and ``'/path/?sort_posts=modified,author__username'``.

::

    SORTER_ALLOWED_CRITERIA = {
        'sort': ['created', 'title'],
        'sort_posts': ['modified', 'author__*'],
    }
