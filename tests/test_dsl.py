# -*- coding: utf-8 -*-

import nose
from nose.tools import assert_equal
from nose.tools import nottest
from nose.tools import raises

from aws_vapor.dsl import Template
from aws_vapor.dsl import Element
from aws_vapor.dsl import Parameter
from aws_vapor.dsl import Mapping
from aws_vapor.dsl import Condition
from aws_vapor.dsl import Resource
from aws_vapor.dsl import Output
from aws_vapor.dsl import Attributes
from aws_vapor.dsl import Intrinsics
from aws_vapor.dsl import Pseudos
from aws_vapor.dsl import UserData
from aws_vapor.dsl import CfnInitMetadata


def test_intrinsics_base64():
    assert_equal(Intrinsics.base64('abcde'), {'Fn::Base64': 'abcde'})


def test_intrinsics_find_in_map__map_name():
    assert_equal(
        Intrinsics.find_in_map('map_name', 'top_key', 'second_key'),
        {'Fn::FindInMap': ['map_name', 'top_key', 'second_key']}
    )


def test_intrinsics_find_in_map__mapping():
    mapping = Mapping('map_name').add_category('top_key').add_item('second_key', 'map_value')
    assert_equal(
        Intrinsics.find_in_map(mapping, 'top_key', 'second_key'),
        {'Fn::FindInMap': ['map_name', 'top_key', 'second_key']}
    )


@raises(ValueError)
def test_intrinsics_find_in_map__others():
    Intrinsics.find_in_map({}, 'top_key', 'second_key')


def test_intrinsics_fn_and__two_conditions():
    conditions = [Condition('cond_name').expression(Intrinsics.fn_equals('value_1', 'value_2')) for _ in range(2)]
    assert_equal(
        Intrinsics.fn_and(conditions),
        {'Fn::And': [
            {'Fn::Equals': ['value_1', 'value_2']},
            {'Fn::Equals': ['value_1', 'value_2']}
        ]}
    )


@raises(ValueError)
def test_intrinsics_fn_and__only_one_condition():
    condition = Condition('cond_name').expression(Intrinsics.fn_equals('value_1', 'value_2'))
    Intrinsics.fn_and([condition])


@raises(ValueError)
def test_intrinsics_fn_and__more_than_ten_conditions():
    conditions = [Condition('cond_name').expression(Intrinsics.fn_equals('value_1', 'value_2')) for _ in range(11)]
    Intrinsics.fn_and(conditions)


def test_intrinsics_fn_equals():
    assert_equal(
        Intrinsics.fn_equals('value_1', 'value_2'),
        {'Fn::Equals': ['value_1', 'value_2']}
    )


def test_intrinsics_fn_if():
    assert_equal(
        Intrinsics.fn_if('cond_name', 'value_1', 'value_2'),
        {'Fn::If': ['cond_name', 'value_1', 'value_2']}
    )


def test_intrinsics_fn_not():
    condition = Condition('cond_name').expression(Intrinsics.fn_equals('value_1', 'value_2'))
    assert_equal(
        Intrinsics.fn_not(condition),
        {'Fn::Not': [{'Fn::Equals': ['value_1', 'value_2']}]}
    )


def test_intrinsics_fn_or__two_conditions():
    conditions = [Condition('cond_name').expression(Intrinsics.fn_equals('value_1', 'value_2')) for _ in range(2)]
    assert_equal(
        Intrinsics.fn_or(conditions),
        {'Fn::Or': [
            {'Fn::Equals': ['value_1', 'value_2']},
            {'Fn::Equals': ['value_1', 'value_2']}
        ]}
    )


@raises(ValueError)
def test_intrinsics_fn_or__only_one_condition():
    condition = Condition('cond_name').expression(Intrinsics.fn_equals('value_1', 'value_2'))
    Intrinsics.fn_or([condition])


@raises(ValueError)
def test_intrinsics_fn_or__more_than_ten_conditions():
    conditions = [Condition('cond_name').expression(Intrinsics.fn_equals('value_1', 'value_2')) for _ in range(11)]
    Intrinsics.fn_or(conditions)


def test_intrinsics_get_att():
    assert_equal(
        Intrinsics.get_att('res_name', 'attr_name'),
        {'Fn::GetAtt': ['res_name', 'attr_name']}
    )


def test_intrinsics_get_azs__with_region():
    assert_equal(
        Intrinsics.get_azs('region_name'),
        {'Fn::GetAZs': 'region_name'}
    )


def test_intrinsics_get_azs__without_region():
    assert_equal(
        Intrinsics.get_azs(),
        {'Fn::GetAZs': ''}
    )


def test_intrinsics_join():
    assert_equal(
        Intrinsics.join('delim', ['value_1', 'value_2', 'value_3']),
        {'Fn::Join': ['delim', ['value_1', 'value_2', 'value_3']]}
    )


def test_intrinsics_select():
    assert_equal(
        Intrinsics.select(2, ['value_1', 'value_2', 'value_3']),
        {'Fn::Select': [2, ['value_1', 'value_2', 'value_3']]}
    )


def test_intrinsics_ref__elem_name():
    assert_equal(
        Intrinsics.ref('elem_name'),
        {'Ref': 'elem_name'}
    )


def test_intrinsics_ref__element():
    element = Element('elem_name')
    assert_equal(
        Intrinsics.ref(element),
        {'Ref': 'elem_name'}
    )


@raises(ValueError)
def test_intrinsics_ref__others():
    Intrinsics.ref({}),


def test_pseudos_account_id():
    assert_equal(Pseudos.account_id(), {'Ref': 'AWS::AccountId'})


def test_pseudos_notification_arns():
    assert_equal(Pseudos.notification_arns(), {'Ref': 'AWS::NotificationARNs'})


def test_pseudos_no_value():
    assert_equal(Pseudos.no_value(), {'Ref': 'AWS::NoValue'})


def test_pseudos_region():
    assert_equal(Pseudos.region(), {'Ref': 'AWS::Region'})


def test_pseudos_stack_id():
    assert_equal(Pseudos.stack_id(), {'Ref': 'AWS::StackId'})


def test_pseudos_stack_name():
    assert_equal(Pseudos.stack_name(), {'Ref': 'AWS::StackName'})


if __name__ == '__main__':
    nose.main(argv=['nosetests', '-s', '-v'], defaultTest=__file__)
