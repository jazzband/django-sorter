Usage
=====

.. highlight:: html+django

.. _sort:

Sorting
-------

The center piece of the app is the ``{% sort %}`` template tag which
takes one required and one optional argument.

The bare bones example is::

    {% load sorter_tags %}

    {% sort object_qs as sorted_objects %}

    {% for obj in sorted_objects %}
        {{ obj.title }}
    {% endfor %}

If this template is rendered with a list of ``objects``, say a Django
QuerySet, the template tag will order it by calling the ``order_by()``.
The sorting criteria passed to this method is retrieved from the
request's GET paramaters (the "querystring_") by looking for a field-value
pair with the name **sort**.

Simple
++++++

So imagine you have a list of blog posts that you want to sort by their
creation dates, in an ascending order. With the example template above
all you'd have to do is to call the view rendering those blog posts with
the appropriate querystring::

    http://example.com/blog/?sort=creation_date

Since name of the field is automatically picked up and passed to
``order_by()`` you can also sort in descending order by prepending
the name of the field with a negative sign (``-``)::

    http://example.com/blog/?sort=-creation_date

You can also pass multiple fields to the querystring parameter to
sort for multiple fields::

    http://example.com/blog/?sort=-creation_date,title

Complex
+++++++

In some cases you may want to sort multiple lists of objects in the same
template or use advanced techniques like chained sorting workflows.

All you need to do is to pass a second parameter to the ``{% sort %}``
template tag which defines the name of the querystring parameter::

    {% load sorter_tags %}

    {% sort object_qs with "posts" as sorted_objects %}

    {% for obj in sorted_objects %}
        {{ obj.title }}
    {% endfor %}

Make sure to use unique names to prevent any clash with other sortings
that may happen on the same page. As a matter of additional precaution
the template tag will prepend it with ``'sort_'`` when analyzing the
request's querystring.

So if you'd use the example template above, the template tag would look
for a querystring parameter named ``'sort_posts'`` because the second
parameter to the template tag is ``"posts"``::

    http://example.com/blog/?sort_posts=creation_date

.. _sortlink:

Links
-----

When sorting objects it's usually required to link to other sorting
criterias. ``django-sorter`` includes the ``{% sortlink %}`` template tag
for that which takes a number of optional arguments and a required list of
sorting criterias::

    {% sortlink [with NAME] [rel REL] [class CLASS] [as VARIABLE] by ORDER_A1[,ORDER_A2,..] [ORDER_B1[,ORDER_B2,..]] .. %}
        LABEL
    {% endsortlink %}

As with the :ref:`{% sort %}<sort>` template tag, ``sortlink`` takes the
name of the querystring parameter it's supposed to be working with.

For example, the following code would fit the example
:ref:`shown above<sort>`::

    {% sortlink with "posts" by "title" %}Title{% endsortlink %}

If this snippet would be included in a template that renders your blog
(with a request path of ``'/blog/'``), we'd get::

    <a href="/blog/?sort_posts=title" title="Sort by: 'title' (desc)">Title</a>

Multiple criterias
++++++++++++++++++

Multiple sorting criterias can be specified in comma separated form::

    {% sortlink with "posts" by "creation_data,title" %}
        Creation date and title
    {% endsortlink %}

would generate::

    <a href="/blog/?sort=-creation_date,title" title="Sort by: 'creation_date' (asc) and 'title' (desc)">Creation date and title</a>

Link text
+++++++++

The template tag is a block tag, which means translating the link text
is as easy as using Django's ``trans`` template tag::

    {% load i18n %}

    {% sortlink with "posts" by "creation_data,title" %}
        {% trans "Creation date and title" %}
    {% endsortlink %}

Other paramters
+++++++++++++++

- ``rel`` which sets the appropriate attribute of the link,
  e.g. useful when trying to set `rel="nofollow"`_.

- ``class`` which is useful to style the link correctly.

- ``as`` which allows assigning the result of the template tag to
  a template context variable.

Further customization
+++++++++++++++++++++

Of course any further customization is also possible by overriding the
templates used by the template tag. By default ``django-sorter`` will use
the ``sorter/sortlink.html`` template, to render each link.

Furthermore -- if a name is given with the ``with`` argument -- it'll also
look for the template ``sorter/sortlink_NAME.html``, where ``NAME`` is the
value of the argument passed. E.g.::

    {% sortlink with "posts" by "title" %}Title{% endsortlink %}

would make the template tag look for a ``sorter/sortlink_posts.html``
*and* ``sorter/sortlink.html``.

The template tag passes a bunch of variable to the template:

- ``with`` - The name of querystring parameter to take into account.
- ``rel`` - The value to be used for the HTML rel attribute.
- ``class`` - The value to be used for the HTML class attribute.
- ``by`` - The list of sorting criterias.
- ``title`` - A string which lists all search criteria in prose.
- ``label`` - The rendered content of the template block.
- ``url`` - The URLObject_ instance with the querystring set appropriately.
- ``query`` - The value of the querystring parameter.

.. _`rel="nofollow"`: http://en.wikipedia.org/wiki/Nofollow
.. _`URLObject`: https://github.com/zacharyvoase/urlobject

Criteria cycling
++++++++++++++++

Sometimes you'll want to allow switching between criterias depending on
the currently selected sorting criteria. For example, if you sort a
list of blog posts in ascending order you might want to show a link
to the same list but in *descending* order.

With ``django-sorter`` this is as easy as passing a **series** of sorting
criterias to the same template tag::

    {% sortlink with "posts" by "title" "-title" %}Title{% endsortlink %}

Now when the link is rendered it will check the current URL and select
**the next** sorting criteria to render.

For example, if you'd be on the page with the URL
``'/blog/?sort_posts=title'``, the result would be::

    <a href="/blog/?sort_posts=-title" title="Sort by: 'title' (desc)">Title</a>

Of course, if the last sorting criteria is found the current request's
querystring, it'll start with the first again.

.. _sortform:

Forms
-----

Other than the :ref:`sortlink<sortlink>` template tag, ``django-sorter``
also ships with a second template tag to apply other sorting criterias --
the ``sortform`` tag.

It works basically the same as ``sortlink`` and uses the same code behind
the scenes, but looks for a different template: ``sorter/sortform.html``.
Just like the :ref:`sortlink<sortlink>` tag it'll use the name of the
querystring parameter if given to additionally look for a specific template,
e.g. ``sorter/sortform_posts.html``

An example::

    {% sortform with "posts" by "creation_date" %}
        {% trans "Creation and title" %}
    {% endsortform %}

rendered::

    <form action="" method="get">
        <input type="hidden" name="sort_posts" value="creation_date" />
        <input type="submit" value="Creation date" title="Sort by: 'creation_date' (asc)" />
    </form>

.. _sorturl:

URLs
----

As a quick helper in case you don't like ``django-sorter`` to generate
the links or forms for your sorting efforts, you can also use the simple
``sorturl`` template tag::

    {% sorturl with "posts" by "creation_date" %}

would only return the URL to the sorting::

    /blog/?sort_posts=creation_date

Don't forget that it also takes an optional ``as`` parameter (like the rest
of the parameters described for the :ref:`sort<sort>` template tag). That's
great for storing the URL to further mangle it or use it for other template-y
things, e.g.::

    {% sorturl with "posts" by "creation_date" as sort_by_date_url %}

    {% blocktrans with sort_by_date_url as url %}
    Please visit the following URL to sort by date:

        http://example.com{{ sort_by_date_url }}

    Thanks!
    {% endblocktrans %}

.. _querystring: http://en.wikipedia.org/wiki/Querystring
