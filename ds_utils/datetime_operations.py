# !/usr/bin/env python
# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from typing import Literal, Optional, Union

import pandas as pd


def calculate_date_string_end_date(
    date_str: str,
    date_format: Optional[str],
    financial_year_sep: Literal['/', '-', None],
    academic_year_sep: Literal['/', '-', None],
) -> pd.Timestamp:
    '''
    Calculate an end date from a date string, including non-standard
    date formats

    Parameters:
        - date_str (str): An input date strings - which can include
        things in non-standard formats, such as calendar, financial
        and academic year quarters
        - date_format (str): The format the supplied date is in
        - financial_year_sep (str): The separator between the two
        years in a financial year
        - academic_year_sep (str): The separator between the two
        years in an academic year

    Returns:
        - end_date (datetime): The end date of the input date string

    Notes:
        None
    '''

    def predict_date_format(date_str):
        '''
        Attempt to predict the format of a date string based on its
        formatting

        Parameters:
            - date_str (str): An input date strings - which can include
            things in non-standard formats, such as calendar, financial
            and academic year quarters

        Returns:
            - date_format (str): The end date of the input date string

        Notes:
            None
        '''

        if len(date_str) == 4:
            date_format = '%Y'
        elif (
            len(date_str) == 7 and
            '/' in date_str and
            len(date_str.split('/')[0]) == 4 and
            len(date_str.split('/')[1]) == 2
        ):
            date_format = '%Y/%y'
        else:
            date_format = None

        return date_format

    # Attempt to predict date format
    if date_format is None:
        date_format = predict_date_format(date_str)

    # Calendar year
    if date_format in ['%Y', '%Y + 1']:
        end_date = str(date_str) + '-12-31'

    # Financial year
    elif date_format == '%Y/%y' and financial_year_sep == '/':
        end_date = date_str[:2] + date_str[-2:] + '-03-31'
    elif date_format == '%Y-%y' and financial_year_sep == '-':
        end_date = date_str[:2] + date_str[-2:] + '-03-31'

    # Academic year
    elif date_format == '%Y-%y' and academic_year_sep == '-':
        end_date = date_str[:2] + date_str[-2:] + '-08-31'
    elif date_format == '%Y/%y' and academic_year_sep == '/':
        end_date = date_str[:2] + date_str[-2:] + '-08-31'

    # Calendar year quarter
    elif date_format == '%Y %Q':
        if date_str[-3:] == 'All':
            end_date = date_str[:4] + '-12-31'
        elif date_str[-1:] == '1':
            end_date = date_str[:4] + '-03-31'
        elif date_str[-1:] == '2':
            end_date = date_str[:4] + '-06-30'
        elif date_str[-1:] == '3':
            end_date = date_str[:4] + '-09-30'
        elif date_str[-1:] == '4':
            end_date = date_str[:4] + '-12-31'

    # Financial year quarter
    elif date_format in ['%Y/%y %Q', '%Y-%y %Q']:
        if date_str[-3:] == 'All':
            end_date = str(int(date_str[:4]) + 1) + '-03-31'
        elif date_str[-1:] == '4':
            end_date = str(int(date_str[:4]) + 1) + '-03-31'
        elif date_str[-1:] == '1':
            end_date = date_str[:4] + '-06-30'
        elif date_str[-1:] == '2':
            end_date = date_str[:4] + '-09-30'
        elif date_str[-1:] == '3':
            end_date = date_str[:4] + '-12-31'

    # School term
    # NB: This calculates a notional rather than an actual end
    # date - e.g. April will not always fall in the spring term
    elif date_format == '%Y-%y %T':
        if 'autumn' in date_str.lower():
            end_date = date_str[:4] + '-12-31'
        elif 'spring' in date_str.lower():
            end_date = date_str[:2] + date_str[5:7] + '-04-30'
        elif 'summer' in date_str.lower():
            end_date = date_str[:2] + date_str[5:7] + '-08-31'

    # 31 March of year
    elif date_format == '31-03-%Y':
        end_date = pd.to_datetime(
            date_str,
            dayfirst=True
        )

    # Other non-standard formats
    elif date_format == '%b %y - %b %y':

        # Turn end month/year into a date, add a month and subtract a day -
        # as the easiest way of getting to the end of the month
        end_date = (
            pd.to_datetime(date_str.split('-')[1].strip()) +
            relativedelta(months=1) - relativedelta(days=1)
        )

    elif date_format == '%B %Y - %B %Y':

        # Turn end month/year into a date, add a month and subtract a day -
        # as the easiest way of getting to the end of the month
        end_date = (
            pd.to_datetime(date_str.split('-')[1].strip()) +
            relativedelta(months=1) - relativedelta(days=1)
        )

    elif date_format == '%B %Y':
        end_date = (
            pd.to_datetime(date_str) +
            relativedelta(months=1) - relativedelta(days=1)
        )

    elif date_format == '%b-%Y':
        end_date = (
            pd.to_datetime(date_str) +
            relativedelta(months=1) - relativedelta(days=1)
        )

    elif date_format == '%b-%y':
        date_str = date_str[:3] + '-20' + date_str[-2:]
        end_date = (
            pd.to_datetime(date_str) +
            relativedelta(months=1) - relativedelta(days=1)
        )

    elif date_format in ['%B %Y/%y', '%B %Y-%y']:

        # Grab month + first year of financial year
        end_date = pd.to_datetime(date_str[:-3])

        # Iterate year if we're in the first three months
        if end_date.month <= 3:
            end_date += relativedelta(years=1)

        # Move to end of the month
        end_date += relativedelta(months=1) - relativedelta(days=1)

    # Standard formats
    elif date_format in [
        '%d/%m/%Y',
        '%d-%b-%Y',
        '%Y-%m-%d',
    ]:
        end_date = pd.to_datetime(
            date_str,
            format=date_format
        )

    else:
        raise RuntimeError('Date format not handled')

    end_date = pd.to_datetime(
        end_date
    )

    return end_date


def convert_academicfinancial_year_string_to_year_string(year: str) -> str:
    '''
    Convert a financial or academic year string to a year string

    Parameters
        - year: A string representing a financial or academic year

    Returns
        - formatted_year: A string representing a year

    Notes
        - The year returned is the end year of the financial or academic year
        - See related convert_year_string_to_academicfinancial_year_string()
    '''
    if len(str(year)) == 6:
        formatted_year = str(year)[:4]
    elif len(str(year)) == 7:
        formatted_year = str(year)[:4]

    return formatted_year


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


def convert_year_string_to_academicfinancial_year_string(
    year: str,
    sep: str
) -> str:
    '''
    Convert a year string from one format to another

    Parameters
        - year: A string representing a year

    Returns
        - formatted_year: A string representing a year in a different format

    Notes
        - Where year is a calendar year, the academic year or financial returned
        is the one which ends in the calendar year
        - See related convert_academicfinancial_year_string_to_year_string()
    '''
    if sep is None:
        sep = ''

    if len(str(year)) == 4:
        formatted_year = str(year - 1) + sep + str(year)[-2:]
    elif len(str(year)) == 6:
        formatted_year = str(year)[:4] + sep + str(year)[-2:]
    elif len(str(year)) == 7:
        formatted_year = str(year)[:4] + sep + str(year)[-2:]
    elif type(year) is pd.Timestamp:
        formatted_year = str(year.year - 1) + sep + str(year.year)[-2:]

    return formatted_year


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
