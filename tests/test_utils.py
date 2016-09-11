# -*- coding: utf-8 -*-

import nose
from nose.tools import assert_equal
from nose.tools import nottest
from nose.tools import raises

import os

from aws_vapor.utils import load_from_config_file
from aws_vapor.utils import get_property_from_config_file
from aws_vapor.utils import save_to_config_file
from aws_vapor.utils import combine_user_data
from aws_vapor.utils import inject_params
from aws_vapor.utils import open_outputfile
from aws_vapor.utils import CURRENT_DIRECTORY
from aws_vapor.utils import CONFIG_FILE_NAME
from aws_vapor.utils import FILE_WRITE_MODE


TOX_TMP1_DIR = '.tox/tmp1'
TOX_TMP2_DIR = '.tox/tmp2'
INVALID_DIR = '.tox/invalid'


def setup():
    def _(directory):
        if not os.path.exists(directory):
            os.mkdir(directory)

        config_file = os.path.join(directory, CONFIG_FILE_NAME)
        with open(config_file, mode=FILE_WRITE_MODE) as fh:
            fh.write('[section_1]\n')
            fh.write('key_1 = value_1\n')
            fh.write('key_2 = value_2\n')
            fh.write('[section_2]\n')
            fh.write('key_3 = value_3\n')
            fh.write('key_4 = value_4\n')
            fh.write('[section_%s]\n' % directory[-4:])
            fh.write('key_5 = value_5\n')
            fh.write('[section_override]\n')
            fh.write('directory = %s\n' % directory)

    _(CURRENT_DIRECTORY)
    _(TOX_TMP1_DIR)
    _(TOX_TMP2_DIR)


def teardown():
    def _(directory):
        config_file = os.path.join(directory, CONFIG_FILE_NAME)
        if os.path.exists(config_file):
            os.remove(config_file)

    _(CURRENT_DIRECTORY)
    _(TOX_TMP1_DIR)
    _(TOX_TMP2_DIR)


def test_load_from_config_file__single_file():
    assert_equal(
        load_from_config_file([TOX_TMP1_DIR]),
        {
            'section_1': {
                'key_1': 'value_1', 'key_2': 'value_2'
            },
            'section_2': {
                'key_3': 'value_3', 'key_4': 'value_4'
            },
            'section_tmp1': {
                'key_5': 'value_5'
            },
            'section_override': {
                'directory': TOX_TMP1_DIR
            }
        }
    )


def test_load_from_config_file__multiple_files():
    assert_equal(
        load_from_config_file([TOX_TMP1_DIR, TOX_TMP2_DIR]),
        {
            'section_1': {
                'key_1': 'value_1', 'key_2': 'value_2'
            },
            'section_2': {
                'key_3': 'value_3', 'key_4': 'value_4'
            },
            'section_tmp1': {
                'key_5': 'value_5'
            },
            'section_tmp2': {
                'key_5': 'value_5'
            },
            'section_override': {
                'directory': TOX_TMP2_DIR
            }
        }
    )


def test_load_from_config_file__invalid_directory():
    assert_equal(
        load_from_config_file([TOX_TMP1_DIR, INVALID_DIR]),
        {
            'section_1': {
                'key_1': 'value_1', 'key_2': 'value_2'
            },
            'section_2': {
                'key_3': 'value_3', 'key_4': 'value_4'
            },
            'section_tmp1': {
                'key_5': 'value_5'
            },
            'section_override': {
                'directory': TOX_TMP1_DIR
            }
        }
    )


def test_load_from_config_file__not_found_config_files():
    assert_equal(
        load_from_config_file([INVALID_DIR]),
        {}
    )


def test_get_property_from_config_file__exists_key():
    assert_equal(
        get_property_from_config_file('section_1', 'key_1'),
        'value_1'
    )


def test_get_property_from_config_file__not_found_section():
    assert_equal(
        get_property_from_config_file('section_X', 'key_X'),
        None
    )


def test_get_property_from_config_file__not_found_section_with_default_value():
    assert_equal(
        get_property_from_config_file('section_X', 'key_X', 'value_default'),
        'value_default'
    )


def test_get_property_from_config_file__not_found_key():
    assert_equal(
        get_property_from_config_file('section_1', 'key_X'),
        None
    )


def test_get_property_from_config_file__not_found_key_with_default_value():
    assert_equal(
        get_property_from_config_file('section_1', 'key_X', 'value_default'),
        'value_default'
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
