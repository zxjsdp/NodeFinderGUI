# -*- coding: utf-8 -*-

import pytest
from nodefinder_gui.nodefinder_gui import clean_elements
import mock


def test_clean_elements():
     test_list = ['a ', '\tb\t', 'c; ']

     expected_result = ['a', 'b', 'c']
     actual_result = clean_elements(test_list)

     assert expected_result == actual_result
