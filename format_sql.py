#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

for fname in os.listdir('.'):
    if os.path.isfile(fname):
        if fname.endswith('.sql'):
            print(fname)
            with open(fname, 'r') as f:
                file_contents = f.read()
            file_contents = re.sub(
                'select ',
                r'select\r\n\t',
                file_contents,
                flags=re.IGNORECASE
            )
            file_contents = re.sub(
                'delete ',
                r'delete\r\n\t',
                file_contents,
                flags=re.IGNORECASE
            )
            file_contents = re.sub(
                'insert into ',
                r'insert into\r\n\t',
                file_contents,
                flags=re.IGNORECASE
            )
            file_contents = re.sub(
                'union ',
                r'union\r\n\t',
                file_contents,
                flags=re.IGNORECASE
            )
            file_contents = re.sub(
                'where ',
                r'where\r\n\t',
                file_contents,
                flags=re.IGNORECASE
            )
            file_contents = re.sub(
                'group by ',
                r'group by\r\n\t',
                file_contents,
                flags=re.IGNORECASE
            )
            file_contents = re.sub(
                'having ',
                r'having\r\n\t',
                file_contents,
                flags=re.IGNORECASE
            )
            file_contents = re.sub(
                'order by ',
                r'order by\r\n\t',
                file_contents,
                flags=re.IGNORECASE
            )
            file_contents = re.sub(
                ' inner join ',
                r'\r\n\tinner join ',
                file_contents,
                flags=re.IGNORECASE
            )
            file_contents = re.sub(
                ' left join ',
                r'\r\n\tleft join ',
                file_contents,
                flags=re.IGNORECASE
            )
            file_contents = re.sub(
                ' right join ',
                r'\r\n\tright join ',
                file_contents,
                flags=re.IGNORECASE
            )
            file_contents = re.sub(
                ' on ',
                r' on\r\n\t\t',
                file_contents,
                flags=re.IGNORECASE
            )
            file_contents = re.sub(
                '(, |,)',
                r',\r\n\t',
                file_contents,
                flags=re.IGNORECASE
            )
            file_contents = re.sub(
                r'(\[|\])',
                r'',
                file_contents,
                flags=re.IGNORECASE
            )
            file_contents = re.sub(
                '#',
                '\'',
                file_contents,
                flags=re.IGNORECASE
            )
            file_contents = re.sub(
                ' as ',
                ' ',
                file_contents,
                flags=re.IGNORECASE
            )
            file_contents = file_contents.lower()
            with open(fname, 'w') as file:
                file.write(file_contents)
