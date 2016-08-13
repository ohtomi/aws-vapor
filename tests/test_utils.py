# -*- coding: utf-8 -*-

import nose
from nose.tools import assert_equal
from nose.tools import nottest
from nose.tools import raises

from aws_vapor.utils import load_from_config_file
from aws_vapor.utils import load_from_config_files
from aws_vapor.utils import get_property_from_config_files
from aws_vapor.utils import save_to_config_file
from aws_vapor.utils import combine_user_data
from aws_vapor.utils import inject_params
from aws_vapor.utils import open_outputfile


def test_inject_params__all_placeholders_replaced():
    assert_equal(
        inject_params('abcde\n__{{ fghij }}__\nklmno\n', {'fghij': '__fghij__'}),
        ['abcde\n', '__', '__fghij__', '__\n', 'klmno\n', '\n']
    )


def test_inject_params__no_parameters_passed():
    assert_equal(
        inject_params('abcde\n__{{ fghij }}__\nklmno\n', {}),
        ['abcde\n', '__{{ fghij }}__\n', 'klmno\n', '\n']
    )


def test_inject_params__illegal_placeholder__no_space_on_the_left_side():
    assert_equal(
        inject_params('abcde\n__{{fghij }}__\nklmno\n', {'fghij': '__fghij__'}),
        ['abcde\n', '__{{fghij }}__\n', 'klmno\n', '\n']
    )


def test_inject_params__illegal_placeholder__no_space_on_the_right_side():
    assert_equal(
        inject_params('abcde\n__{{ fghij}}__\nklmno\n', {'fghij': '__fghij__'}),
        ['abcde\n', '__{{ fghij}}__\n', 'klmno\n', '\n']
    )


def test_inject_params__illegal_placeholder__no_spaces_on_the_both_sides():
    assert_equal(
        inject_params('abcde\n__{{fghij}}__\nklmno\n', {'fghij': '__fghij__'}),
        ['abcde\n', '__{{fghij}}__\n', 'klmno\n', '\n']
    )


def test_inject_params__illegal_placeholder__space_between_left_parens():
    assert_equal(
        inject_params('abcde\n__{ { fghij }}__\nklmno\n', {'fghij': '__fghij__'}),
        ['abcde\n', '__{ { fghij }}__\n', 'klmno\n', '\n']
    )


def test_inject_params__illegal_placeholder__space_between_right_parns():
    assert_equal(
        inject_params('abcde\n__{{ fghij } }__\nklmno\n', {'fghij': '__fghij__'}),
        ['abcde\n', '__{{ fghij } }__\n', 'klmno\n', '\n']
    )


def test_inject_params__multi_placeholders_in_one_line():
    assert_equal(
        inject_params('abcde__{{ fghij }}__{{ klmno }}__pqrst', {'fghij': '__fghij__', 'klmno': '__klmno__'}),
        ['abcde__', '__fghij__', '__', '__klmno__', '__pqrst\n']
    )


if __name__ == '__main__':
    nose.main(argv=['nosetests', '-s', '-v'], defaultTest=__file__)
