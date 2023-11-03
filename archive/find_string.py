#!/usr/bin/env python
# -*- coding: utf-8 -*-

# %%
import os

os.chdir(
    'U:/DATA/Politics and Parliament/'
    'Ministers - Ministers database/scripts'
)

for fname in os.listdir('.'):
    if os.path.isfile(fname):
        with open(fname, 'r', encoding='cp850') as f:
            file_contents = f.read()
            if ' rn' in file_contents:
                print(fname)

# %%
