# !/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
from typing import Callable, Optional

from sqlalchemy import create_engine, engine, exc


def connect_sql_db(
    driver_version: Optional[str],
    server: str,
    database: str,
    authentication: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    dialect: str = 'mssql',
    driver: str = 'pyodbc',
    fast_executemany: Optional[bool] = True,
    **kwargs: object
) -> engine.base.Engine:
    """
    Connect to a SQL database using the supplied parameters

    Parameters
        - server: Server name
        - database: Database name
        - authentication: Authentication method
        - username: Username
        - dialect: Dialect
        - driver: Driver
        - **kwargs: Keyword arguments

    Returns
        - engine: SQLAlchemy engine

    Notes
        - None
    """

    # Build connection string
    if driver == 'pyodbc':

        if password:
            connection_string = (
                f'{dialect}+{driver}:///?odbc_connect=' +
                urllib.parse.quote_plus(
                    f'DRIVER={driver_version};SERVER={server};DATABASE={database};' +
                    f'UID={username};PWD={password};AUTHENTICATION={authentication};'
                )
            )
        else:
            connection_string = (
                f'{dialect}+{driver}:///?odbc_connect=' +
                urllib.parse.quote_plus(
                    f'DRIVER={driver_version};SERVER={server};DATABASE={database};' +
                    f'UID={username};AUTHENTICATION={authentication};'
                )
            )

    # Create SQLAlchemy engine
    engine = create_engine(
        connection_string,
        fast_executemany=fast_executemany,
        **kwargs
    )

    return engine


def retry_sql_function(
    function: Callable,
    *args: object,
    **kwargs: object
) -> object:
    """
    Attempt to execute a function involving a database connection,
    retrying if a DBAPIError is raised

    Parameters
        - function: Function to use to query the database
        - *args: Arguments to pass to the function
        - **kwargs: Keyword arguments to pass to the function

    Returns
        - result: Result of the query

    Notes
        - None
    """
    try:
        result = function(*args, **kwargs)
    except exc.DBAPIError:
        result = function(*args, **kwargs)

    return result
