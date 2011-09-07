from itertools import tee, izip, chain


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
