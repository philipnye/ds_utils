# #!/usr/bin/env python
# -*- coding: utf-8 -*-


import pandas as pd
import pandas.testing as pdt

from ds_utils import datetime_operations as do


def test_calculate_date_string_end_date():
    data = [
        ('2021-01-01', '%Y-%m-%d', pd.to_datetime('2021-01-01')),
        ('2022-06-01', '%Y-%m-%d', pd.to_datetime('2022-06-01')),
        ('01/01/2021', '%d/%m/%Y', pd.to_datetime('2021-01-01')),
        ('01/06/2022', '%d/%m/%Y', pd.to_datetime('2022-06-01')),
        ('31/03/2022', '%d/%m/%Y', pd.to_datetime('2022-03-31')),
        ('2022', '%Y', pd.to_datetime('2022-12-31')),
        ('2022/23', '%Y/%y', pd.to_datetime('2023-03-31')),
        ('2022-23', '%Y-%y', pd.to_datetime('2023-08-31')),
        ('Jan 2022 - Jan 2023', '%b %y - %b %y', pd.to_datetime('2023-01-31')),
        ('Feb 2022 - Jan 2023', '%b %y - %b %y', pd.to_datetime('2023-01-31')),
        ('February 2022 - February 2023', '%B %Y - %B %Y', pd.to_datetime('2023-02-28')),
        ('February 2022 - January 2023', '%B %Y - %B %Y', pd.to_datetime('2023-01-31')),
        ('April 2022/23', '%B %Y/%y', pd.to_datetime('2022-04-30')),
        ('August 2022/23', '%B %Y/%y', pd.to_datetime('2022-08-31')),
        ('March 2022/23', '%B %Y/%y', pd.to_datetime('2023-03-31')),
        ('2023 Q1', '%Y %Q', pd.to_datetime('2023-03-31')),
        ('2023 Q4', '%Y %Q', pd.to_datetime('2023-12-31')),
        ('2022/23 Q3', '%Y/%y %Q', pd.to_datetime('2022-12-31')),
        ('2022/23 Q4', '%Y/%y %Q', pd.to_datetime('2023-03-31')),
        ('2023', '%Y + 1', pd.to_datetime('2023-12-31')),
        ('31-03-2022', '31-03-%Y', pd.to_datetime('2022-03-31')),
    ]

    df = pd.DataFrame(
        data,
        columns=['input', 'format', 'output']
    )

    output = [
        do.calculate_date_string_end_date(
            input,
            format,
            financial_year_sep='/',
            academic_year_sep='-',
        )
        for input, format
        in zip(
            df['input'],
            df['format']
        )
    ]

    pdt.assert_series_equal(df['output'], pd.Series(output, name='output'))

    return


def test_map_year_month_to_financial_year():
    assert do.map_year_month_to_financial_year(2021, 4) == '2021/22'
    assert do.map_year_month_to_financial_year(2021, 'April') == '2021/22'
    assert do.map_year_month_to_financial_year(2021, 3) == '2020/21'
    assert do.map_year_month_to_financial_year(2021, 'March') == '2020/21'
    assert do.map_year_month_to_financial_year(2022, 1) == '2021/22'
    assert do.map_year_month_to_financial_year(2022, 'January') == '2021/22'
    assert do.map_year_month_to_financial_year(2022, 12) == '2022/23'
    assert do.map_year_month_to_financial_year(2022, 'December') == '2022/23'

    return
