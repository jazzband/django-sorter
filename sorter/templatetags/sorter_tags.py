from fnmatch import fnmatch
from urlobject import URLObject

from django import template
from django.conf import settings
from django.core.exceptions import FieldError
from django.template import TemplateSyntaxError
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.utils.text import get_text_list

import ttag

from sorter.utils import cycle_pairs

register = template.Library()


class SorterAsTag(ttag.helpers.AsTag):

    def clean(self, data, context):
        """
        Checks if there is a ``request`` variable
        included in the context.
        """
        request = context.get('request')
        if not request:
            raise TemplateSyntaxError("Couldn't find request in context: %s" %
                                      context)
        return super(SorterAsTag, self).clean(data, context)

    def clean_with(self, value):
        """
        Cleans the given name of the sort query
        """
        if not isinstance(value, basestring):
            raise TemplateSyntaxError("Value '%s' is not a string" % value)
        # in case the value equals the default query name
        # or it already has the default query name prefixed
        if (value == settings.SORTER_QUERY_NAME or
                value.startswith(settings.SORTER_QUERY_NAME)):
            return value
        return '%s_%s' % (settings.SORTER_QUERY_NAME, value)


class Sort(SorterAsTag):
    """
    {% sort queryset [with NAME] as VARIABLE %}

    {% sort object_list with "objects" as sorted_objects %}

    """
    exceptions = (FieldError,)

    data = ttag.Arg()
    with_ = ttag.Arg(named=True, required=False, default=settings.SORTER_QUERY_NAME)

    def as_value(self, data, context):
        value = data['data']
        ordering = self.ordering(context, data['with'])
        try:
            ordered_value = value.order_by(*ordering)
            if settings.SORTER_EVALUATE_AFTERWARDS:
                ordered_value = list(ordered_value)
            return ordered_value
        except self.exceptions:
            if settings.SORTER_RAISE_EXCEPTIONS:
                raise
        return value

    def ordering(self, context, name):
        """
        Given the template context and the name of the sorting
        should return a list of ordering values.
        """
        try:
            sort_fields = context['request'].GET[name].split(',')
        except (KeyError, ValueError, TypeError):
            return []
        allowed_ordering = settings.SORTER_ALLOWED_ORDERING.get(name, [])
        if not allowed_ordering:
            return sort_fields
        result = []
        for sort_field in sort_fields:
            for ordering in allowed_ordering:
                if fnmatch(sort_field.lstrip('-'), ordering):
                    result.append(sort_field)
        return result


class TemplateAsTagOptions(ttag.helpers.as_tag.AsTagOptions):

    def __init__(self, meta, *args, **kwargs):
        super(TemplateAsTagOptions, self).__init__(meta=meta, *args, **kwargs)
        self.template_name = getattr(meta, 'template_name', 'sortlink')


class TemplateAsTagMetaclass(ttag.helpers.as_tag.AsTagMetaclass):
    options_class = TemplateAsTagOptions


class Sortlink(SorterAsTag):
    """
    Parses a tag that's supposed to be in this format:

    {% sortlink [with NAME] [rel REL] [class CLASS] [as VARIABLE] by ORDER_A1[,ORDER_A2,..] [ORDER_B1[,ORDER_B2,..]] .. %}
        LABEL
    {% endsortlink %}

    {% sortlink with "objects" by "creation_date,-title" %}
        {% trans "Creation and title" %}
    {% endsortlink %}

    """
    __metaclass__ = TemplateAsTagMetaclass

    with_ = ttag.Arg(required=False, named=True, default=settings.SORTER_QUERY_NAME)
    rel = ttag.Arg(required=False, named=True)
    class_ = ttag.Arg(required=False, named=True)
    by = ttag.MultiArg(named=True)

    class Meta:
        block = True
        as_required = False
        template_name = 'sortlink'

    def as_value(self, data, context):
        label = self.nodelist.render(context)
        if not label.strip():
            raise TemplateSyntaxError("No label was specified")

        # The queries of the current URL, not using sequences here
        # since the order of sorting arguments matter
        url = URLObject.parse(context['request'].get_full_path())
        queries = url.query_dict(seq=False)

        name, orderings = data['with'], data['by']
        query = self.find_query(queries.get(name), orderings, orderings[0])
        url = url.set_query_param(name, query)

        parts = []
        for part in query.split(','):
            part = part.strip()
            if part.startswith('-'):
                part = part.lstrip('-')
                # Translators: Used in title of descending sort fields
                text = _("'%(sort_field)s' (desc)")
            else:
                # Translators: Used in title of ascending sort fields
                text = _("'%(sort_field)s' (asc)")
            parts.append(text % {'sort_field': part})
        # Translators: Used for the link/form input title excluding the sort fields
        title = (_('Sort by: %(sort_fields)s') %
                 {'sort_fields': get_text_list(parts, _('and'))})

        extra_context = dict(data, title=title, label=label, url=url, query=query)
        return render_to_string(self.using(data), extra_context, context)

    def find_query(self, wanted, orderings, default):
        """
        Given the list of order statements and a query that is currently
        found in the request's querystring returns the next in line,
        or falls back to the given default.
        """
        for current, next in cycle_pairs(orderings):
            if current == wanted:
                return next
        return default

    def using(self, data):
        """
        This template tag will use 'sorter/sortlink.html' by default,
        but uses 'sorter/sortlink_NAME.html' additionally if the
        'with' argument is given.
        """
        name = data.get('with')
        template_names = [self._meta.template_name]
        if name and name != settings.SORTER_QUERY_NAME:
            template_names.append(u'%s_%s' % (self._meta.template_name, name))
        return [u"sorter/%s.html" % name for name in template_names]


class Sortform(Sortlink):
    """
    Parses a tag that's supposed to be in this format:

    {% sortform [with NAME] [rel REL] [method METHOD] [class CLASS] [as VARIABLE] by ORDER_A1[,ORDER_A2,..] [ORDER_B1[,ORDER_B2,..]] .. %}
        LABEL
    {% endsortform %}

    {% sortform with "objects" by "creation_date,-title" method "post" %}
        {% trans "Creation and title" %}
    {% endsortform %}

    """
    method = ttag.Arg(named=True, required=False, default='get')

    class Meta:
        block = True
        as_required = False
        template_name = 'sortform'


register.tag(Sort)
register.tag(Sortlink)
register.tag(Sortform)
