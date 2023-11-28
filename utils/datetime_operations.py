# !/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Union

import pandas as pd


def convert_date_string_to_period(item: str) -> pd.Period:
    '''
        Converts a date string to a pandas period object

        Parameters
            - item: a date string in the format YYYY-MM-DD

        Returns
            - a pandas period object

        Notes
            - Ref: https://calmcode.io/til/pandas-timerange.html
    '''

    year = int(item[: 4])
    month = int(item[5: 7])
    day = int(item[8: 10])

    return pd.Period(year=year, month=month, day=day, freq='D')


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


def map_year_month_to_financial_year(
    year: int,
    month: Union[int, str],
) -> str:
    '''
        Map year and month to financial year

        Parameters
            - year: Year
            - month: Month

        Returns
            - fin_year: Financial year
    '''

    # Convert month to number if it's a string
    if isinstance(month, str):
        month = map_month_to_number(month)

    # Handle case where month is between April and end of calendar
    # year
    if month >= 4:
        fin_year = f'{year}/{str(year + 1)[2:]}'

    # Handle case where month is between January and March
    else:
        fin_year = f'{year - 1}/{str(year)[2:]}'

    return fin_year
