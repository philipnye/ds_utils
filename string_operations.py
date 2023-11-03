# !/usr/bin/env python
# -*- coding: utf-8 -*-


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
        'Dr', 'Hon',
        'Miss', 'Mr', 'Mrs', 'Ms',
        'Prof', 'Sir', 'The',
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
