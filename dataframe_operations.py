# #!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Literal, Optional, Union

import pandas as pd


def identify_first_numeric(
    df: pd.DataFrame,
    axis: Union[Literal[0], Literal[1], Literal['index'], Literal['columns']] = 0,
) -> int:
    '''
    Identify the first non-NaN numeric column or row in a dataframe

    Parameters
        df: The dataframe to operate on
        axis: The axis to search for the first numeric column or row.
        If 0 or 'index', search for the first numeric row. If 1 or 'columns',
        search for the first numeric row

    Returns
        header_count: The index of the first numeric column or row

    Notes
        This can be used to identify where the data-proper starts, and
        is often useful before setting an index or MultiIndex
        This does not pick up NaNs due to the application of astype(str)
    '''

    header_count = df.apply(
        lambda x: x.astype(str).str[0].str.isnumeric().any(),
        axis=axis
    ).idxmax()

    return header_count


def create_default_header_names(
    header_count: int,
    axis: Union[Literal[0], Literal[1], Literal['index'], Literal['columns']] = 0,
) -> list:
    '''
    Create a list of default header row or column names

    Parameters
        header_count: The number of header rows or columns to create
        axis: The axis to create the header names for. If 0 or 'index',
        create header names for rows. If 1 or 'columns', create header names
        for columns

    Returns
        header_names: A list of header names

    Notes
        None
    '''

    if axis in [0, 'index']:
        header_names = [f'row_{i}' for i in range(header_count)]
    elif axis in [1, 'columns']:
        header_names = [f'column_{i}' for i in range(header_count)]
    else:
        raise ValueError('axis must be one of 0/1/index/columns')

    return header_names


def create_multiindex(
    df: pd.DataFrame,
    header_row_count: int,
    header_column_count: int,
    header_row_names: Optional[list] = None,
    header_column_names: Optional[list] = None,
) -> pd.DataFrame:
    '''
    Create a MultiIndex for a dataframe from rows and columns
    provided to the function

    Parameters
        df: The dataframe to operate on
        header_row_count: The number of rows to use for the MultiIndex
        header_column_count: The number of columns to use for the MultiIndex
        header_row_names: The names to use for the MultiIndex rows
        header_column_names: The names to use for the MultiIndex columns

    Returns
        df: The dataframe with the MultiIndex set

    Notes
        Any existing index or columns are implicitly dropped
        This function does not have an inplace option, as the way the
        dataframe is recreated means that inplace=True would not work
    '''

    # Create header row, column names if not provided
    if not header_row_names:
        header_row_names = create_default_header_names(header_row_count, axis=0)
    if not header_column_names:
        header_column_names = create_default_header_names(header_column_count, axis=1)

    # Define MultiIndex for header columns
    # This is contents of header_column_count, excluding rows
    # up to last header row, turned into a MultiIndex
    multi_index = pd.MultiIndex.from_arrays(
        [
            df.iloc[header_row_count:, x].values
            for x in range(0, header_column_count)
        ],
        names=header_column_names
    )

    # Define MultiIndex for header rows
    # This is contents of header_row_count, excluding columns
    # up to last header column, turned into a MultiIndex
    multi_columns = pd.MultiIndex.from_arrays(
        [
            df.iloc[x, header_column_count:].values
            for x in range(0, header_row_count)
        ],
        names=header_row_names
    )

    # Define data portion of source table
    data = df.iloc[
        header_row_count:,
        header_column_count:
    ]

    # Recreate dataframe
    df = pd.DataFrame(
        data.values,
        index=multi_index,
        columns=multi_columns
    )

    return df


def forward_fill_headers(
    df: pd.DataFrame,
    header_count: int,
    axis: Union[Literal[0], Literal[1], Literal['index'], Literal['columns']] = 0,
    inplace: bool = False,
) -> pd.DataFrame:
    '''
    Forward fill all header rows/columns in a dataframe, filling rows/columns
    recursively and only filling them where there is a value in the previous
    row/column

    Parameters
        df: The dataframe to operate on
        header_count: The number of header rows/columns to forward fill
        axis: The axis to forward fill. If 0 or 'index', forward fill rows.
        If 1 or 'columns', forward fill columns
        inplace: If True, operate on the dataframe in place. If False, return
        a copy of the dataframe

    Returns
        df: The dataframe with forward filled headers

    Notes
        Ref: https://stackoverflow.com/a/72041766/4659442
        This assumes that the index/columns are numbers
    '''

    # Make a copy of the dataframe if not inplace
    if not inplace:
        df = df.copy()

    # Determine index/columns min
    # NB: This is needed as in the next step we can't assume
    # that index/column row numbering starts at zero -
    # handling the case where rows have been dropped
    if axis in [0, 'index']:
        header_min = df.index.min()
    elif axis in [1, 'columns']:
        header_min = df.columns.min()
    else:
        raise ValueError('axis must be one of 0/1/index/columns')

    # Forward fill first header
    if header_count > 0:
        if axis in [0, 'index']:
            df.loc[header_min].ffill(inplace=True)
        elif axis in [1, 'columns']:
            df.loc[:, header_min].ffill(inplace=True)
    else:
        raise ValueError('header_count must be > 0')

    # Forward fill subsequent headers, if there are any
    if header_count > 1:
        if axis in [0, 'index']:
            for i in range(header_min+1, header_min+header_count):
                df.loc[i] = df.loc[
                    :,
                    df.loc[i-1].notna()
                ].T.groupby(i-1, sort=False)[[i]].ffill()[i]
        elif axis in [1, 'columns']:
            for i in range(header_min+1, header_min+header_count):
                df.loc[:, i] = df.loc[
                    df.loc[:, i-1].notna(),
                    :
                ].groupby(i-1, sort=False)[[i]].ffill()[i]

    # Return dataframe
    if inplace:
        return None
    else:
        return df


def check_number_rowscolumns(
    df: pd.DataFrame,
    min: int,
    max: int,
    axis: Union[Literal[0], Literal[1], Literal['index'], Literal['columns']] = 0,
) -> bool:
    '''
    Check that the number of rows/columns in the df is within a specified range

    Parameters
        df: The dataframe to operate on
        min: The minimum number of rows/columns
        max: The maximum number of rows/columns

    Returns
        result: True if the number of rows/columns is within the specified range,
        otherwise False

    Notes
        This checks that the row/column count is within the specified range,
        inclusive
    '''

    # Check that min is an integer
    if not isinstance(min, int):
        raise TypeError('min must be an integer')

    # Check that max is an integer
    if not isinstance(max, int):
        raise TypeError('max must be an integer')

    # Check that min, max is >= 0
    if min < 0 or max < 0:
        raise ValueError('min and max must be >= 0')

    # Check that min <= max
    if min > max:
        raise ValueError('min must be <= max')

    # Check that min <= number of rows <= max
    if axis in [0, 'index']:
        result = min <= df.shape[0] <= max
    elif axis in [1, 'columns']:
        result = min <= df.shape[1] <= max
    else:
        raise ValueError('axis must be one of 0/1/index/columns')

    return result
