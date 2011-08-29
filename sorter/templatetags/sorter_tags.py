from itertools import tee, izip, chain
from urlobject import URLObject

from django import template
from django.conf import settings
from django.core.exceptions import FieldError
from django.template import TemplateSyntaxError
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.utils.text import get_text_list

import ttag

register = template.Library()


def cycle_pairs(iterable):
    """
    Cycles through the given iterable, returning an iterator which
    returns the current and the next item. When reaching the end
    it returns the last and the first item.
    """
    first, last = iterable[0], iterable[-1]
    a, b = tee(iterable)
    next(b, None)
    return chain(izip(a, b), [(last, first)])


class CleanQueryNameMixin(object):
    """
    A mixin to clean with given name of the sort query
    """
    def clean_with(self, value):
        if not isinstance(value, basestring):
            raise TemplateSyntaxError("Value '%s' is not a string" % value)
        if value == settings.SORTER_QUERY_NAME:
            return value
        return '%s_%s' % (settings.SORTER_QUERY_NAME, value)


class Sort(ttag.helpers.AsTag, CleanQueryNameMixin):
    """
    {% sort queryset [with NAME] as VARIABLE %}

    {% sort object_list with "objects" as sorted_objects %}

    """
    exceptions = [FieldError]

    data = ttag.Arg()
    with_ = ttag.Arg(named=True, required=False, default=settings.SORTER_QUERY_NAME)

    def clean(self, data, context):
        request = context.get('request')
        if not request:
            raise TemplateSyntaxError("Couldn't find request in context: %s" %
                                      context)
        return data

    def as_value(self, data, context):
        ordering = self.get_fields(context['request'], data['with'])
        value = data['data']
        if ordering:
            try:
                return value.order_by(*ordering)
            except self.exceptions:
                if settings.SORTER_RAISE_EXCEPTIONS:
                    raise
        return value

    def get_fields(self, request, name):
        try:
            return request.GET[name].split(',')
        except (KeyError, ValueError, TypeError):
            pass
        return []


class Sortlink(ttag.helpers.AsTag, CleanQueryNameMixin):
    """
    Parses a tag that's supposed to be in this format:

    {% sortlink [with NAME] [rel REL] [class CLASS] [as VARIABLE] by ORDER_A1[,ORDER_A2,..] [ORDER_B1[,ORDER_B2,..]] .. %}
        LABEL
    {% endsortlink %}

    {% sortlink with "objects" by "creation_date,-title" %}
        {% trans "Creation and title" %}
    {% endsortlink %}

    """
    with_ = ttag.Arg(required=False, named=True, default=settings.SORTER_QUERY_NAME)
    rel = ttag.Arg(required=False, named=True)
    class_ = ttag.Arg(required=False, named=True)
    by = ttag.MultiArg(named=True)

    class Meta:
        block = True
        as_required = False

    def as_value(self, data, context):
        request = context.get('request')
        if not request:
            raise TemplateSyntaxError("Couldn't find request in context: %s" %
                                      context)
        label = self.nodelist.render(context)
        if not label.strip():
            raise TemplateSyntaxError("No label was specified")

        # The queries of the current URL, not using sequences here
        # since the order of sorting arguments matter
        url = URLObject.parse(request.get_full_path())
        queries = url.query_dict(seq=False)

        name, orderings = data['with'], data['by']
        query = self.find_query(queries.get(name), orderings, orderings[0])
        url = url.set_query_param(name, query)

        parts = []
        for part in query.split(','):
            part = part.strip()
            if part.startswith('-'):
                dir_, part = 'desc', part.lstrip('-')
            else:
                dir_ = 'asc'
            parts.append(_("'%(part)s' (%(dir)s)") %
                           {'dir': dir_, 'part': part})
        title = _('Sort by %s') % get_text_list(parts, _('and'))
        extra_context = dict(data, title=title, label=label, url=url)
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

    def using(self, data, template_name='sorter/sortlink.html'):
        """
        This template tag will use 'sorter/sortlink.html' by default,
        but uses 'sorter/sortlink_SUFFIX.html' additionally if the
        'with' argument is given.
        """
        name = data.get('with')
        if not name:
            return template_name
        return ['sorter/sortlink_%s.html' % name] + [template_name]


register.tag(Sort)
register.tag(Sortlink)
