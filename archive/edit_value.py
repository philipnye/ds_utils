# %%
# !/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Purpose
        Select values using regex and edit
    Inputs
        XXX
    Outputs
        XXX
    Parameters
        XXX
    Notes
        XXX
'''

import os
import re

# %%
# SET PARAMETERS
root_dir = (
    'C:/Users/nyep/Institute for Government/Research - Public services/' +
    'Projects/Performance Tracker/Scripts'
)

pattern = r"(.*skip_rows_up_to': *)(\d*)"

public_services = [
    'Adult social care', 'Children\'s social care', 'Criminal courts',
    'Neighbourhood services', 'Prisons', 'Schools'
]

# %%
# Iterate over folders
for public_service in public_services:
    folder_path = root_dir + '/' + public_service

    # Change folder
    os.chdir(folder_path)

    # Iterate over files in folder
    for fname in os.listdir('.'):
        if os.path.isfile(fname):

            # Select data item parameter files
            if 'dataitemparameters.py' in fname:
                print(fname)

                # Open file and edit values selected in regex
                with open(fname, 'r') as f:
                    file_contents = f.read()
                    file_contents_edited = re.sub(
                        pattern,
                        lambda x: x.group(1) + str(int(x.group(2)) + 1),
                        file_contents
                    )

                # Save results
                with open(fname, 'w') as file:
                    file.write(file_contents_edited)

# %%
