# !/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import pandas.testing as pdt
import pytest

from ds_utils.fuzzy_match import fuzzy_merge


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
    df_output = fuzzy_merge(
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
            'match_score': [100.000000, 66.666667, 100.000000, 88.888889, 100.000000, 100.000000],
            'col_a_df_left': ['one', 'two', 'three', 'four', 'five', 'five'],
            'col_b_df_left': [1, 2, 3, 4, 5, 5],
            'col_a_df_right': ['one', 'too', 'three', 'fours', 'five', 'five'],
            'col_b_df_right': ['a', 'b', 'c', 'd', 'e', 'f'],
        }
    )

    # Test output
    pdt.assert_frame_equal(df_output, df_expected)

    return


def test_no_matches():
    '''
        Test non-empty, non-MultiIndex df_left, non-empty, non-MultiIndex df_right,
        where no matches exist
    '''

    # Create dataframes
    df_left = pd.DataFrame({
        'col_a': ['one', 'two', 'three', 'four', 'five'],
        'col_b': [1, 2, 3, 4, 5]
    })
    df_right = pd.DataFrame({
        'col_a': ['six', 'seven', 'eight', 'nine', 'ten'],
        'col_b': ['a', 'b', 'c', 'd', 'e']
    })

    # Use function
    df_output = fuzzy_merge(
        df_left,
        df_right,
        'col_a',
        'col_a',
        score_cutoff=60,
        limit=2
    )

    # Add expected output
    df_expected = pd.DataFrame(
        columns=['match_score', 'col_a_df_left', 'col_b_df_left'],
        index=pd.MultiIndex.from_arrays(
            [
                [],
                [],
            ],
            names=['df_left_id', 'df_right_id']
        )
    )

    # Test output
    # NB: Disabling checking of types as the inferred_type differs
    # here
    pdt.assert_frame_equal(
        df_output,
        df_expected,
        check_index_type=False,
        check_dtype=False,
    )

    return


def test_df_left_nan():
    '''
        Test non-empty, non-MultiIndex df_left, non-empty, non-MultiIndex df_right,
        where matches exist, df_left contains pd.NA, np.nan and None
    '''

    # Create dataframes
    df_left = pd.DataFrame({
        'col_a': [pd.NA, 'two', np.NaN, 'four', None],
        'col_b': [1, 2, 3, 4, 5]
    })
    df_right = pd.DataFrame({
        'col_a': ['one', 'too', 'three', 'fours', 'five', 'five'],
        'col_b': ['a', 'b', 'c', 'd', 'e', 'f']
    })

    # Use function
    df_output = fuzzy_merge(
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
            'match_score': [66.666667, 88.888889],
            'col_a_df_left': ['two', 'four'],
            'col_b_df_left': [2, 4],
            'col_a_df_right': ['too', 'fours'],
            'col_b_df_right': ['b', 'd'],
        }
    )

    # Test output
    pdt.assert_frame_equal(df_output, df_expected)

    return


def test_df_right_nan():
    '''
        Test non-empty, non-MultiIndex df_left, non-empty, non-MultiIndex df_right,
        where matches exist, df_right contains pd.NA, np.nan and None
    '''

    # Create dataframes
    df_left = pd.DataFrame({
        'col_a': ['one', 'two', 'three', 'four', 'five'],
        'col_b': [1, 2, 3, 4, 5]
    })
    df_right = pd.DataFrame({
        'col_a': [pd.NA, 'too', np.NaN, 'fours', None, 'five'],
        'col_b': ['a', 'b', 'c', 'd', 'e', 'f']
    })

    # Use function
    df_output = fuzzy_merge(
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
                [1, 3, 4],
                [1, 3, 5],
            ],
            names=['df_left_id', 'df_right_id']
        ),
        data={
            'match_score': [66.666667, 88.888889, 100.000000],
            'col_a_df_left': ['two', 'four', 'five'],
            'col_b_df_left': [2, 4, 5],
            'col_a_df_right': ['too', 'fours', 'five'],
            'col_b_df_right': ['b', 'd', 'f'],
        }
    )

    # Test output
    pdt.assert_frame_equal(df_output, df_expected)

    return


def test_column_not_in_df():
    '''
        Test column_x not in df_left
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
        fuzzy_merge(
            df_left,
            df_right,
            'col_c',
            'col_a',
            score_cutoff=60,
            limit=2
        )

    # Test function, df_right
    with pytest.raises(KeyError):
        fuzzy_merge(
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
        Test empty df_left, non-empty df_right
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
    df_output = fuzzy_merge(
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
        columns=['match_score', 'col_a_df_left', 'col_b_df_left'],
    )

    # Test output
    pdt.assert_frame_equal(df_output, df_expected, check_index_type=False)

    # Use function, reversing df_left and df_right
    df_output = fuzzy_merge(
        df_right,
        df_left,
        'col_a',
        'col_a',
        score_cutoff=60,
        limit=2,
    )

    # Test output
    pdt.assert_frame_equal(df_output, df_expected, check_index_type=False)

    return


def test_empty_dfs():
    '''
        Test empty df_left and df_right dataframes
    '''

    # Create dataframes
    df_left = pd.DataFrame(columns=['col_a', 'col_b'])
    df_right = pd.DataFrame(columns=['col_a', 'col_b'])

    # Use function
    df_output = fuzzy_merge(
        df_left,
        df_right,
        'col_a',
        'col_a',
        score_cutoff=60,
        limit=2
    )

    # Add expected output
    df_expected = pd.DataFrame(
        columns=['match_score', 'col_a_df_left', 'col_b_df_left'],
        index=pd.MultiIndex.from_arrays(
            [
                [],
                [],
            ],
            names=['df_left_id', 'df_right_id']
        )
    )

    # Test output
    # NB: Disabling checking of index type as the inferred_type differs
    # here - 'integer' for df_output and 'empty' for df_expected
    pdt.assert_frame_equal(
        df_output,
        df_expected,
        check_index_type=False
    )

    return


def test_int_column_names():
    '''
        Test df_left with integer column names
    '''

    # Create dataframes
    df_left = pd.DataFrame({
        0: ['one', 'two', 'three', 'four', 'five'],
        1: [1, 2, 3, 4, 5]
    })
    df_right = pd.DataFrame({
        0: ['one', 'too', 'three', 'fours', 'five', 'five'],
        1: ['a', 'b', 'c', 'd', 'e', 'f']
    })

    # Use function
    df_output = fuzzy_merge(
        df_left,
        df_right,
        0,
        0,
        score_cutoff=60,
        limit=2,
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
            'match_score': [100.000000, 66.666667, 100.000000, 88.888889, 100.000000, 100.000000],
            '0_df_left': ['one', 'two', 'three', 'four', 'five', 'five'],
            '1_df_left': [1, 2, 3, 4, 5, 5],
            '0_df_right': ['one', 'too', 'three', 'fours', 'five', 'five'],
            '1_df_right': ['a', 'b', 'c', 'd', 'e', 'f'],
        }
    )

    # Test output
    pdt.assert_frame_equal(df_output, df_expected)

    return


def test_float_column_names():
    '''
        Test df_left with float column names
    '''

    # Create dataframes
    df_left = pd.DataFrame({
        0.0: ['one', 'two', 'three', 'four', 'five'],
        1.0: [1, 2, 3, 4, 5]
    })
    df_right = pd.DataFrame({
        0.0: ['one', 'too', 'three', 'fours', 'five', 'five'],
        1.0: ['a', 'b', 'c', 'd', 'e', 'f']
    })

    # Use function
    df_output = fuzzy_merge(
        df_left,
        df_right,
        0.0,
        0.0,
        score_cutoff=60,
        limit=2,
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
            'match_score': [100.000000, 66.666667, 100.000000, 88.888889, 100.000000, 100.000000],
            '0.0_df_left': ['one', 'two', 'three', 'four', 'five', 'five'],
            '1.0_df_left': [1, 2, 3, 4, 5, 5],
            '0.0_df_right': ['one', 'too', 'three', 'fours', 'five', 'five'],
            '1.0_df_right': ['a', 'b', 'c', 'd', 'e', 'f'],
        }
    )

    # Test output
    pdt.assert_frame_equal(df_output, df_expected)

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
    df_output = fuzzy_merge(
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
            'match_score': [100.000000, 66.666667, 100.000000, 88.888889, 100.000000, 100.000000],
            'col_a_df_left': ['one', 'two', 'three', 'four', 'five', 'five'],
            'col_b_df_left': [1, 2, 3, 4, 5, 5],
            'col_a_df_right': ['one', 'too', 'three', 'fours', 'five', 'five'],
            'col_b_df_right': ['a', 'b', 'c', 'd', 'e', 'f'],
        }
    )

    # Test output
    pdt.assert_frame_equal(df_output, df_expected)

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
    df_output = fuzzy_merge(
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
            'match_score': [100.000000, 66.666667, 100.000000, 88.888889, 100.000000, 100.000000],
            'col_a_df_left': ['one', 'two', 'three', 'four', 'five', 'five'],
            'col_b_df_left': [1, 2, 3, 4, 5, 5],
            'col_a_df_right': ['one', 'too', 'three', 'fours', 'five', 'five'],
            'col_b_df_right': ['a', 'b', 'c', 'd', 'e', 'f'],
        }
    )

    # Test output
    pdt.assert_frame_equal(df_output, df_expected)

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
    df_output = fuzzy_merge(
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
            'match_score': [100.000000, 66.666667, 100.000000, 88.888889, 100.000000, 100.000000],
            'col_a_df_left': ['one', 'two', 'three', 'four', 'five', 'five'],
            'col_b_df_left': [1, 2, 3, 4, 5, 5],
            'col_a_df_right': ['one', 'too', 'three', 'fours', 'five', 'five'],
            'col_b_df_right': ['a', 'b', 'c', 'd', 'e', 'f'],
        }
    )

    # Test output
    pdt.assert_frame_equal(df_output, df_expected)

    return


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
    df_output = fuzzy_merge(
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
                [0.0, np.NaN, 2.0, 3.0, 4.0, 5.0],
            ],
            names=['df_left_id', 'df_right_id']
        ),
        data={
            'match_score': pd.to_numeric(
                [100.000000, np.NaN, 100.000000, 88.888889, 100.000000, 100.000000]
            ),
            'col_a_df_left': ['one', 'two', 'three', 'four', 'five', 'five'],
            'col_b_df_left': pd.to_numeric([1, 2, 3, 4, 5, 5]),
            'col_a_df_right': ['one', np.NaN, 'three', 'fours', 'five', 'five'],
            'col_b_df_right': ['a', np.NaN, 'c', 'd', 'e', 'f'],
        }
    )

    # Test output
    pdt.assert_frame_equal(df_output, df_expected)

    return


def test_drop_cols_none():
    '''
        Test non-empty, non-MultiIndex df_left, non-empty, non-MultiIndex df_right,
        where matches exist, drop_na=None
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

    # Use function, drop_na=None
    df_output = fuzzy_merge(
        df_left,
        df_right,
        'col_a',
        'col_a',
        score_cutoff=80,
        limit=2,
        drop_cols=None
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
            'match_score': pd.to_numeric(
                [100.000000, 100.000000, 88.888889, 100.000000, 100.000000]
            ),
            'col_a_df_left': ['one', 'three', 'four', 'five', 'five'],
            'col_b_df_left': pd.to_numeric([1, 3, 4, 5, 5]),
            'col_a_df_right': ['one', 'three', 'fours', 'five', 'five'],
            'col_b_df_right': ['a', 'c', 'd', 'e', 'f'],
        }
    )

    # Test output
    pdt.assert_frame_equal(df_output, df_expected)

    return


def test_drop_cols_left():
    '''
        Test non-empty, non-MultiIndex df_left, non-empty, non-MultiIndex df_right,
        where matches exist, drop_cols_='left'
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
    df_output = fuzzy_merge(
        df_left,
        df_right,
        'col_a',
        'col_a',
        score_cutoff=80,
        limit=2,
        drop_cols='left'
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
            'match_score': pd.to_numeric(
                [100.000000, 100.000000, 88.888889, 100.000000, 100.000000]
            ),
            'col_a_df_right': ['one', 'three', 'fours', 'five', 'five'],
            'col_b_df_right': ['a', 'c', 'd', 'e', 'f'],
        }
    )

    # Test output
    pdt.assert_frame_equal(df_output, df_expected)

    return


def test_drop_cols_right():
    '''
        Test non-empty, non-MultiIndex df_left, non-empty, non-MultiIndex df_right,
        where matches exist, drop_cols_='right'
    '''

    # Create dataframes
    df_left = pd.DataFrame({
        'col_a': ['one', 'two', 'three', 'four', 'five', 'five'],
        'col_b': [1, 2, 3, 4, 5, 5]
    })
    df_right = pd.DataFrame({
        'col_a': ['one', 'too', 'three', 'fours', 'five'],
        'col_b': ['a', 'b', 'c', 'd', 'e']
    })

    # Use function
    df_output = fuzzy_merge(
        df_left,
        df_right,
        'col_a',
        'col_a',
        score_cutoff=80,
        limit=2,
        drop_cols='right'
    )

    # Add expected output
    df_expected = pd.DataFrame(
        index=pd.MultiIndex.from_arrays(
            [
                [0, 2, 3, 4, 5],
                [0, 2, 3, 4, 4],
            ],
            names=['df_left_id', 'df_right_id']
        ),
        data={
            'match_score': pd.to_numeric(
                [100.000000, 100.000000, 88.888889, 100.000000, 100.000000]
            ),
            'col_a_df_left': ['one', 'three', 'four', 'five', 'five'],
            'col_b_df_left': pd.to_numeric([1, 3, 4, 5, 5]),
        }
    )

    # Test output
    pdt.assert_frame_equal(df_output, df_expected)

    return


def test_drop_cols_both():
    '''
        Test non-empty, non-MultiIndex df_left, non-empty, non-MultiIndex df_right,
        where matches exist, drop_cols_='both'
    '''

    # Create dataframes
    df_left = pd.DataFrame({
        'col_a': ['one', 'two', 'three', 'four', 'five', 'five'],
        'col_b': [1, 2, 3, 4, 5, 5]
    })
    df_right = pd.DataFrame({
        'col_a': ['one', 'too', 'three', 'fours', 'five'],
        'col_b': ['a', 'b', 'c', 'd', 'e']
    })

    # Use function
    df_output = fuzzy_merge(
        df_left,
        df_right,
        'col_a',
        'col_a',
        score_cutoff=80,
        limit=2,
        drop_cols='both'
    )

    # Add expected output
    df_expected = pd.DataFrame(
        index=pd.MultiIndex.from_arrays(
            [
                [0, 2, 3, 4, 5],
                [0, 2, 3, 4, 4],
            ],
            names=['df_left_id', 'df_right_id']
        ),
        data={
            'match_score': pd.to_numeric(
                [100.000000, 100.000000, 88.888889, 100.000000, 100.000000]
            ),
        }
    )

    # Test output
    pdt.assert_frame_equal(df_output, df_expected)

    return


def test_drop_cols_match():
    '''
        Test non-empty, non-MultiIndex df_left, non-empty, non-MultiIndex df_right,
        where matches exist, drop_cols_='match'
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
    df_output = fuzzy_merge(
        df_left,
        df_right,
        'col_a',
        'col_a',
        score_cutoff=80,
        limit=2,
        drop_cols='match'
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
            'col_a_df_left': ['one', 'three', 'four', 'five', 'five'],
            'col_b_df_left': pd.to_numeric([1, 3, 4, 5, 5]),
            'col_a_df_right': ['one', 'three', 'fours', 'five', 'five'],
            'col_b_df_right': ['a', 'c', 'd', 'e', 'f'],
        }
    )

    # Test output
    pdt.assert_frame_equal(df_output, df_expected)

    return


def test_drop_cols_invalid():
    '''
        Test non-empty, non-MultiIndex df_left, non-empty, non-MultiIndex df_right,
        where matches exist, drop_cols_='invalid'
    '''

    # Create dataframes
    df_left = pd.DataFrame({
        'col_a': ['one', 'two', 'three', 'four', 'five', 'five'],
        'col_b': [1, 2, 3, 4, 5, 5]
    })
    df_right = pd.DataFrame({
        'col_a': ['one', 'too', 'three', 'fours', 'five'],
        'col_b': ['a', 'b', 'c', 'd', 'e']
    })

    # Use function
    with pytest.raises(ValueError):
        fuzzy_merge(
            df_left,
            df_right,
            'col_a',
            'col_a',
            score_cutoff=80,
            limit=2,
            drop_cols='invalid'
        )

    return


def test_suffixes():
    '''
        Test non-empty, non-MultiIndex df_left, non-empty, non-MultiIndex df_right,
        where matches exist and suffixes supplied
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

    # Use function, suffixes
    df_output = fuzzy_merge(
        df_left,
        df_right,
        'col_a',
        'col_a',
        score_cutoff=80,
        limit=2,
        suffixes=('_left', '_right')
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
            'match_score': pd.to_numeric(
                [100.000000, 100.000000, 88.888889, 100.000000, 100.000000]
            ),
            'col_a_left': ['one', 'three', 'four', 'five', 'five'],
            'col_b_left': pd.to_numeric([1, 3, 4, 5, 5]),
            'col_a_right': ['one', 'three', 'fours', 'five', 'five'],
            'col_b_right': ['a', 'c', 'd', 'e', 'f'],
        }
    )

    # Test output
    pdt.assert_frame_equal(df_output, df_expected)

    return


def test_suffixes_and_drop_cols_left():
    '''
        Test non-empty, non-MultiIndex df_left, non-empty, non-MultiIndex df_right,
        where matches exist and suffixes supplied, drop_cols='left'
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

    # Use function, suffixes
    df_output = fuzzy_merge(
        df_left,
        df_right,
        'col_a',
        'col_a',
        score_cutoff=80,
        limit=2,
        suffixes=('_left', '_right'),
        drop_cols='left',
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
            'match_score': pd.to_numeric(
                [100.000000, 100.000000, 88.888889, 100.000000, 100.000000]
            ),
            'col_a_right': ['one', 'three', 'fours', 'five', 'five'],
            'col_b_right': ['a', 'c', 'd', 'e', 'f'],
        }
    )

    # Test output
    pdt.assert_frame_equal(df_output, df_expected)

    return


def test_suffixes_and_drop_cols_right():
    '''
        Test non-empty, non-MultiIndex df_left, non-empty, non-MultiIndex df_right,
        where matches exist and suffixes supplied, drop_cols='right'
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

    # Use function, suffixes
    df_output = fuzzy_merge(
        df_left,
        df_right,
        'col_a',
        'col_a',
        score_cutoff=80,
        limit=2,
        suffixes=('_left', '_right'),
        drop_cols='right',
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
            'match_score': pd.to_numeric(
                [100.000000, 100.000000, 88.888889, 100.000000, 100.000000]
            ),
            'col_a_left': ['one', 'three', 'four', 'five', 'five'],
            'col_b_left': pd.to_numeric([1, 3, 4, 5, 5]),
        }
    )

    # Test output
    pdt.assert_frame_equal(df_output, df_expected)

    return


def test_suffixes_and_drop_cols_both():
    '''
        Test non-empty, non-MultiIndex df_left, non-empty, non-MultiIndex df_right,
        where matches exist and suffixes supplied, drop_cols='both'
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

    # Use function, suffixes
    df_output = fuzzy_merge(
        df_left,
        df_right,
        'col_a',
        'col_a',
        score_cutoff=80,
        limit=2,
        suffixes=('_left', '_right'),
        drop_cols='both',
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
            'match_score': pd.to_numeric(
                [100.000000, 100.000000, 88.888889, 100.000000, 100.000000]
            ),
        }
    )

    # Test output
    pdt.assert_frame_equal(df_output, df_expected)

    return


def test_suffixes_and_drop_cols_match():
    '''
        Test non-empty, non-MultiIndex df_left, non-empty, non-MultiIndex df_right,
        where matches exist and suffixes supplied, drop_cols='match'
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

    # Use function, suffixes
    df_output = fuzzy_merge(
        df_left,
        df_right,
        'col_a',
        'col_a',
        score_cutoff=80,
        limit=2,
        suffixes=('_left', '_right'),
        drop_cols='match',
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
            'col_a_left': ['one', 'three', 'four', 'five', 'five'],
            'col_b_left': pd.to_numeric([1, 3, 4, 5, 5]),
            'col_a_right': ['one', 'three', 'fours', 'five', 'five'],
            'col_b_right': ['a', 'c', 'd', 'e', 'f'],
        }
    )

    # Test output
    pdt.assert_frame_equal(df_output, df_expected)

    return
