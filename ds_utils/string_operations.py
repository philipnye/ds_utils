# !/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Optional


def split_title_names(
    name: str,
) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Split names containing 'of' into probable title, last_name, place

    Parameters
        - name: Name to split

    Returns
        - title: Probable title
        - last_name: Probable last name
        - place: Probable place

    Notes
        None
    """
    # Raise error if 'of' not in name
    if 'of' not in name:
        raise ValueError('\'of\' not in name')

    # Set default values
    title, last_name, place = None, None, None

    # Count number of words before 'of'
    name_split = name.split(' ')
    of_index = name_split.index('of')

    # If one word before 'of', word before 'of' is title, words after 'of' are place
    # e.g. 'Duke of Wellington', 'Earl of Minto'
    if of_index == 1:
        title = name_split[0]
        place = ' '.join(name_split[of_index + 1:])

    # If 'Lord Archbishop' or 'Lord Bishop' before 'of', words before 'of' are title,
    # words after 'of' are place
    # e.g. 'Lord Bishop of London', 'Lord Bishop of Bath and Wells'
    elif (
        of_index > 1 and
        ' '.join(name_split[:2]) in ['Lord Archbishop', 'Lord Bishop']
    ):
        title = ' '.join(name_split[:2])
        place = ' '.join(name_split[3:])

    # If more than one word before 'of', first word is title, other words before
    # 'of' are last_name, and words after 'of' are place
    # e.g. 'Lord Young of Cookham', 'Lord Cameron of Chipping Norton'
    elif of_index > 1:
        title = name_split[0]
        last_name = ' '.join(name_split[1:of_index])
        place = ' '.join(name_split[of_index + 1:])

    return title, last_name, place


def strip_name_title(
    name: str,
    exclude_peerage: bool = False
) -> str:
    '''
        Strip titles from a name

        Parameters
            name: Name to operate on
            exclude_peerage: Whether to exclude peerage titles

        Returns
            name: Cleansed name

        Notes
            None
    '''

    # Remove titles
    if name.partition(' ')[0] in [
        'Miss', 'Mr', 'Mrs', 'Ms',
        'Dame', 'Sir',
        'Dr', 'Hon', 'Prof', 'The',
    ]:
        name = name.partition(' ')[2]

    if not exclude_peerage:
        if name.partition(' ')[0] in [
            'Baroness', 'Earl', 'Lord', 'Viscount',
        ]:
            name = name.partition(' ')[2]

    # Strip leading and trailing whitespace
    name = name.strip()

    # Replace multiple consecutive whitespace
    name = ' '.join(name.split())

    return name
