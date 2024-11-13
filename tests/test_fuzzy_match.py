# !/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import pandas.testing as pdt
import pytest

from ds_utils import matching_operations as mo


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
    df_matches = mo.fuzzy_match(
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
    df_matches = mo.fuzzy_match(
        df_left,
        df_right,
        'col_a',
        'col_a',
        score_cutoff=60,
        limit=2
    )

    # Add expected output
    df_expected = pd.DataFrame(
        columns=['match_string', 'match_score'],
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
    # here - 'integer' for df_matches and 'empty' for df_expected
    pdt.assert_frame_equal(
        df_matches,
        df_expected,
        check_index_type=False
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
    df_matches = mo.fuzzy_match(
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
    df_matches = mo.fuzzy_match(
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
            'match_string': ['too', 'fours', 'five'],
            'match_score': [66.666667, 88.888889, 100.000000],
        }
    )

    # Test output
    pdt.assert_frame_equal(df_matches, df_expected)

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
        mo.fuzzy_match(
            df_left,
            df_right,
            'col_c',
            'col_a',
            score_cutoff=60,
            limit=2
        )

    # Test function, df_right
    with pytest.raises(KeyError):
        mo.fuzzy_match(
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
    df_matches = mo.fuzzy_match(
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
    df_matches = mo.fuzzy_match(
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


def test_empty_dfs():
    '''
        Test empty df_left and df_right dataframes
    '''

    # Create dataframes
    df_left = pd.DataFrame(columns=['col_a', 'col_b'])
    df_right = pd.DataFrame(columns=['col_a', 'col_b'])

    # Use function
    df_matches = mo.fuzzy_match(
        df_left,
        df_right,
        'col_a',
        'col_a',
        score_cutoff=60,
        limit=2
    )

    # Add expected output
    df_expected = pd.DataFrame(
        columns=['match_string', 'match_score'],
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
    # here - 'integer' for df_matches and 'empty' for df_expected
    pdt.assert_frame_equal(
        df_matches,
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
    df_matches = mo.fuzzy_match(
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
            'match_string': ['one', 'too', 'three', 'fours', 'five', 'five'],
            'match_score': [100.000000, 66.666667, 100.000000, 88.888889, 100.000000, 100.000000],
        }
    )

    # Test output
    pdt.assert_frame_equal(df_matches, df_expected)

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
    df_matches = mo.fuzzy_match(
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
    df_matches = mo.fuzzy_match(
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
    df_matches = mo.fuzzy_match(
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
    df_matches = mo.fuzzy_match(
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
    df_matches = mo.fuzzy_match(
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
    df_matches = mo.fuzzy_match(
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
            'match_string': ['one', np.NaN, 'three', 'fours', 'five', 'five'],
            'match_score': pd.to_numeric(
                [100.000000, np.NaN, 100.000000, 88.888889, 100.000000, 100.000000]
            )
        }
    )

    # Test output
    pdt.assert_frame_equal(df_matches, df_expected)

    return
