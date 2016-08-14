# -*- coding: utf-8 -*-

import nose
from nose.tools import assert_equal
from nose.tools import nottest
from nose.tools import raises

import os

from aws_vapor.utils import load_from_config_file
from aws_vapor.utils import load_from_config_files
from aws_vapor.utils import get_property_from_config_files
from aws_vapor.utils import save_to_config_file
from aws_vapor.utils import combine_user_data
from aws_vapor.utils import inject_params
from aws_vapor.utils import open_outputfile
from aws_vapor.utils import FILE_WRITE_MODE


TOX_TMP_DIR = '.tox/tmp'
CONFIG_FILE_NAME = os.path.join(TOX_TMP_DIR, 'config')


def setup():
    if not os.path.exists(TOX_TMP_DIR):
        os.mkdir(TOX_TMP_DIR)

    with open(CONFIG_FILE_NAME, mode=FILE_WRITE_MODE) as fh:
        fh.write('[section_1]\n')
        fh.write('key_1 = value_1\n')
        fh.write('key_2 = value_2\n')
        fh.write('[section_2]\n')
        fh.write('key_3 = value_3\n')
        fh.write('key_4 = value_4\n')


def teardown():
    if os.path.exists(CONFIG_FILE_NAME):
        os.remove(CONFIG_FILE_NAME)


def test_load_from_config_file():
    assert_equal(
        load_from_config_file(TOX_TMP_DIR),
        {
            'section_1': {
                'key_1': 'value_1', 'key_2': 'value_2'
            },
            'section_2': {
                'key_3': 'value_3', 'key_4': 'value_4'
            }
        }
    )


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
