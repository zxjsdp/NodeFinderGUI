# -*- coding: utf-8 -*-

from __future__ import print_function, with_statement

import pytest
import mock

from nodefinder_gui.nodefinder_gui import (
    clean_elements,
    get_clean_tree_str,
    get_right_index_of_name,
    get_insertion_list,
    get_index_of_tmrca,
    single_calibration,
    add_single_branch_label,
    multi_calibration,
    get_cali_list,
    get_tree_str,
    get_species_names_from_tree_str,
)


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


def test_get_insertion_list():
    clean_tree_str = '((a,((b,c),(d,e))),(f,g));'
    name = 'c'

    expected_insertion_list = [10, 17, 18, 25]
    actual_insertion_list = get_insertion_list(clean_tree_str, name)

    assert expected_insertion_list == actual_insertion_list


def test_get_index_of_tmrca():
    clean_tree_str = '((a,((b,c),(d,e))),(f,g));'
    name_a = 'a'
    name_b = 'e'

    expected_index_of_tmrca = 18
    actual_index_of_tmrca = get_index_of_tmrca(clean_tree_str, name_a, name_b)

    assert expected_index_of_tmrca == actual_index_of_tmrca


def test_single_calibration():
    raw_tree_str = '((a ,((b, c), (d, e))), (f, g));'
    name_a = 'a'
    name_b = 'e'
    cali_info = '>0.3<0.4'

    expected_tree_with_cali = '((a,((b,c),(d,e)))>0.3<0.4,(f,g));'
    actual_tree_with_cali = single_calibration(raw_tree_str, name_a,
                                               name_b, cali_info)

    assert expected_tree_with_cali == actual_tree_with_cali


def test_add_single_branch_label():
    raw_tree_str = '((a ,((b, c), (d, e))), (f, g));'
    name_a = 'c'
    branch_label = '#1'

    expected_tree_with_branch_label = '((a,((b,c #1 ),(d,e))),(f,g));'
    actual_tree_with_branch_label = add_single_branch_label(
        raw_tree_str, name_a, branch_label)

    assert expected_tree_with_branch_label == actual_tree_with_branch_label


def test_multi_calibration():
    raw_tree_str = '((a ,((b, c), (d, e))), (f, g));'
    cali_tuple_list = [('b', 'c', '>0.1<0.2'),
                       ('a', 'b', '>0.2<0.3'),
                       ('a', 'e', '>0.3<0.4'),
                       ('d', 'f', '>0.6<0.7')]

    expected_tree_with_multi_cali = \
        '((a, ((b, c)>0.1<0.2, (d, e)))>0.3<0.4, (f, g))>0.6<0.7;'
    actual_tree_with_multi_cali = multi_calibration(raw_tree_str,
                                                    cali_tuple_list)

    assert expected_tree_with_multi_cali == actual_tree_with_multi_cali


def test_get_cali_list():
    raw_cali_content = """
        b, c, >0.1<0.2
        a, b, >0.2<0.3
        a, e, >0.3<0.4
        d, f, >0.6<0.7"""

    expected_cali_list = [
        ['b', 'c', '>0.1<0.2'],
        ['a', 'b', '>0.2<0.3'],
        ['a', 'e', '>0.3<0.4'],
        ['d', 'f', '>0.6<0.7']]
    actual_cali_list = get_cali_list(raw_cali_content)

    assert expected_cali_list == actual_cali_list


def test_get_tree_str():
    raw_tree_str = ('120\n# comment line\n ((a ,((b, c), (d, e))), '
                    '(f, g));\n\n// another comment line')

    expected_tree_str = '((a ,((b, c), (d, e))), (f, g));'
    actual_tree_str = get_tree_str(raw_tree_str)

    assert expected_tree_str == actual_tree_str


def test_get_species_names_from_tree_str():

    raw_tree_str = '((a ,((b, c), (d, e))), (f, g));'

    expected_species_names = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
    actual_species_names = get_species_names_from_tree_str(raw_tree_str)

    expected_species_num = 7
    actual_species_num = len(get_species_names_from_tree_str(raw_tree_str))

    assert expected_species_names == actual_species_names
    assert expected_species_num == actual_species_num