# #!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect
import os
from typing import Optional, Union
import urllib.request

import pandas as pd


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


def extract_filename(
    url: Union[str, float],
    with_extension: bool = True
) -> Optional[str]:
    '''
        Extract filetype from URL

        Parameters
            - url: A link to the file

        Returns
            filename: The name of the file

        Notes
            None
    '''
    # Handle NaNs
    if pd.isnull(url):
        return pd.NA

    # Handle normal cases
    else:
        url = url.split('/')[-1]

        if not with_extension:
            url = url.split('.')[0]

        return url


def extract_filetype(
    filename: Union[str, float],
    with_dot: bool = False,
    lowercase: bool = True
) -> Optional[str]:
    '''
        Extract filetype from filename

        Parameters
            - filename: The name of the file
            - with_dot: Whether to include the dot in the output
            - lowercase: Whether to return the filetype in lowercase

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

        if lowercase:
            filetype = filetype.lower()

        return filetype


def log_details(
    filename: str,
    logs_folder_path: str,
    logs_file_name: str,
    message: str
):
    '''
        Log details of file actions

        Parameters
            filename: Name of file
            logs_folder_path: Path to folder to save log to
            logs_file_name: Name of log file
            message: Message to log, along with filename

        Returns
            None

        Notes
            None
    '''

    # Change directory
    if logs_folder_path is None:
        raise ValueError('logs_folder_path must be specified where save_logs=True')
    else:
        os.chdir(logs_folder_path)

    # Log details
    with open(logs_file_name, 'a') as log:
        log.write(
            str(pd.Timestamp.now()) + ' - ' +
            filename + ' ' + message + '\n'
        )

    return


def download_file(
    url, data_folder_path,
    rename_data_file=False, new_filename=None,
    overwrite_existing=False, save_logs=False,
    logs_folder_path=None, logs_file_name='download_log.txt'
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
            - save_logs: Whether to log details of the download

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
        if save_logs:
            log_details(
                filename, logs_folder_path, logs_file_name,
                message='downloaded from ' + url
            )

    else:
        if save_logs:
            log_details(
                filename, logs_folder_path, logs_file_name,
                message='already exists'
            )

    return


def read_data_file(
    file_path: str,
    filename: Union[str, float],
    file_ending: str,
    force_to_dict: bool = False,
    save_logs: bool = False,
    logs_folder_path: Optional[str] = None,
    logs_file_name: str = 'read_log.txt',
    **kwargs,
) -> Union[dict, pd.DataFrame]:
    '''
        Read in data from spreadsheet or flat file to a dataframe,
        optionally logging the outcome

        Parameters
            file_path: Path to file
            filename: Name of file, including file ending
            file_ending: File ending of file
            force_to_dict: Whether to force the output to be a dictionary
            of dataframes, even if there is only one dataframe, as
            when we use read_csv() or when the file only contains one
            sheet
            logs_folder_path: Path to folder to save log to
            save_logs: Whether to log details of the read
            logs_file_name: Name of log file
            **kwargs: Additional arguments to pass to pandas read_csv()
            or read_excel()

        Returns
            return_data: Dataframe of data, or dictionary of dataframes

        Notes
            None
    '''

    # Restrict kwargs to those that are valid for the function
    # being used
    # ref: https://stackoverflow.com/a/44052550/4659442
    if file_ending == '.csv' or file_ending == '.txt':
        sig = inspect.signature(pd.read_csv)
    elif file_ending == '.ods' or file_ending == '.xlsx':
        sig = inspect.signature(pd.read_excel)
    else:
        raise ValueError('File ending not recognised: ' + file_ending)

    kwargs = {
        key: value for key, value in kwargs.items()
        if key in sig.parameters.keys()
    }

    # Read in data
    if file_ending == '.csv':
        return_data = pd.read_csv(
            file_path + '/' + filename,
            **kwargs,
        )
    elif file_ending == '.ods':
        return_data = pd.read_excel(
            file_path + '/' + filename,
            engine='odf',
            **kwargs,
        )
    elif file_ending == '.txt':
        return_data = pd.read_csv(
            file_path + '/' + filename,
            sep='\t',
            **kwargs,
        )
    elif file_ending == '.xlsx':
        return_data = pd.read_excel(
            file_path + '/' + filename,
            **kwargs,
        )
    else:
        raise ValueError('File ending not recognised: ' + file_ending)

    # Log details if required
    if save_logs:
        log_details(
            filename, logs_folder_path, logs_file_name,
            message='read'
        )

    # Force result to be a dictionary if required
    if force_to_dict and not isinstance(return_data, dict):
        return_data = {0: return_data}

    return return_data
