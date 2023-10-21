# !/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import pandas.testing as pdt
import pytest

from fuzzy_match import fuzzy_match


def test_simple_case():
    '''
        Test non-empty, non-MultiIndex df_left, non-empty, non-MultiIndex df_right,
        where matches exist
    '''

    # Create dataframes
    df_left = pd.DataFrame({
        'col_a': ['one', 'two', 'three', 'four', 'five'],
        'col_b': [1, 2, 3, 4, 5]
    })
    df_right = pd.DataFrame({
        'col_a': ['one', 'too', 'three', 'fours', 'five', 'five'],
        'col_b': ['a', 'b', 'c', 'd', 'e', 'f']
    })

    # Use function
    df_matches = fuzzy_match(
        df_left,
        df_right,
        'col_a',
        'col_a',
        score_cutoff=60,
        limit=2
    )

    # Add expected output
    df_expected = pd.DataFrame(
        index=pd.MultiIndex.from_arrays(
            [
                [0, 1, 2, 3, 4, 4],
                [0, 1, 2, 3, 4, 5],
            ],
            names=['df_left_id', 'df_right_id']
        ),
        data={
            'match_string': ['one', 'too', 'three', 'fours', 'five', 'five'],
            'match_score': [100.000000, 66.666667, 100.000000, 88.888889, 100.000000, 100.000000],
        }
    )

    # Test output
    pdt.assert_frame_equal(df_matches, df_expected)

    return


def test_multiindex_df_left():
    '''
        Test non-empty, MultiIndex df_left, non-empty, non-MultiIndex df_right,
        where matches exist
    '''

    # Create dataframes
    df_left = pd.DataFrame(
        index=pd.MultiIndex.from_arrays(
            [
                [0, 1, 2, 3, 4],
                [5, 6, 7, 8, 9],
            ],
        ),
        data={
            'col_a': ['one', 'two', 'three', 'four', 'five'],
            'col_b': [1, 2, 3, 4, 5]
        }
    )

    df_right = pd.DataFrame({
        'col_a': ['one', 'too', 'three', 'fours', 'five', 'five'],
        'col_b': ['a', 'b', 'c', 'd', 'e', 'f']
    })

    # Use function
    df_matches = fuzzy_match(
        df_left,
        df_right,
        'col_a',
        'col_a',
        score_cutoff=60,
        limit=2
    )

    # Add expected output
    df_expected = pd.DataFrame(
        index=pd.MultiIndex.from_arrays(
            [
                [(0, 5), (1, 6), (2, 7), (3, 8), (4, 9), (4, 9)],
                [0, 1, 2, 3, 4, 5]
            ],
            names=['df_left_id', 'df_right_id']
        ),
        data={
            'match_string': ['one', 'too', 'three', 'fours', 'five', 'five'],
            'match_score': [100.000000, 66.666667, 100.000000, 88.888889, 100.000000, 100.000000],
        }
    )

    # Test output
    pdt.assert_frame_equal(df_matches, df_expected)

    return


def test_multiindex_df_right():
    '''
        Test non-empty, non-MultiIndex df_left, non-empty, MultiIndex df_right,
        where matches exist
    '''

    # Create dataframes
    df_left = pd.DataFrame({
        'col_a': ['one', 'two', 'three', 'four', 'five'],
        'col_b': [1, 2, 3, 4, 5]
    })
    df_right = pd.DataFrame(
        index=pd.MultiIndex.from_arrays(
            [
                [0, 1, 2, 3, 4, 5],
                [6, 7, 8, 9, 10, 11],
            ],
        ),
        data={
            'col_a': ['one', 'too', 'three', 'fours', 'five', 'five'],
            'col_b': ['a', 'b', 'c', 'd', 'e', 'f']
        }
    )

    # Use function
    df_matches = fuzzy_match(
        df_left,
        df_right,
        'col_a',
        'col_a',
        score_cutoff=60,
        limit=2
    )

    # Add expected output
    df_expected = pd.DataFrame(
        index=pd.MultiIndex.from_arrays(
            [
                [0, 1, 2, 3, 4, 4],
                [(0, 6), (1, 7), (2, 8), (3, 9), (4, 10), (5, 11)]
            ],
            names=['df_left_id', 'df_right_id']
        ),
        data={
            'match_string': ['one', 'too', 'three', 'fours', 'five', 'five'],
            'match_score': [100.000000, 66.666667, 100.000000, 88.888889, 100.000000, 100.000000],
        }
    )

    # Test output
    pdt.assert_frame_equal(df_matches, df_expected)

    return


def test_multiindex_df_left_and_right():
    '''
        Test non-empty, MultiIndex df_left, non-empty, MultiIndex df_right,
        where matches exist
    '''

    # Create dataframes
    df_left = pd.DataFrame(
        index=pd.MultiIndex.from_arrays(
            [
                [0, 1, 2, 3, 4],
                [5, 6, 7, 8, 9],
            ],
        ),
        data={
            'col_a': ['one', 'two', 'three', 'four', 'five'],
            'col_b': [1, 2, 3, 4, 5]
        }
    )
    df_right = pd.DataFrame(
        index=pd.MultiIndex.from_arrays(
            [
                [0, 1, 2, 3, 4, 5],
                [6, 7, 8, 9, 10, 11],
            ],
        ),
        data={
            'col_a': ['one', 'too', 'three', 'fours', 'five', 'five'],
            'col_b': ['a', 'b', 'c', 'd', 'e', 'f']
        }
    )

    # Use function
    df_matches = fuzzy_match(
        df_left,
        df_right,
        'col_a',
        'col_a',
        score_cutoff=60,
        limit=2
    )

    # Add expected output
    df_expected = pd.DataFrame(
        index=pd.MultiIndex.from_arrays(
            [
                [(0, 5), (1, 6), (2, 7), (3, 8), (4, 9), (4, 9)],
                [(0, 6), (1, 7), (2, 8), (3, 9), (4, 10), (5, 11)]
            ],
            names=['df_left_id', 'df_right_id']
        ),
        data={
            'match_string': ['one', 'too', 'three', 'fours', 'five', 'five'],
            'match_score': [100.000000, 66.666667, 100.000000, 88.888889, 100.000000, 100.000000],
        }
    )

    # Test output
    pdt.assert_frame_equal(df_matches, df_expected)

    return


def test_df_left_nan():
    '''
        Test non-empty, non-MultiIndex df_left, non-empty, non-MultiIndex df_right,
        where matches exist, df_left contains pd.NA, np.nan and None
    '''

    # Create dataframes
    df_left = pd.DataFrame({
        'col_a': [pd.NA, 'two', float('nan'), 'four', None],
        'col_b': [1, 2, 3, 4, 5]
    })
    df_right = pd.DataFrame({
        'col_a': ['one', 'too', 'three', 'fours', 'five', 'five'],
        'col_b': ['a', 'b', 'c', 'd', 'e', 'f']
    })

    # Use function
    df_matches = fuzzy_match(
        df_left,
        df_right,
        'col_a',
        'col_a',
        score_cutoff=60,
        limit=2
    )

    # Add expected output
    df_expected = pd.DataFrame(
        index=pd.MultiIndex.from_arrays(
            [
                [1, 3],
                [1, 3],
            ],
            names=['df_left_id', 'df_right_id']
        ),
        data={
            'match_string': ['too', 'fours'],
            'match_score': [66.666667, 88.888889],
        }
    )

    # Test output
    pdt.assert_frame_equal(df_matches, df_expected)

    return


def test_clean_strings_false():
    '''
        Test non-empty, non-MultiIndex df_left featuring punctuation,
        non-empty, non-MultiIndex df_right, where matches exist,
        clean_strings=False
    '''

    # Create dataframes
    df_left = pd.DataFrame({
        'col_a': ['one', 'two!', 'three', 'four', 'five'],
        'col_b': [1, 2, 3, 4, 5]
    })
    df_right = pd.DataFrame({
        'col_a': ['one', 'too', 'three', 'fours', 'five', 'five'],
        'col_b': ['a', 'b', 'c', 'd', 'e', 'f']
    })

    # Use function
    df_matches = fuzzy_match(
        df_left,
        df_right,
        'col_a',
        'col_a',
        score_cutoff=60,
        limit=2,
        clean_strings=False
    )

    # Add expected output
    df_expected = pd.DataFrame(
        index=pd.MultiIndex.from_arrays(
            [
                [0, 2, 3, 4, 4],
                [0, 2, 3, 4, 5],
            ],
            names=['df_left_id', 'df_right_id']
        ),
        data={
            'match_string': ['one', 'three', 'fours', 'five', 'five'],
            'match_score': [100.000000, 100.000000, 88.888889, 100.000000, 100.000000],
        }
    )

    # Test output
    pdt.assert_frame_equal(df_matches, df_expected)


def test_drop_na_false():
    '''
        Test non-empty, non-MultiIndex df_left, non-empty, non-MultiIndex df_right,
        where matches exist, drop_na=False
    '''

    # Create dataframes
    df_left = pd.DataFrame({
        'col_a': ['one', 'two', 'three', 'four', 'five'],
        'col_b': [1, 2, 3, 4, 5]
    })
    df_right = pd.DataFrame({
        'col_a': ['one', 'too', 'three', 'fours', 'five', 'five'],
        'col_b': ['a', 'b', 'c', 'd', 'e', 'f']
    })

    # Use function
    df_matches = fuzzy_match(
        df_left,
        df_right,
        'col_a',
        'col_a',
        score_cutoff=80,
        limit=2,
        drop_na=False
    )

    # Add expected output
    df_expected = pd.DataFrame(
        index=pd.MultiIndex.from_arrays(
            [
                [0, 1, 2, 3, 4, 4],
                [0.0, pd.NA, 2.0, 3.0, 4.0, 5.0],
            ],
            names=['df_left_id', 'df_right_id']
        ),
        data={
            'match_string': ['one', pd.NA, 'three', 'fours', 'five', 'five'],
            'match_score': pd.to_numeric(
                [100.000000, pd.NA, 100.000000, 88.888889, 100.000000, 100.000000]
            )
        }
    )

    # Test output
    pdt.assert_frame_equal(df_matches, df_expected)


def test_column_not_in_df():
    '''
        Test column_x not in df_x
    '''

    # Create dataframes
    df_left = pd.DataFrame({
        'col_a': ['one', 'two', 'three', 'four', 'five'],
        'col_b': [1, 2, 3, 4, 5]
    })
    df_right = pd.DataFrame({
        'col_a': ['one', 'too', 'three', 'fours', 'five', 'five'],
        'col_b': ['a', 'b', 'c', 'd', 'e', 'f']
    })

    # Test function, df_left
    with pytest.raises(KeyError):
        fuzzy_match(
            df_left,
            df_right,
            'col_c',
            'col_a',
            score_cutoff=60,
            limit=2
        )

    # Test function, df_right
    with pytest.raises(KeyError):
        fuzzy_match(
            df_left,
            df_right,
            'col_a',
            'col_c',
            score_cutoff=60,
            limit=2
        )

    return


def test_empty_df():
    '''
        Test empty df_x, non-empty df_y
    '''

    # Create dataframes
    df_left = pd.DataFrame(
        data={},
        columns=['col_a', 'col_b']
    )
    df_right = pd.DataFrame({
        'col_a': ['one', 'too', 'three', 'fours', 'five', 'five'],
        'col_b': ['a', 'b', 'c', 'd', 'e', 'f']

    })

    # Use function
    df_matches = fuzzy_match(
        df_left,
        df_right,
        'col_a',
        'col_a',
        score_cutoff=60,
        limit=2,
    )

    # Add expected output
    df_expected = pd.DataFrame(
        index=pd.MultiIndex(
            levels=[[], []],
            codes=[[], []],
            names=['df_left_id', 'df_right_id']
        ),
        columns=['match_string', 'match_score'],
    )

    # Test output
    pdt.assert_frame_equal(df_matches, df_expected, check_index_type=False)

    # Use function, reversing df_left and df_right
    df_matches = fuzzy_match(
        df_right,
        df_left,
        'col_a',
        'col_a',
        score_cutoff=60,
        limit=2,
    )

    # Test output
    pdt.assert_frame_equal(df_matches, df_expected, check_index_type=False)

    return
