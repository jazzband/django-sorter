django-sorter
-------------

``django-sorter`` helps sorting objects in Django templates and generating
links without modifying your views.

1. List this application in the ``INSTALLED_APPS`` setting.
   Your settings file might look something like::

       INSTALLED_APPS = (
           # ...
           'sorter',
       )

2. If it's not already added in your setup, add the ``request`` template
   context processor. If you don't have ``TEMPLATE_CONTEXT_PROCESSORS``
   defined in your setting, you might need to `add it`_::

       TEMPLATE_CONTEXT_PROCESSORS = (
           # ...
           "django.core.context_processors.request",
       )

3. Add this line at the top of your template to load the sorting tags:

       {% load sorter_tags %}

4. Decide on a variable that you would like to order by, and use the
   sort tag on that variable before iterating over it.

       {% sort objects as sorted_objects %}

5. Optionally, you can display different sort links::

    <tr>
       <th>{% sortlink by "first_name" %}Name{% endsortlink %}</th>
       <th>{% sortlink by "creation_date,-title" %}Creation{% endsortlink %}</th>
        ...
    </tr>

    The template tag takes a comma separated list of sorting statements.
    It also is a block tag and allows you to set the label of the generated
    link. The previous snippet will be rendered like this::

    <tr>
        <th><a href="/current/path/?sort=first_name" title="Sort by 'first_name' (asc)">Name</a></th>
        <th><a href="/current/path/?sort=creation_date,-title" title="Sort by 'creation_date' (asc) and 'title' (desc)">Creation</a></th>
        ...
    </tr>

That's it!


.. _`add it`: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors