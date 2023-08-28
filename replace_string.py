#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

os.chdir(
    'U:/DATA/Politics and Parliament/'
    'Ministers - Ministers database/scripts'
)

replacements_list = [{
    'target_string':
        'This needs to be strictly greater than, otherwise we would pick up'
        'both the new and the old person characteristics where the change'
        'happened on the appointment end_date',
    'replacement_string':
        'This needs to be strictly greater than, otherwise we would pick up'
        'both the new and the old person characteristics where the change'
        'happened on the appointment start_date'
}]

for fname in os.listdir('.'):
    if os.path.isfile(fname):
        # if fname in ('temp.sql', 'temp_reshuffles.sql', 'temp2.sql'):
        if fname.endswith('.sql'):
            print(fname)
            with open(fname, 'r') as f:
                file_contents = f.read()
                for replacement in replacements_list:
                    file_contents = file_contents.replace(
                        replacement['target_string'],
                        replacement['replacement_string']
                    )
            with open(fname, 'w') as file:
                file.write(file_contents)
