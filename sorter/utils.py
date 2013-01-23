from itertools import tee, izip, chain
from fnmatch import fnmatch
from sorter.conf import settings

def cycle_pairs(iterable):
    """
    Cycles through the given iterable, returning an iterator which
    returns the current and the next item. When reaching the end
    it returns the last and the first item.
    """
    first, last = iterable[0], iterable[-1]
    a, b = tee(iterable)
    iter(b).next()
    return chain(izip(a, b), [(last, first)])

def ordering(request, name):
    """
    Given the request and the name of the sorting
    should return a list of ordering values.
    """
    try:
        sort_fields = request.GET[name].split(',')
    except (KeyError, ValueError, TypeError):
        return []
    result = []
    allowed_criteria = settings.SORTER_ALLOWED_CRITERIA.get(name)
    if allowed_criteria is None:
        return result
    for sort_field in sort_fields:
        for criteria in allowed_criteria:
            if fnmatch(sort_field.lstrip('-'), criteria):
                result.append(sort_field)
    return result