django-sorter
=============

.. image:: https://jazzband.co/static/img/badge.svg
   :target: https://jazzband.co/
   :alt: Jazzband

``django-sorter`` helps with sorting objects in Django templates without
modifying your views, can be used multiple times on the same page or
template, provides helpers to easily generate links and forms to switch
the sorting criteria (including the sort order) and has ~100% test coverage.

Quickstart
----------

#. Get the app with your favorte Python packaging tool, e.g.::

    pip install django-sorter

#. List this application in the ``INSTALLED_APPS`` setting.
   Your settings file might look something like::

        INSTALLED_APPS = (
            # ...
            'sorter',
        )

#. If it's not already added in your setup, add the ``request`` template
   context processor to the ``TEMPLATE_CONTEXT_PROCESSORS`` setting
   (you might need to `add it`_)::

        TEMPLATE_CONTEXT_PROCESSORS = (
            # ...
            'django.core.context_processors.request',
        )

#. Specify the allowed sorting criteria, for at least the default
   ``'sort'`` sorting querystring parameter::

        SORTER_ALLOWED_CRITERIA = {
            'sort': ['first_name', 'creation_date', 'title'],
        }

#. Add this line at the top of your template to load the sorting tags::

        {% load sorter_tags %}

#. Decide on a variable that you would like to sort, and use the
   sort tag on that variable before iterating over it.

   ::

       {% sort objects as sorted_objects %}

#. Optionally, you can display different sort links or forms::

        <tr>
           <th>{% sortlink by "first_name" %}By first name{% endsortlink %}</th>
           <th>{% sortlink by "creation_date,-title" %}By creation date and title{% endsortlink %}</th>
            ...
        </tr>

   The template tag takes a comma separated list of sorting statements.
   It also is a block tag and allows you to set the label of the generated
   link. The previous snippet will be rendered like this::

        <tr>
            <th><a href="/?sort=first_name" title="Sort by 'first_name' (asc)">By name</a></th>
            <th><a href="/?sort=creation_date,-title" title="Sort by 'creation_date' (asc) and 'title' (desc)">By creation and title</a></th>
            ...
        </tr>

   Similarly the ``{% sortform %}`` template tag renders a form instead of
   a simple link.

.. _`add it`: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
