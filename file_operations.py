# #!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import urllib.request

import pandas as pd
from typing import Optional, Union


def create_folder(path: str) -> None:
    '''
        Create a folder if it doesn't already exist

        Parameters
            path: Path to folder to create

        Returns
            None

        Notes
            None
    '''
    if not os.path.exists(path):
        os.mkdir(path)

    return


def extract_filetype(
    filename: Union[str, float],
    with_dot: bool = False
) -> Optional[str]:
    '''
        Extract filetype from filename

        Arguments
            - filename: The name of the file

        Returns
            filetype: The filetype ending

        Notes
            None
    '''
    # Handle NaNs
    if pd.isnull(filename):
        return pd.NA

    # Handle normal cases
    else:
        filetype = filename.split('.')[-1]

        if with_dot:
            filetype = '.' + filetype

        return filetype


def download_file(
    url, data_folder_path,
    logs_folder_path, logs_file_name='download_log.txt',
    rename_data_file=False, new_filename=None,
    overwrite_existing=False, log_details=True
):
    '''
        Download a file from a URL, checking first whether it already
        exists and optionally renaming it, and logging the outcome

        Parameters
            - url: URL of file to download
            - data_folder_path: Path to folder to save file to
            - logs_folder_path: Path to folder to save log to
            - logs_file_name: Name of log file
            - rename_data_file: Whether to rename the data file
            - new_filename: New filename to use if renaming
            - overwrite_existing: Whether to overwrite existing file
            - log_details: Whether to log details of the download

        Returns
            None

        Notes
            - Both data_folder_path and logs_folder_path must exist,
            otherwise an error will be thrown
    '''

    # Change directory
    os.chdir(data_folder_path)

    # Extract the file
    filename = url.split('/')[-1]

    # Rename the file if required
    if rename_data_file:
        filename = new_filename

    # Remove existing file if required
    if os.path.exists(filename) and overwrite_existing:
        os.remove(filename)

    # Download file if required and log details of download if required
    if not os.path.exists(filename):

        # Download file
        urllib.request.urlretrieve(url, filename)

        # Log details if required
        if log_details:
            os.chdir(logs_folder_path)
            with open(logs_file_name, 'a') as log:
                log.write(
                    str(pd.Timestamp.now()) + ' - ' +
                    filename + ' downloaded from ' + url + '\n'
                )
    else:
        if log_details:
            os.chdir(logs_folder_path)
            with open(logs_file_name, 'a') as log:
                log.write(
                    str(pd.Timestamp.now()) + ' - ' +
                    filename + ' already exists\n'
                )

    return
