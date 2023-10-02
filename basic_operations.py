from typing import Iterable, Any


def all_equal(iterable: Iterable[Any]) -> bool:
    '''
    Check that all elements of an iterable are equal

    Parameters
    ----------
    iterable: The iterable to test

    Returns
    -------
    result: True if all elements are equal, False otherwise

    Examples
    --------
    >>> all_equal([1, 1, 1])
    True
    >>> all_equal([1, 2, 1])
    False
    >>> all_equal([])
    True

    Notes
    -----
    None

    '''
    iterable = iter(iterable)
    try:
        first = next(iterable)
    except StopIteration:
        return True
    return all(first == x for x in iterable)
