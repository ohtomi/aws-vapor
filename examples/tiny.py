# -*- coding: utf-8 -*-

from aws_vapor.dsl import (
    Template, Parameter, Mapping, Condition, Resource, Output,
    Attributes, Intrinsics, Pseudos,
    UserData, CfnInitMetadata
)


def generate():
    t = Template(description='Sample Template')

    t.parameters(Parameter('SampleParameter')
        .description('this is sample parameter')
        .type('String')
    )

    t.mappings(Mapping('SampleMapping')
        .add_category('Category1').add_item('ItemKey1', 'Item Value1').add_item('ItemKey2', 'Item Value2')
        .add_category('Category2').add_item('ItemKey3', 'Item Value3').add_item('ItemKey4', 'Item Value4')
    )

    t.conditions(Condition('SampleCondition').expression(Intrinsics.fn_equals(Intrinsics.ref('EnvType'), 'prod')))

    vpc = t.resources(Resource('SampleResource').type('AWS::EC2::VPC').properties([
        Attributes.of('CidrBlock', '10.0.0.0/16'),
        Attributes.of('InstanceTenancy', 'default')
    ]))

    t.outputs(Output('SampleOutput').description('-').value(Intrinsics.ref(vpc)))

    return t
