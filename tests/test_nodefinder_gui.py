# -*- coding: utf-8 -*-

import pytest
from nodefinder_gui.nodefinder_gui import (
    clean_elements, get_clean_tree_str, get_right_index_of_name
)
import mock


def test_clean_elements():
    test_list = ['a ', '\tb\t', 'c; ']

    expected_result = ['a', 'b', 'c']
    actual_result = clean_elements(test_list)

    assert expected_result == actual_result


def test_get_clean_tree_str():
    test_tree_str = '((a ,((b, c), (d, e))), (f, g));'

    expected_result = '((a,((b,c),(d,e))),(f,g));'
    actual_result = get_clean_tree_str(test_tree_str)

    assert expected_result == actual_result


def test_get_right_index_of_name():
    test_tree_str = '((a,((b,c),(ddd,e))),(f,g));'
    test_name = 'ddd'

    expected_right_index_of_name = 15
    actual_right_index_of_name = get_right_index_of_name(test_tree_str,
                                                         test_name)

    assert expected_right_index_of_name == actual_right_index_of_name