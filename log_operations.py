# !/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd


def log_details(
    logs_folder_path: str,
    logs_file_name: str,
    message: str
) -> None:
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
        raise ValueError('logs_folder_path must be specified where logging is enabled')

    # Log details
    with open(logs_folder_path + '/' + logs_file_name, 'a') as log:
        log.write(
            str(pd.Timestamp.now()) + ' - ' +
            message + '\n'
        )

    return
