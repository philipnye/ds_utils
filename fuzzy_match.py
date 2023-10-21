# !/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Hashable

import pandas as pd
from rapidfuzz import process, utils


# Define fuzzy matching function
def fuzzy_match(
    df_left: pd.DataFrame,
    df_right: pd.DataFrame,
    column_left: Hashable,
    column_right: Hashable,
    score_cutoff: int = 90,
    limit: int = 1,
    clean_strings: bool = True,
    drop_na: bool = True,
) -> pd.DataFrame:
    '''
        Fuzzy match two dataframes.

            Parameters:
                - df_left: The base dataframe which we want to find matches
                for
                - df_right: The dataframe in which we want to look for matches
                to values in df_left
                - column_left, column_right: Columns on which to match
                - score_cutoff: A score below which any matches
                will be dropped
                - limit: The number of matches to find for each row
                in df_left
                - clean_strings: Whether to apply rapidfuzz's default_process
                processor, which converts strings to lowercase, removes
                non-alphanumeric characters and trims whitespace
                - drop_na: Whether to drop rows where no matches are found

            Returns:
                - df_matches: A dataframe of matches with a MultiIndex
                consisting of the ids from df_left and df_right, and
                columns match_string, match_score. Where df_left or
                df_right has a MultiIndex, the relevant index is a tuple

            Notes:
                - This adds matches as rows rather than columns, to ensure a
                tidy dataset
                - The maximum number of matches that can be returned is
                len(df_left) * limit
                - None, np.nan and pd.NA in column_left or column_right are
                considered not to match with anything
    '''
    # Replace pd.NA with None as rapidfuzz doesn't currently handle pd.NA
    # Ref: https://github.com/maxbachmann/RapidFuzz/issues/349
    df_left = df_left.replace({pd.NA: None})
    df_right = df_right.replace({pd.NA: None})

    # Create a series of matches
    # NB: Passing a series to process.extract() yields a series named column_left
    # where the index is the index of df_left and the values are lists of tuples,
    # of the form [(<value>, <score>, <index>), ...] - in this case the match
    # value from df_right, the match score and index of df_right. Where df_right
    # has a MultiIndex, the index is a tuple
    # (ref: https://stackoverflow.com/a/63725864/4659442)
    series_matches = df_left[column_left].apply(
        lambda x: process.extract(
            x, df_right[column_right],
            limit=limit, score_cutoff=score_cutoff,
            processor=utils.default_process if clean_strings else None
        )
    )

    # Drop empty matches
    if drop_na:
        series_matches = series_matches[
            series_matches.apply(lambda x: len(x) > 0)
        ]

    # Convert matches to a dataframe in long form
    df_matches = series_matches.to_frame()
    df_matches.index.name = 'df_left_id'
    df_matches = df_matches.explode(column_left)

    # Convert match tuple to columns
    df_matches = pd.DataFrame(
        index=df_matches.index,
        data=df_matches[column_left].tolist(),
        columns=['match_string', 'match_score', 'df_right_id']
    )

    # Convert indexes to tuples where df_left and/or df_right have MultiIndexes
    # as otherwise any subsequent merging will fail
    # NB: This is done before adding df_right_id to the index, as otherwise
    # df_right_id would become part of df_left_id
    # NB: Flattening df_matches index is only needed where df_left has a
    # MultiIndex, as in the case where df_right has a MultiIndex the df_right
    # index will have been a single, named column in df_matches
    if df_left.index.nlevels > 1:
        df_matches.index = pd.MultiIndex.to_flat_index(df_matches.index)
        df_matches.index.name = 'df_left_id'

    # Add df_right id to index, meaning it will consist of df_left id and
    # df_right id
    # NB: This will be a unique index, as long as df_left and df_right have
    # unique indexes
    df_matches.set_index(['df_right_id'], append=True, inplace=True)

    return df_matches


# Define fuzzy merging function
def fuzzy_merge(
    df_left: pd.DataFrame,
    df_right: pd.DataFrame,
    column_left: Hashable,
    column_right: Hashable,
    score_cutoff: int = 90,
    limit: int = 1,
    clean_strings: bool = True,
    drop_na: bool = True
):
    '''
        Fuzzy merge two dataframes.

            Parameters:
                - df_left: The base dataframe which we want to find matches
                for
                - df_right: The dataframe in which we want to look for matches
                to values in df_left
                - column_left, column_right: Columns on which to match
                - score_cutoff: A score below which any matches
                will be dropped
                - limit: The number of matches to find for each row
                in df_left
                - clean_strings: Whether to apply rapidfuzz's default_process
                processor, which converts strings to lowercase, removes
                non-alphanumeric characters and trims whitespace

            Returns:
                - df_matches: A dataframe of matches with a MultiIndex
                consisting of the ids from df_left and df_right, and
                columns match_string, match_score. Where df_left or
                df_right has a MultiIndex, the relevant index is a tuple

            Notes:
                - This adds matches as rows rather than columns, to ensure a
                tidy dataset
                - The merge carried out is a left merge, so all rows from
                df_left are retained
                - The maximum number of matches that can be returned is
                len(df_left) * limit
    '''

    # Fuzzy match datasets
    df_matches = fuzzy_match(
        df_left,
        df_right,
        column_left,
        column_right,
        score_cutoff=score_cutoff,
        limit=limit,
        clean_strings=clean_strings,
        drop_na=drop_na
    )

    # Convert indexes to tuples where df_left and/or df_right have MultiIndexes
    # as otherwise any subsequent merging will fail
    # NB: We do this on copies of df_left and/or df_right, and use these in the
    # # subsequent merge, so that we don't modify the original dataframes
    df_left_flat_index = df_left.copy()
    df_right_flat_index = df_right.copy()

    if df_left.index.nlevels > 1:
        df_left_flat_index.index = pd.MultiIndex.to_flat_index(df_left_flat_index.index)
        df_left_flat_index.index.name = 'df_left_id'
    if df_right.index.nlevels > 1:
        df_right_flat_index.index = pd.MultiIndex.to_flat_index(df_right_flat_index.index)

    # Merge data
    df_output = df_left_flat_index.merge(
        df_matches,
        how='left',
        left_index=True,
        right_on='df_left_id'
    ).merge(
        df_right_flat_index,
        how='left',
        left_on='df_right_id',
        right_index=True,
        suffixes=['_df_left', '_df_right']
    )

    return df_output
