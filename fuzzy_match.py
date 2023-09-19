# %%
# !/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Purpose
        Define fuzzy match, fuzzy merge functions
    Inputs
        None
    Outputs
        None
    Parameters
        None
    Notes
        None
'''

import pandas as pd

from thefuzz import process


# %%
# Define fuzzy matching function
def fuzzy_match(
    df_left, df_right, column_left, column_right, threshold=90, limit=1
):
    '''
        Fuzzy match two dataframes.

            Parameters:
                - df_left, df_right (df): The dataframes to match
                - column_left, column_right (str): Columns on which to match
                - threshold (int): A score below which any matches
                will be dropped
                - limit (int): The number of matches to find for each row
                in df_left

            Returns:
                - df_matches (df): A dataframe of matches with columns
                df_left_id, match_string, match_score, df_right_id

            Notes:
                - This adds matches as rows rather than columns, to preserve a
                tidy dataset
                - Passing a series to process.extract() yields results in the
                form [(<value>, <score>, <index>), ...].
                (Ref: https://stackoverflow.com/a/63725864/4659442)
                - Where df_right has a MultiIndex, the index is a tuple
    '''

    # Create a series of matches
    # Creates a series with id from df_left and column name _column_left_,
    # with _limit_ matches per item
    series_matches = df_left[column_left].apply(
        lambda x: process.extract(x, df_right[column_right], limit=limit)
    )

    # Convert matches to a tidy dataframe
    df_matches = series_matches.to_frame()
    df_matches = df_matches.explode(column_left)     # Convert list of matches to rows

    # Convert match tuple to columns
    if df_right.index.nlevels == 1:
        df_matches[
            ['match_string', 'match_score', 'df_right_id']
        ] = pd.DataFrame(
            df_matches[column_left].tolist(), index=df_matches.index
        )

    # Handle case where df_right has a MultiIndex
    # In this case, df_matches should have columns
    # ['match_string', 'match_score', 'df_right_<index_level1_name>',
    # 'df_right_<index_level2_name>', ...]
    else:
        df_matches[
            ['match_string', 'match_score', 'df_right_indexes']
        ] = pd.DataFrame(
            df_matches[column_left].tolist(), index=df_matches.index
        )
        # Convert index tuple to columns. NB: Creation of columns is done in two stages as list
        # comprehension can't be combined with other column-creation operations
        df_matches = pd.concat([
            df_matches,
            pd.DataFrame(
                df_matches['df_right_indexes'].tolist(),
                columns=[
                    'df_right_' + index_column
                    for index_column in df_right.index.names
                ],
                index=df_matches.index
            )
        ], axis=1)
        df_matches.drop('df_right_indexes', axis=1, inplace=True)      # Drop column of index tuples
    df_matches.drop(column_left, axis=1, inplace=True)      # Drop column of match tuples

    # Reset index, as in creating a tidy dataframe we've introduced multiple
    # rows per id, so that no longer functions well as the index
    if df_matches.index.name:
        index_name = df_matches.index.name     # Stash index name
    else:
        index_name = 'index'        # Default used by pandas
    df_matches.reset_index(inplace=True)
    # The previous index has now become a column: rename for ease of reference
    df_matches.rename(columns={index_name: 'df_left_id'}, inplace=True)

    # Drop matches below threshold
    df_matches.drop(
        df_matches.loc[df_matches['match_score'] < threshold].index,
        inplace=True
    )

    return df_matches


# %%
# Create dataframes
df_left = pd.DataFrame({
    'col_a': ['one', 'two', 'three', 'four', 'five'],
    'col_b': [1, 2, 3, 4, 5]
})
df_right = pd.DataFrame({
    'col_a': ['one', 'too', 'three', 'fours', 'five', 'five'],
    'col_b': ['a', 'b', 'c', 'd', 'e', 'f']
})

# %%
# Use function
df_matches = fuzzy_match(
    df_left,
    df_right,
    'col_a',
    'col_a',
    threshold=60,
    limit=2
)

# %%
df_matches

# %%
# Merge data
df_output = df_left.merge(
    df_matches,
    how='left',
    left_index=True,
    right_on='df_left_id'
).merge(
    df_right,
    how='left',
    left_on='df_right_id',
    right_index=True,
    suffixes=['_df_left', '_df_right']
)

# %%
df_output

# %%
# XXX For some reason the first merge operation wrecks the dataframe's index. Recreated from the
# value we have in the matches lookup table
df_output.set_index('df_left_id', inplace=True)

# Drop columns used in the matching
df_output = df_output[['col_a_df_left', 'col_b_df_left', 'col_b_df_right']]
df_output.index.name = 'id'

# %%
df_output


# %%
# Define fuzzy merging function
def fuzzy_merge(
    df_left, df_right, column_left, column_right, threshold=90, limit=1
):
    '''
        Fuzzy merge two dataframes.

            Parameters:
                - df_left, df_right (df): The dataframes to match
                - column_left, column_right (str): Columns on which to match
                - threshold (int): A score below which any matches
                will be dropped
                - limit (int): The number of matches to find for each row
                in df_left

            Returns:
                - df_matches (df): A dataframe of matches with columns
                df_left_id, match_string, match_score, df_right_id

            Notes:
                - This adds matches as rows rather than columns, to preserve a
                tidy dataset
                - Passing a series to process.extract() yields results in the
                form [(<value>, <score>, <index>), ...].
                (Ref: https://stackoverflow.com/a/63725864/4659442)
                - Where df_right has a MultiIndex, the index is a tuple
    '''

    # Fuzzy match datasets
    df_matches = fuzzy_match(
        df_left,
        df_right,
        column_left,
        column_right,
        threshold=threshold,
        limit=limit
    )

    # Merge data
    df_output = df_left.merge(
        df_matches,
        how='left',
        left_index=True,
        right_on='df_left_id'
    ).merge(
        df_right,
        how='left',
        left_on='df_right_id',
        right_index=True,
        suffixes=['_df_left', '_df_right']
    )

    # Recreate index
    df_output.set_index('df_left_id', inplace=True)

    # Drop columns used in the matching
    df_output = df_output[['col_a_df_left', 'col_b_df_left', 'col_b_df_right']]
    df_output.index.name = 'id'

    return df_output


# %%
# Use fuzzy merge function
df_output = fuzzy_merge(
    df_left,
    df_right,
    'col_a',
    'col_a',
    threshold=60,
    limit=2
)
