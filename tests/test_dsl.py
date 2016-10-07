# -*- coding: utf-8 -*-

import nose
from nose.tools import assert_equal
from nose.tools import nottest
from nose.tools import raises

import os

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
from aws_vapor.utils import FILE_WRITE_MODE


TOX_TMP_DIR = '.tox/tmp'
X_SHELL_SCRIPT_FILE_NAME = os.path.join(TOX_TMP_DIR, 'x-shellscript.txt')
X_SHELL_SCRIPT_PARAMS = {
    'param_1': 'value_1',
    'param_2': 'value_2'
}


def setup():
    if not os.path.exists(TOX_TMP_DIR):
        os.mkdir(TOX_TMP_DIR)

    with open(X_SHELL_SCRIPT_FILE_NAME, mode=FILE_WRITE_MODE) as fh:
        fh.write('ABCDE {{ param_1 }}\n')
        fh.write('abcde {{ param_2 }}\n')


def teardown():
    if os.path.exists(X_SHELL_SCRIPT_FILE_NAME):
        os.remove(X_SHELL_SCRIPT_FILE_NAME)


def test_element():
    template = {}
    Element('abcde').attributes('key_1', 'value_1').attributes('key_2', 'value_2').to_template(template)
    assert_equal(
        template,
        {'abcde': {'key_1': 'value_1', 'key_2': 'value_2'}}
    )


def test_parameter():
    template = {}
    Parameter('abcde').description('description').type('type').default('default').to_template(template)
    assert_equal(
        template,
        {'abcde': {'Description': 'description', 'Type': 'type', 'Default': 'default'}}
    )


def test_mapping__one_category():
    template = {}
    Mapping('abcde').add_category('category_1').add_item('key_1', 'value_1').add_item('key_2', 'value_2').to_template(template)
    assert_equal(
        template,
        {'abcde': {
            'category_1': {'key_1': 'value_1', 'key_2': 'value_2'}
        }}
    )


def test_mapping__two_categories():
    template = {}
    mapping = Mapping('abcde')
    mapping.add_category('category_1').add_item('key_1', 'value_1').add_item('key_2', 'value_2')
    mapping.add_category('category_2').add_item('key_3', 'value_3').add_item('key_4', 'value_4')
    mapping.to_template(template)
    assert_equal(
        template,
        {'abcde': {
            'category_1': {'key_1': 'value_1', 'key_2': 'value_2'},
            'category_2': {'key_3': 'value_3', 'key_4': 'value_4'}
        }}
    )


def test_mapping__find_in_map__ok():
    mapping = Mapping('abcde')
    mapping.add_category('category_1').add_item('key_1', 'value_1').add_item('key_2', 'value_2')
    assert_equal(
        mapping.find_in_map('category_1', 'key_1'),
        {'Fn::FindInMap': ['abcde', 'category_1', 'key_1']}
    )


@raises(ValueError)
def test_mapping__find_in_map__missing_top_level_key():
    mapping = Mapping('abcde')
    mapping.add_category('category_1').add_item('key_1', 'value_1').add_item('key_2', 'value_2')
    mapping.find_in_map('category_X', 'key_1'),


@raises(ValueError)
def test_mapping__find_in_map__missing_second_level_key():
    mapping = Mapping('abcde')
    mapping.add_category('category_1').add_item('key_1', 'value_1').add_item('key_2', 'value_2')
    mapping.find_in_map('category_1', 'key_X'),


def test_condition():
    template = {}
    condition = Condition('abcde').expression(Intrinsics.fn_equals('value_1', 'value_2')).to_template(template)
    assert_equal(
        template,
        {'abcde': {'Fn::Equals': ['value_1', 'value_2']}}
    )


def test_resource__properties():
    template = {}
    resource = Resource('abcde').type('type').properties([
        {'key_1': 'value_1'},
        {'key_2': 'value_2'}
    ]).to_template(template)
    assert_equal(
        template,
        {'abcde': {'Type': 'type', 'Properties': {
            'key_1': 'value_1',
            'key_2': 'value_2'
        }}}
    )


def test_resource__add_property():
    template = {}
    resource = Resource('abcde').type('type')
    resource.add_property({'key_1': 'value_1'})
    resource.add_property({'key_2': 'value_2'})
    resource.to_template(template)
    assert_equal(
        template,
        {'abcde': {'Type': 'type', 'Properties': {
            'key_1': 'value_1',
            'key_2': 'value_2'
        }}}
    )


def test_resource__depends_on__resource():
    template = {}
    resource = Resource('abcde').type('type').dependsOn(Resource('res_name')).to_template(template)
    assert_equal(
        template,
        {'abcde': {'Type': 'type', 'DependsOn': 'res_name'}}
    )


def test_resource__depends_on__named_object():
    class named_object(object):
        def __init__(self):
            self.name = 'res_name'
    template = {}
    resource = Resource('abcde').type('type').dependsOn(named_object()).to_template(template)
    assert_equal(
        template,
        {'abcde': {'Type': 'type', 'DependsOn': 'res_name'}}
    )


@raises(ValueError)
def test_resource__depends_on__other():
    Resource('abcde').type('type').dependsOn({})


def test_resource__user_data():
    template = {}
    resource = Resource('abcde').type('type').properties([
        UserData.of(['value_1', 'value_2', 'value_3'])
    ]).to_template(template)
    assert_equal(
        template,
        {'abcde': {'Type': 'type', 'Properties': {
            'UserData': {'Fn::Base64': {'Fn::Join': ['', ['value_1', 'value_2', 'value_3']]}}
        }}}
    )


def test_resource__metadata__config():
    template = {}
    resource = Resource('abcde').type('type')
    resource.metadata(CfnInitMetadata.of(CfnInitMetadata.Config('config').commands('key_1', 'value_1')))
    resource.to_template(template)
    assert_equal(
        template,
        {'abcde': {'Type': 'type', 'Metadata': {
            'AWS::CloudFormation::Init': {
                'config': {
                    'commands': {
                        'key_1': {
                            'command': 'value_1'
                        }
                    }
                }
            }
        }}}
    )


def test_resource__metadata__config_sets():
    template = {}
    resource = Resource('abcde').type('type')
    resource.metadata(CfnInitMetadata.of([
        CfnInitMetadata.ConfigSet('default', [
            CfnInitMetadata.Config('config')
                .commands('key_1', 'value_1')
        ])
    ]))
    resource.to_template(template)
    assert_equal(
        template,
        {'abcde': {'Type': 'type', 'Metadata': {
            'AWS::CloudFormation::Init': {
                'configSets': {
                    'default': ['config']
                },
                'config': {
                    'commands': {
                        'key_1': {
                            'command': 'value_1'
                        }
                    }
                }
            }
        }}}
    )


def test_output__standard():
    template = {}
    output = Output('abcde').description('description').value(Intrinsics.get_att('res_name', 'attr_name')).to_template(template)
    assert_equal(
        template,
        {'abcde': {'Description': 'description', 'Value': {'Fn::GetAtt': ['res_name', 'attr_name']}}}
    )


def test_output__with_export():
    template = {}
    output = Output('abcde').description('description').value(Intrinsics.get_att('res_name', 'attr_name')).export('variable_name').to_template(template)
    assert_equal(
        template,
        {'abcde': {'Description': 'description', 'Value': {'Fn::GetAtt': ['res_name', 'attr_name']}, 'Export': {'Name': 'variable_name'}}}
    )


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


def test_intrinsics_import_value():
    assert_equal(
        Intrinsics.import_value('value'),
        {'Fn::ImportValue': 'value'}
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


def test_intrinsics_sub__with_parameters():
    assert_equal(
        Intrinsics.sub('template', {'key_1': 'value_1', 'key_2': 'value_2', 'key_3': 'value_3'}),
        {'Fn::Sub': ['template', {'key_1': 'value_1', 'key_2': 'value_2', 'key_3': 'value_3'}]}
    )


def test_intrinsics_sub__without_parameters():
    assert_equal(
        Intrinsics.sub('template'),
        {'Fn::Sub': 'template'}
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


def test_user_data_of():
    assert_equal(
        UserData.of(['value_1', 'value_2', 'value_3']),
        {'UserData': {'Fn::Base64': {'Fn::Join': ['', ['value_1', 'value_2', 'value_3']]}}}
    )


def test_cfn_init_metadata_of__config():
    assert_equal(
        CfnInitMetadata.of(CfnInitMetadata.Config('config').commands('key_1', 'value_1')),
        {'AWS::CloudFormation::Init': {'config': {'commands': {'key_1': {'command': 'value_1'}}}}}
    )


def test_cfn_init_metadata_of__config_sets():
    assert_equal(
        CfnInitMetadata.of([CfnInitMetadata.ConfigSet('default', [CfnInitMetadata.Config('config').commands('key_1', 'value_1')])]),
        {'AWS::CloudFormation::Init': {'configSets': {'default': ['config']}, 'config': {'commands': {'key_1': {'command': 'value_1'}}}}}
    )


if __name__ == '__main__':
    nose.main(argv=['nosetests', '-s', '-v'], defaultTest=__file__)
