# #!/usr/bin/env python
# -*- coding: utf-8 -*-


import format_datetime as fd


def test_map_year_month_to_financial_year():
    assert fd.map_year_month_to_financial_year(2021, 4) == '2021/22'
    assert fd.map_year_month_to_financial_year(2021, 'April') == '2021/22'
    assert fd.map_year_month_to_financial_year(2021, 3) == '2020/21'
    assert fd.map_year_month_to_financial_year(2021, 'March') == '2020/21'
    assert fd.map_year_month_to_financial_year(2022, 1) == '2021/22'
    assert fd.map_year_month_to_financial_year(2022, 'January') == '2021/22'
    assert fd.map_year_month_to_financial_year(2022, 12) == '2022/23'
    assert fd.map_year_month_to_financial_year(2022, 'December') == '2022/23'
