# !/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Any, Callable, Iterable


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


def test_function_on_iterable(
    iterable: Iterable[Any],
    function: Callable,
    empty_iterable_result: bool = False,
) -> bool:
    '''
    Check that all elements of an iterable are equal

    Parameters
    ----------
    iterable: The iterable to test
    function: The function to test
    empty_iterable_result: The result to return if the iterable is empty

    Returns
    -------
    result: True if the function returns True for all elements of the iterable

    Examples
    --------
    >>> test_function_on_iterable([1, 2, 3], lambda x: x > 0)
    True
    >>> test_function_on_iterable([1, 2, 3], lambda x: x > 1)
    False
    >>> test_function_on_iterable([], lambda x: x > 0)
    False
    >>> test_function_on_iterable([], lambda x: x > 0, empty_iterable_result=True)
    True
    >>> test_function_on_iterable([[1, 2], [3], [4, 5, 6, 7]], lambda x: len(x) > 0)
    True
    >>> test_function_on_iterable([[1, 2], [3], [4, 5, 6, 7]], lambda x: len(x) > 1)
    False

    Notes
    -----
    None

    '''
    # Convert iterable to list to ensure it supports len() and multiple passes
    iterable = list(iterable)
    # Test for empty iterable
    if empty_iterable_result:
        if len(iterable) == 0:
            return True
    else:
        if len(iterable) == 0:
            return False

    # Test function on iterable
    result = [function(x) for x in iterable]

    return all(result)
