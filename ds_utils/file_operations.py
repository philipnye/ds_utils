# !/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect
import os
import re
from typing import Any, Callable, Literal, Optional, Union
import urllib.request

import pandas as pd

from ds_utils.log_operations import log_details


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


def get_sheet_info(file_path: str, filename: str, file_ending: str) -> dict():
    '''
        Get information about sheets in a file

        Parameters
            file_path: Path to folder
            filename: Name of file
            file_ending: File ending

        Returns
            sheet_info: Dictionary containing sheet names and number of sheets

        Notes
            None

        Future developments
            This could probably be optimised by using openpyxl (.xlsx) or xlrd (.xls)
            or ?? (.ods) rather than read_excel(), which reads the whole file into memory
            rather than just the sheet names
    '''
    if file_ending == '.csv' or file_ending == '.txt':
        n_sheets = 1
        sheet_names = None
    elif file_ending == '.xlsx':
        xl_file = pd.ExcelFile(file_path + '/' + filename)
        sheet_names = xl_file.sheet_names
        n_sheets = len(sheet_names)
    elif file_ending == '.ods':
        xl_file = pd.ExcelFile(file_path + '/' + filename, engine='odf')
        sheet_names = xl_file.sheet_names
        n_sheets = len(sheet_names)
    else:
        raise ValueError('File ending not recognised')

    sheet_info = {'n_sheets': n_sheets, 'sheet_names': sheet_names}

    return sheet_info


def read_excel_sheet_name_regex(
    file_path: str,
    filename: str,
    file_ending: str,
    regex_sheet_name: Union[bool, Literal['loose', 'strict']],
    **kwargs,
) -> Union[dict, pd.DataFrame]:
    '''
        Read in data from spreadsheet to a dataframe, using a regex
        to match the sheet name, and return all matches

        Parameters
            file_path: Path to folder
            filename: Name of file, including file ending
            file_ending: File ending of file
            regex_sheet_name: Which type of regex to apply. See
            read_data_file() for details of allowed value

            **kwargs: Additional arguments to pass to pandas' read_excel()

        Returns
            return_data: Dataframe of data, or dictionary of dataframes

        Notes
            None

        Future developments
            Make this consistent with read_excel() and replace first
            three args with path
    '''

    # Raise errors
    if file_ending not in ['.ods', '.xlsx']:
        raise ValueError('File ending not recognised: ' + file_ending)

    if 'sheet_name' not in kwargs.keys():
        raise ValueError('sheet_name must be provided')

    # Read sheet names of file
    sheet_names = get_sheet_info(file_path, filename, file_ending)['sheet_names']

    # Filter sheets
    if regex_sheet_name == 'loose' and len(sheet_names) == 1:
        matching_sheet_names = sheet_names
    elif regex_sheet_name or regex_sheet_name == 'strict':

        # Compile regex
        r = re.compile(kwargs['sheet_name'])

        # Get sheet names that match regex
        matching_sheet_names = list(
            filter(r.match, sheet_names)
        )

    # Save matching sheet names back to kwargs, converting
    # list to a string where only one element
    # NB: This is done so that we don't pass two sheet_name args
    # to read_excel() - one explicitly and the other as part of
    # **kwargs
    # NB: This is done so that read_excel() returns a df
    # rather than a dict of dfs
    if len(matching_sheet_names) == 1:
        kwargs['sheet_name'] = matching_sheet_names[0]
    else:
        kwargs['sheet_name'] = matching_sheet_names

    # Read in data
    return_data = pd.read_excel(
        file_path + '/' + filename,
        **kwargs,
    )

    return return_data


def download_file(
    url, data_folder_path,
    rename_data_file=False, new_filename=None,
    overwrite_existing=False, save_logs=False,
    logs_folder_path=None, logs_file_name='download_log.txt'
) -> None:
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
                logs_folder_path, logs_file_name,
                message=filename + ' downloaded from ' + url
            )

    else:
        if save_logs:
            log_details(
                logs_folder_path, logs_file_name,
                message=filename + ' already exists'
            )

    return


def read_data_file(
    file_path: str,
    filename: Union[str, float],
    file_ending: str,
    date_stamped: bool = False,
    **kwargs,
) -> Union[list, dict, pd.DataFrame]:
    '''
        Read in data from spreadsheet, flat file or pickle

        Parameters
            file_path: Path to folder
            filename: Name of file, including file ending
            file_ending: File ending of file
            date_stamped: Whether to look for datestamped files
            **kwargs: Additional arguments to pass to read_datestamped_file()
            or read_data_file()

        Returns
            return_data: Returns the data type returned by read_datestamped_file()
            or read_data_file()

        Notes
            None
        '''

    # Read in data
    if file_ending in ['.csv', '.ods', '.txt', '.xlsx'] and date_stamped:
        return_data = read_datestamped_data_file(
            file_path,
            filename,
            file_ending,
            read_function=read_spreadsheetflatfile(),
            **kwargs,
        )
    elif file_ending in ['.csv', '.ods', '.txt', '.xlsx']:
        return_data = read_data_file(
            file_path + '/' + filename,
            **kwargs,
        )
    elif file_ending == '.pkl' and date_stamped:
        return_data = read_datestamped_data_file(
            file_path,
            filename,
            file_ending,
            read_function=pd.read_pickle,
            **kwargs,
        )
    elif file_ending == '.pkl':
        return_data = pd.read_pickle(
            file_path + '/' + filename,
            **kwargs,
        )
    else:
        raise ValueError('File ending not recognised: ' + file_ending)

    return return_data


def read_spreadsheetflatfile(
    file_path: str,
    filename: Union[str, float],
    file_ending: str,
    encoding: Optional[Union[str, list]] = None,
    regex_sheet_name: Union[bool, Literal['loose', 'strict']] = False,
    drop_na: bool = False,
    force_to_dict: bool = False,
    save_logs: bool = False,
    logs_folder_path: Optional[str] = None,
    logs_file_name: str = 'read_log.txt',
    **kwargs,
) -> Union[dict, pd.DataFrame]:
    '''
        Read in data from spreadsheet or flat file, optionally logging
        the outcome

        Parameters
            file_path: Path to folder
            filename: Name of file, including file ending
            file_ending: File ending of file
            encoding: Encoding to use when reading a flat file. Where
            encoding is a list, the function will try each encoding
            in turn
            regex_sheet_name: Whether to use a regex to match sheet names.
            Where True or 'strict', strict matching is used - meaning the
            sheet name must match the regex patterns provided in the sheet_name
            kwarg exactly. Where 'loose', if the spreadsheet consists of
            one sheet only, this will be returned even if it doesn't match
            the regex pattern provided in sheet_name. 'strict' is the same
            as True, but is provided for clarity
            drop_na: Whether to apply pandas' dropna() before returning
            the result. This is useful for getting rid of empty or near-
            empty rows or columns, which can sometimes be the source of
            problems when attempting to work with the data
            force_to_dict: Whether to force the output to be a dictionary
            of dataframes, even if there is only one dataframe, as
            when we use read_csv() or when the file only contains one
            sheet
            logs_folder_path: Path to folder to save log to
            save_logs: Whether to log details of the read
            logs_file_name: Name of log file
            **kwargs: Additional arguments to pass to pandas' read_csv(),
            read_excel() or dropna()

        Returns
            return_data: Dataframe of data, or dictionary of dataframes

        Notes
            kwargs need to be split into those that are valid for
            the read functions and dropna() so that arguments that are
            not valid for a function aren't passed to it
    '''

    # Restrict kwargs to those that are valid for the functions
    # being used
    # Ref: https://stackoverflow.com/a/44052550/4659442
    if file_ending == '.csv' or file_ending == '.txt':
        read_sig = inspect.signature(pd.read_csv)
    elif file_ending == '.ods' or file_ending == '.xlsx':
        read_sig = inspect.signature(pd.read_excel)
    else:
        raise ValueError('File ending not recognised: ' + file_ending)

    read_kwargs = {
        key: value for key, value in kwargs.items()
        if key in read_sig.parameters.keys()
    }

    if drop_na:
        drop_na_sig = inspect.signature(pd.DataFrame.dropna)

        drop_na_kwargs = {
            key: value for key, value in kwargs.items()
            if key in drop_na_sig.parameters.keys()
        }

    # Read in data
    if file_ending in ['.csv', '.txt']:
        if encoding and isinstance(encoding, list):
            for enc in encoding:
                try:
                    return_data = pd.read_csv(
                        file_path + '/' + filename,
                        encoding=enc,
                        **read_kwargs,
                    )
                    break
                except UnicodeDecodeError:
                    continue
        else:
            return_data = pd.read_csv(
                file_path + '/' + filename,
                **read_kwargs,
            )
    elif file_ending in ['.ods', '.xlsx']:
        if regex_sheet_name:
            if 'sheet_name' not in read_kwargs.keys():
                raise ValueError('sheet_name must be provided where regex_sheet_name')

            return_data = read_excel_sheet_name_regex(
                file_path,
                filename,
                file_ending,
                regex_sheet_name=regex_sheet_name,
                **read_kwargs,
            )

        else:
            return_data = pd.read_excel(
                file_path + '/' + filename,
                **read_kwargs,
            )

    # Drop NaNs if required
    if drop_na:
        return_data.dropna(**drop_na_kwargs, inplace=True)

    # Log details if required
    if save_logs:
        log_details(
            logs_folder_path, logs_file_name,
            message=filename + ' read'
        )

    # Force result to be a dictionary if required
    if force_to_dict and not isinstance(return_data, dict):
        return_data = {0: return_data}

    return return_data


def read_datestamped_data_file(
    file_path: str,
    filename: Union[str, float],
    file_ending: str,
    file_choice: Literal['latest', 'all'],
    read_function: Callable,
    **kwargs,
) -> Union[list, dict, pd.DataFrame]:
    '''
        Read in data from a datestamped spreadsheet, flat file or pickle

        Parameters
            file_path: Path to folder
            filename: Name of file, including file ending, minus datestamp
            file_ending: File ending of file
            file_choice: Which file or files to read. If 'latest', only
            the latest file will be read. If 'all', all files will be read
            read_function: Function to use to read in the file
            **kwargs: Additional arguments to pass to read_function()

        Returns
            return_data: Returns a list where file_choice='latest' and read_function()
            returns a list. Returns a dict where file_choice='latest' and read_function()
            returns a dict, or returns a dict with keys as filenames and values one of
            several options where file_choice='all'. Returns a dataframe where
            file_choice='latest' and read_function() returns a dataframe.

        Notes
            This only works with dates formatted as %Y-%m-%d, the ISO standard format
            This can return multiple files, because we select files
            minus the datestamp, and then read in all files that match

        Future enhancements
            Add date_format argument, allowing the user to use date formats
            other than %Y-%m-%d
    '''

    # Strip file ending from filename
    # NB: We do this because we want to match all files that start
    # with the filename, then have a datestamp, then have the file
    # ending - we will not match files if we keep the file ending
    # after the first part of the filename
    filename = filename.split('.')[0]

    # Read names of all files in directory
    all_files = os.listdir(file_path)

    # Filter to only those that match the filename
    matching_files = [
        file for file in all_files
        if re.search(filename, file)
    ]
    if len(matching_files) == 0:
        raise FileNotFoundError('No files found with filename ' + filename)

    # Filter to only those that contain a datestamp in the expected format
    matching_files = [
        file for file in matching_files
        if re.search(r'\d{4}-\d{2}-\d{2}', file)
    ]
    if len(matching_files) == 0:
        raise FileNotFoundError(
            'No files found with a datestamp in the expected format, %Y-%m-%d'
        )

    # Select file to read
    if file_choice == 'latest':
        files_to_read = max(matching_files)
    elif file_choice == 'all':
        files_to_read = matching_files
    else:
        raise ValueError('file_choice not recognised: ' + file_choice)

    # Read in data
    if file_choice == 'latest':
        if read_function == pd.read_pickle:
            return_data = read_function(
                file_path + '/' + files_to_read
            )
        else:
            return_data = read_function(
                file_path,
                files_to_read,
                file_ending,
                **kwargs,
            )
    elif file_choice == 'all':
        if read_function == pd.read_pickle:
            return_data = {
                file: read_function(
                    file_path + '/' + file
                ) for file in files_to_read
            }
        else:
            return_data = {
                file: read_function(
                    file_path,
                    file,
                    file_ending,
                    **kwargs,
                ) for file in files_to_read
            }

    # Print filename(s) read
    if file_choice == 'latest':
        print('Read ' + files_to_read)
    else:
        if len(files_to_read) == 1:
            print('Read ' + files_to_read[0])
        else:
            print('Read:\n' + '\n'.join(files_to_read))

    return return_data


def read_sheet_names(
    file: Any
) -> list[str]:
    """
    Takes an input file and returns a list of sheet names

    Parameters:
        - file: A file that's been read in via
        streamlit's file_uploader

    Returns:
        - sheet_names: A list of sheet names

    Notes:
        - file can we any object that read_excel() can read
        - For files containing large amounts of data this can significantly
        increase the speed of reading sheet names
        Ref: https://stackoverflow.com/a/77771116/4659442

    """
    sheet_names = list(pd.read_excel(file, sheet_name=None, nrows=0).keys())

    return sheet_names
