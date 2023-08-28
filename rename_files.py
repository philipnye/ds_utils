#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

os.chdir(
    'U:/DATA/Politics and Parliament/Ministers - Meetings/Source/Edited data'
)

for fname in os.listdir('.'):
    if os.path.isfile(fname):
        # Append something to Word document file name
        # if fname.endswith('.docx'):
        #     os.rename(fname, fname.replace('.docx', ' guide.docx'))

        # Reverse two elements of file name
        fname_quarter = fname.split('-')[1]
        fname_year = fname.split('-')[2]
        fname_new_list = (
            [fname.split('-')[0], fname_year, fname_quarter] +
            fname.split('-')[3:]
        )
        fname_new = '-'.join(fname_new_list)
        os.rename(fname, fname_new)
