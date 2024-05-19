# !/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Literal, Optional, Union

import pandas as pd


def count_column_nulls(
    df: pd.DataFrame,
    groupby: Optional[list[str]] = None,
    transpose: bool = False,
    percent: bool = False,
    format: Optional[str] = None,
) -> pd.DataFrame:
    '''
    Count the number of nulls in each column of a datagrame

    Parameters
        - df: The dataframe to operate on
        - groupby: A column in df on which to group results
        - transpose: If True, df column names are row indexes. If False,
        df column names are columns
        - percent: If True, return the percentage of nulls in each column. If
        False, return the count of nulls in each column
        - format: A format string to apply to the results

    Returns
        - df_nulls: Counts of the number of nulls in each row

    Notes
        - Where groupby is not supplied we invert transpose, as df_nulls starts
        off in long/transposed form as it has been created from a Series
    '''

    if not groupby:
        if not percent:
            df_nulls = df.apply(lambda x: x.isnull().sum()).to_frame()
            transpose = not transpose
        else:
            df_nulls = df.apply(lambda x: x.isnull().mean()).to_frame()
            transpose = not transpose
    else:
        if not percent:
            df_nulls = df.groupby(groupby).apply(lambda x: x.isnull().sum())
        else:
            df_nulls = df.groupby(groupby).apply(lambda x: x.isnull().mean())

    if format:
        df_nulls = df_nulls.map(format.format)

    if transpose:
        return df_nulls.T
    else:
        return df_nulls


def flatten_nested_json_columns(df):
    """
    Flatten nested JSON in a DataFrame.

    Parameters:
        - df: DataFrame with nested JSON

    Returns:
        - df: DataFrame with flattened JSON

    Notes
        - This is an edited version of https://stackoverflow.com/a/61269285/4659442:
            - Renamed
            - Replaced all() is replaced with any(). This fixes a bug, whereby
            the function doesn't explode/normalize a column if there's one or more
            NaNs in it. It does rely on columns not containing a mix of types, however
            - Intermediate 'index' column dropped before return

    """
    df = df.reset_index()

    # Search for columns to explode/flatten
    s = (df.map(type) == list).any()
    list_columns = s[s].index.tolist()

    s = (df.map(type) == dict).any()
    dict_columns = s[s].index.tolist()

    while len(list_columns) > 0 or len(dict_columns) > 0:
        new_columns = []

        # Explode dictionaries horizontally, adding new columns
        for col in dict_columns:
            horiz_exploded = pd.json_normalize(df[col]).add_prefix(f'{col}.')
            horiz_exploded.index = df.index
            df = pd.concat([df, horiz_exploded], axis=1).drop(columns=[col])
            new_columns.extend(horiz_exploded.columns)

        # Explode lists vertically, adding new columns
        for col in list_columns:
            df = df.drop(columns=[col]).join(df[col].explode().to_frame())

            # Prevent combinatorial explosion when multiple
            # cols have lists or lists of lists
            df = df.reset_index(drop=True)
            new_columns.append(col)

        # check if there are still dict o list fields to flatten
        s = (df[new_columns].map(type) == list).any()
        list_columns = s[s].index.tolist()

        s = (df[new_columns].map(type) == dict).any()
        dict_columns = s[s].index.tolist()

    df.drop(columns=['index'], inplace=True)

    return df


def identify_first_numeric(
    df: pd.DataFrame,
    axis: Union[Literal[0], Literal[1], Literal['index'], Literal['columns']] = 0,
    exclude: Union[None, int, list, str] = None,
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

    # Define helper function
    def check_nonnan_numeric_in_column(column: pd.Series) -> bool:
        '''
        Check if a column contains any numeric values, excluding NaNs

        Parameters
            column: The column to check

        Returns
            result: True if the column contains any numeric values, otherwise False

        Notes
            This
        '''

        # Check if any values are numeric
        # NB: This checks the first character of each value,
        # in order to avoid picking up NaNs
        # Ref: https://stackoverflow.com/a/70613999/4659442
        result = column.astype(str).str[0].str.isnumeric().any()

        return result

    # Identify first numeric
    # NB: Explicitly checking if exclude is None, as we want to
    # treat the case where exclude is 0 differently
    header_count = df.apply(
        lambda x: check_nonnan_numeric_in_column(x) if exclude is None
        else check_nonnan_numeric_in_column(x) if (
            type(exclude) in [int, str] and not x.name == exclude
        )
        else check_nonnan_numeric_in_column(x) if (
            type(exclude) is list and x.name not in exclude
        )
        else None,
        axis=axis
    ).idxmax()

    return header_count


def identify_row_differences(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    keep_rows: Union[Literal['both'], Literal['first'], Literal['second']] = 'second',
    indicator_values: Optional[list] = None,
    drop_indicator_column: bool = True,
    **kwargs,
) -> pd.DataFrame:
    '''
    Identify rows in df2 that are not in df1

    Parameters
        df1: The first dataframe to compare
        df2: The second dataframe to compare
        keep_rows: Which rows to keep. If 'both', returns rows in the first
        and the second dataframe which differ. If 'first', returns rows in
        the first dataframe which are not in the second dataframe. If 'second',
        returns rows in the second dataframe which are not in the first dataframe
        indicator_values: A list of values to use for the indicator column
        drop_indicator_column: If True, drop the merge column
        **kwargs: Additional arguments to pass to the compare function

    Returns
        df_diff: A dataframe containing the differences between the two dataframes

    Notes
        None
    '''

    # Compare dataframes
    df_diff = df1.merge(
        df2,
        indicator=True,
        **kwargs
    )

    # Keep rows
    if keep_rows == 'both':
        df_diff = df_diff.loc[
            (df_diff['_merge'] == 'left_only') |
            (df_diff['_merge'] == 'right_only')
        ]
    elif keep_rows == 'first':
        df_diff = df_diff.loc[
            df_diff['_merge'] == 'left_only'
        ]
    elif keep_rows == 'second':
        df_diff = df_diff.loc[
            df_diff['_merge'] == 'right_only'
        ]
    else:
        raise ValueError('keep_rows must be one of both/first/second')

    # Re-map indicator values
    if indicator_values:
        df_diff['_merge'] = df_diff['_merge'].map({
            'left_only': indicator_values[0],
            'right_only': indicator_values[1]
        })

    # Drop merge column
    if drop_indicator_column:
        df_diff = df_diff.drop(columns='_merge')

    return df_diff


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


def turn_column_into_columns_values(
    df: pd.DataFrame,
    column: str,
    values: list[list],
    missing_values: Optional[list] = None,
    column_names: Optional[list] = None,
    strict: bool = True,
) -> pd.DataFrame:
    '''
    Turn a column into multiple columns, allocating values into specific columns

    Parameters
        - df: The dataframe to operate on
        - column: The column to split, which can be either an index or a non-index column
        - values: The values to split on, with these values ffilled to subsequent rows.
        The number of lists should be equal to the number of columns to split into. None
        is used as a catchall for all values that aren't otherwise specified
        - missing_values: The values to use - generally for totals - where the original
        shape of the data means no value is present
        - column_names: The names to use for the new columns
        - strict: If True, raise an error if the values are not in the column

    Returns
        - df: The dataframe with:
            - The column turned into a MultiIndex where column begins as an index column
            - The column split into multiple (non-index) columns where column begins
            as a column

    Notes
        - strict=False option not yet implemented
        - Only one catchall value can be supplied, and it can only be used for the
        last of the new columns

    Future developments
        - TODO: Test whether this functions as expected where:
            - df has an index and column is not part of the index
            - column is part of a MultiIndex
        - TODO: Fix handling of things with a header row MultiIndex. As
        currently implemented this probably leads to levels other than the
        first being dropped (see TODO flag below)
        - TODO: Change ffilling so that things are only ffilled within their group
        - Implement strict=False option, or remove strict argument
    '''

    # Convert index column to column where that's the column we want to operate on
    # NB: This is done so the rest of the function can operate either on something
    # that starts as an index column or otherwise
    if column in df.index.names:
        index_column_converted = True

        # Identify column position
        column_position = df.index.names.index(column)

        # Identify index columns before and after column we're operating on
        index_columns_before = df.index.names[:column_position]
        index_columns_after = df.index.names[column_position+1:]

        # Stash header row names
        if df.columns.names:
            header_row_names = df.columns.names

        df = df.reset_index()
    else:
        index_column_converted = False
        column_position = df.columns.get_loc(column)

    # Check if values all appear in column
    # NB: Nones - which occur where we've supplied a catchall case - are removed
    # before checking
    if strict and not all(
        item in df.loc[:, column].values
        for item in [item for sublist in values for item in sublist if item is not None]
    ):
        values_not_found = [
            item for item in [item for sublist in values for item in sublist if item is not None]
            if item not in df.loc[:, column].values
        ]
        raise ValueError(f'values {values_not_found} not in column {column}')
    elif not strict:
        raise NotImplementedError('strict=False not yet implemented')

    # Check that only one catchall value is supplied
    if values.count([None]) > 1:
        raise ValueError('only one catchall value can be supplied')

    # Check that catchall value is last
    if values.count([None]) == 1 and values[-1] != [None]:
        raise ValueError('catchall value must be last in list')

    # Duplicate columns into new df
    if not column_names:
        column_names = [f'column_{i}' for i in range(len(values))]
    df_new_columns = pd.concat(
        [df.loc[:, column]] * len(values),
        axis=1,
        ignore_index=True
    ).set_axis(labels=column_names, axis=1)

    # Set values to NaN where they're not in the list of values for each column
    # NB: inplace=True doesn't work on where() here
    # NB: This relies on our catchall case being the last column -
    # without that our isna() condition won't work
    for i, sublist in enumerate(values):

        # Handle normal case
        if sublist != [None]:
            df_new_columns[
                column_names[i]
            ] = df_new_columns[
                column_names[i]
            ].where(df_new_columns[column_names[i]].isin(sublist))

        # Handle catchall case - retaining all values not specified as belonging
        # in a different column
        else:
            other_columns = [c for c in df_new_columns.columns if c != column_names[i]]
            df_new_columns[
                column_names[i]
            ] = df_new_columns[
                column_names[i]
            ].where(
                df_new_columns[other_columns].isna().all(axis=1)
            )

    # Forward fill
    # NB: Can't use inplace=True as we're operating on selected columns only
    df_new_columns[other_columns] = df_new_columns[other_columns].ffill()

    # Supply missing values
    for i, value in enumerate(missing_values):
        if value is not None:
            df_new_columns[column_names[i]] = df_new_columns[column_names[i]].fillna(value)

    # Create copy of original dataframe
    # NB: We do this in order to safely drop the original column
    df_result = df.copy()

    # Drop original column
    df_result.drop(column, axis=1, inplace=True)

    # Split dataframe into columns before and after the deleted column
    df_result_before_column = df_result.iloc[:, :column_position]
    df_result_after_column = df_result.iloc[:, column_position:]

    # Prepend new columns and set column names
    # TODO: Fix handling of things with a header row MultiIndex
    df_result = pd.concat(
        [
            df_result_before_column,
            df_new_columns,
            df_result_after_column,
        ],
        ignore_index=True,
        axis=1
    ).reset_index(drop=True).set_axis(
        labels=(
            [
                c[0] if isinstance(c, tuple)
                else c
                for c in df_result_before_column.columns
            ] +
            [c for c in df_new_columns.columns] +
            [
                c[0] if isinstance(c, tuple)
                else c
                for c in df_result_after_column.columns
            ]
        ),
        axis=1
    )

    # Convert back to index columns if that's what we started with
    if index_column_converted:
        df_result.set_index(
            index_columns_before + column_names + index_columns_after,
            inplace=True
        )

        # Reapply header row names
        df_result.columns.names = header_row_names

    return df_result


def turn_column_into_columns(
    df: pd.DataFrame,
    column: str,
    split_by: Union[Union[Literal['sep']], Literal['values']] = 'values',
    sep: Optional[bool] = None,
    values: Optional[list[list]] = None,
    missing_values: Optional[list] = None,
    column_names: Optional[list] = None,
    strict: bool = True,
) -> pd.DataFrame:
    '''
    Turn a column into multiple columns, either splitting on a separator or by allocating
    values into specific columns

    Parameters
        df: The dataframe to operate on
        column: The column to split
        split_by: If 'values', split by values. If 'sep', split by separator
        sep: The separator to split on
        values: The values to split on
        missing_values: The values to use - generally for totals - where the original
        column_names: The names to use for the new columns
        strict: If True, raise an error if the separator/values are not in the column

    Returns
        df: The dataframe with the column split into multiple columns

    Notes
        - 'sep' option not yet implemented
        - See related turn_row_into_rows()

    Future developments
        - Implement 'sep' option
    '''
    # Check that split_by is valid
    if split_by not in ['values', 'sep']:
        raise ValueError('split_by must be one of values/sep')

    # Check if sep or values has been supplied
    if split_by == 'sep' and not sep:
        raise ValueError('sep must be supplied if split_by is sep')
    if split_by == 'values' and not values:
        raise ValueError('values must be supplied if split_by is values')

    if split_by == 'sep':
        raise NotImplementedError("split_by='sep' not yet implemented")
    elif split_by == 'values':
        return turn_column_into_columns_values(
            df=df,
            column=column,
            values=values,
            missing_values=missing_values,
            column_names=column_names,
            strict=strict,
        )


def turn_row_into_rows_sep(
    df: pd.DataFrame,
    row: str,
    sep: str,
    row_names: Optional[list] = None,
    strict: bool = True,
) -> pd.DataFrame:
    '''
    Turn a row into multiple rows, splitting on a separator

    Parameters
        - df: The dataframe to operate on
        - row: The row to split
        - sep: The separator to split on
        # - missing_values: The values to use - generally for totals - where the original
        # shape of the data means no value is present
        - row_names: The names to use for the new rows
        - strict: If True, raise an error if the separator is not in the row

    Returns
        - df: The dataframe with:
            - The row turned into a MultiIndex where row begins as an index row
            - The row split into multiple (non-index) rows where row begins
            as a row

    Notes
        None

    Future developments
        - TODO: This works where the row is a sole index row, but most likely not in other
        cases. It needs refactoring - probably keeping the 'Recreate dataframe' section but
        changing much of what comes before it, and possibly even then reworking things to make
        sure things with/without MultiIndex header columns work correctly
        - Implement missing_values argument?
    '''

    # Convert header row to row where that's the row we want to operate on
    # NB: This is done so the rest of the function can operate either on something
    # that starts as a header row or otherwise
    if row in df.columns.names:
        # TODO: Uncomment/remove
        # header_row_converted = True

        # Identify row position
        # NB: This is using Python's list index() method, rather than
        # something to do with the pandas index
        row_position = df.columns.names.index(row)

        # Identify header rows before and after row we're operating on
        # TODO: Uncomment/remove
        # header_rows_before = df.columns.names[:row_position]
        # header_rows_after = df.columns.names[row_position+1:]

        # Stash header column names
        # TODO: Uncomment/remove
        # if df.index.names:
        #     header_row_names = df.index.names

        df_no_index = df.copy().T.reset_index().T
    else:
        # TODO: Uncomment/remove
        # header_row_converted = False
        row_position = df.index.get_loc(row)

    # Check if separator appears in row
    # NB: dropna() is needed as otherwise the function will fail if we
    # have NaNs in the row, as we can't iterate on them
    if strict and not all(
        sep in value for value in df_no_index.loc[row].dropna().values.tolist()[0]
    ):
        raise ValueError(f'sep {sep} not in row {row}')
    elif not strict:
        raise NotImplementedError('strict=False not yet implemented')

    # Duplicate rows into new df
    new_row_count = len(row_names)

    if not row_names:
        row_names = [f'row_{i}' for i in range(new_row_count)]
    df_new_rows = pd.concat(
        [df_no_index.loc[row, :]] * new_row_count,
        axis=0,
        ignore_index=True
    ).set_axis(labels=row_names, axis=0)

    # Split row
    for row_name in row_names:
        df_new_rows.loc[row_name] = df_new_rows.loc[row_name].apply(
            lambda x: x.split(sep, maxsplit=1)[row_names.index(row_name)]
        )

    # Create copy of original dataframe
    # NB: We do this in order to safely drop the original row
    df_result = df_no_index.copy()

    # Drop original row
    df_result.drop(row, axis=0, inplace=True)

    # Split dataframe into rows before and after the deleted row
    df_result_after_row = df_result.iloc[row_position:, :]

    # Recreate dataframe
    df_result = pd.DataFrame(
        df_result_after_row.values,
        index=df.index,
        columns=pd.MultiIndex.from_frame(df_new_rows.T)
    )

    return df_result


def turn_row_into_rows(
    df: pd.DataFrame,
    row: int,
    sep: str,
    strict: bool = True,
) -> pd.DataFrame:
    '''
    Turn a row into multiple rows, splitting on a separator

    Parameters
        df: The dataframe to operate on
        row: The row to split
        sep: The separator to split on
        strict: If True, raise an error if the separator is not in the row

    Returns
        df: The dataframe with the row split into multiple rows

    Notes
        None

    Future developments
        Allow passing None as sep, in which case the function will
        try to identify the separator automatically, looking
        at the punctuation used most commonly in the row
    '''

    # Check if separator appears in row
    # NB: dropna() is needed as otherwise the function will fail if we
    # have NaNs in the row, as we can't iterate on them
    if strict and not any(
        sep in value for value in df.iloc[row].dropna().values.tolist()
    ):
        raise ValueError(f'sep {sep} not in row {row}')
    elif not strict and not any(
        sep in value for value in df.iloc[row].dropna().values.tolist()
    ):
        return df

    # Split columns into list
    # NB: col_list is a series of lists or NaNs where a column contains
    # only of NaNs. We've previously dropped columns where header rows
    # are entirely NaN - but because we're operating on a single header
    # row here it is possible to get NaNs
    col_lists = df.iloc[row].str.split(sep)

    # Make all items the same length
    # NB: We need to treat NaNs differently as len(NaN) results
    # in a TypeError. Columns will be lists where they are not NaN
    # NB: This is needed in order for df.explode to work
    max_len = max([len(x) for x in col_lists if x is not type(x) is list])

    col_lists = col_lists.apply(
        lambda x:
            x + [pd.NA] * (max_len - len(x)) if type(x) is list
            else [pd.NA] * max_len
    )

    df_new_rows = pd.DataFrame([col_lists],)

    df_new_rows = df_new_rows.explode(
        column=df_new_rows.columns.tolist()
    )

    # Create copy of original dataframe
    # NB: We do this in order to safely drop the original row
    df_result = df.copy()

    # Drop original row
    df_result.drop(row, axis=0, inplace=True)

    # Prepend new rows
    df_result = pd.concat(
        [df_new_rows, df_result],
        ignore_index=True
    ).reset_index(drop=True)

    return df_result


def change_rowcolumn_case(
    df: pd.DataFrame,
    indexes: list,
    case: Union[Literal['lower'], Literal['sentence'], Literal['title'], Literal['upper']],
    axis: Union[Literal[0], Literal[1], Literal['index'], Literal['columns']] = 0,
    excepted_strings: Optional[list] = None,
    inplace: bool = True,
) -> pd.DataFrame:
    '''
    Make strings in non-header rows/columns a specified title case, bar
    certain excepted substrings

    Parameters
        df: The dataframe to operate on. NB: This does not currently work
        on dfs with MultiIndexes
        indexes: A list of rows/columns to operate on, specified by index
        case: The case to convert to
        axis: The axis to operate on. If 0 or 'index', operate on rows.
        If 1 or 'columns', operate on columns
        excepted_strings: A list of strings to keep upper case
        inplace: If True, operate on the dataframe in place. If False, return
        a copy of the dataframe

    Returns
        df: If inplace, None. Otherwise, the edited dataframe

    Notes
        excepted_strings only matches full strings, not partial strings

    Future developments
        Handle dfs with MultiIndexes
    '''

    # Make a copy of the dataframe if not inplace
    if not inplace:
        df = df.copy()

    # Check that axis is valid
    if axis not in [0, 1, 'index', 'columns']:
        raise ValueError('axis must be one of 0/1/index/columns')

    # Check that case is valid
    if case not in ['lower', 'sentence', 'title', 'upper']:
        raise ValueError('case must be one of lower/upper/title/sentence')

    # Check that excepted_strings is valid
    if excepted_strings:
        if not isinstance(excepted_strings, list):
            raise TypeError('excepted_strings must be a list')
        if not all(isinstance(x, str) for x in excepted_strings):
            raise TypeError('all elements of excepted_strings must be strings')

    # Check that indexes is valid
    if indexes:
        if not isinstance(indexes, list):
            raise TypeError('indexes must be a list')

    # Make row/column values specified case
    if axis in [0, 'index']:
        df.loc[indexes] = df.loc[indexes, :].apply(
            lambda x: x.str.lower() if case == 'lower'
            else x.str.capitalize() if case == 'sentence'
            else x.str.title() if case == 'title'
            else x.str.upper() if case == 'upper'
            else None
        )
    elif axis in [1, 'columns']:
        df.loc[:, indexes] = df.loc[:, indexes].apply(
            lambda x: x.str.lower() if case == 'lower'
            else x.str.capitalize() if case == 'sentence'
            else x.str.title() if case == 'title'
            else x.str.upper() if case == 'upper'
            else None
        )

    # Make exceptions the case supplied
    # NB: This fixes the case of the exceptions supplied, as they
    # will have been converted to case in the previous step
    # NB: This only matches full strings, not partial strings
    # NB: Special handling is required where case == 'sentence' as
    # the exception can either appear at the start of the string
    # or part way through
    if excepted_strings:

        # Build dictionary of exceptions to correct
        if case == 'lower':
            dict_exceptions = {
                r'\b' + str(x.lower()) + r'\b': x for x in excepted_strings
            }
        elif case == 'sentence':
            dict_exceptions = {
                r'\b' + str(x.capitalize()) + r'\b': x for x in excepted_strings
            }
            dict_exceptions.update({
                r'\b' + str(x.lower()) + r'\b': x for x in excepted_strings
            })
        elif case == 'title':
            dict_exceptions = {
                r'\b' + str(x.title()) + r'\b': x for x in excepted_strings
            }
        elif case == 'upper':
            dict_exceptions = {
                r'\b' + str(x.upper()) + r'\b': x for x in excepted_strings
            }

        # Apply exceptions
        if axis in [0, 'index']:
            df.iloc[indexes] = df.iloc[indexes].apply(
                lambda x: x.replace(dict_exceptions, regex=True)
            )
        elif axis in [1, 'columns']:
            df.iloc[:, indexes] = df.iloc[:, indexes].apply(
                lambda x: x.replace(dict_exceptions, regex=True)
            )

    # Return results
    if inplace:
        return None
    else:
        return df
