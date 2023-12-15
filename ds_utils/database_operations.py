# !/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
from typing import Callable, Optional

from sqlalchemy import create_engine, engine, exc


def connect_sql_db(
    driver_version: Optional[str],
    server: str,
    database: str,
    authentication: str,
    username: str,
    dialect: str = 'mssql',
    driver: str = 'pyodbc',
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
        connection_string = (
            f'{dialect}+{driver}:///?odbc_connect=' +
            urllib.parse.quote_plus(
                f'DRIVER={driver_version};SERVER={server};DATABASE={database};' +
                f'UID={username};AUTHENTICATION={authentication};'
            )
        )

    # Create SQLAlchemy engine
    engine = create_engine(connection_string)

    return engine


def retry_sql_query(
    function: Callable,
    query: str,
    **kwargs: object
) -> object:
    """
    Attempt to execute a SQL query, retrying if a DBAPIError is raised

    Parameters
        - function: Function to use to query the database
        - query: SQL query to execute
        - **kwargs: Keyword arguments to pass to the function

    Returns
        - result: Result of the query

    Notes
        - None
    """
    try:
        result = function(query, **kwargs)
    except exc.DBAPIError:
        result = function(query, **kwargs)

    return result
