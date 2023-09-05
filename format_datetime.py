# #!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Purpose
        Standard functions to format dates or times
    Inputs
        None
    Outputs
        None
    Parameters
        None
    Notes
        None
'''


# DEFINE FUNCTION TO MAP MONTHS TO NUMBERS
def map_month_to_number(month, padded=False):
    '''
        Map month to number

        Parameters
            - month: Month to map
            - padded: Whether to pad number with a zero

        Returns
            - Number corresponding to month
    '''

    month_map = {
        'January': 1,
        'February': 2,
        'March': 3,
        'April': 4,
        'May': 5,
        'June': 6,
        'July': 7,
        'August': 8,
        'September': 9,
        'October': 10,
        'November': 11,
        'December': 12
    }

    if padded:
        return '{:02d}'.format(month_map[month])
    else:
        return month_map[month]
