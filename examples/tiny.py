# -*- coding: utf-8 -*-

from aws_vapor.dsl import (
    Template, Parameter, Mapping, Condition, Resource, Output,
    Attributes, Intrinsics, Pseudos,
    UserData, CfnInitMetadata
)

def generate():
    t = Template(description='see. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/conditions-section-structure.html')

    m = t.mappings(Mapping('RegionMap')
        .add_category('us-east-1').add_item('AMI', 'ami-7f418316').add_item('TestAZ', 'us-east-1a')
        .add_category('us-west-1').add_item('AMI', 'ami-951945d0').add_item('TestAZ', 'us-west-1a')
        .add_category('us-west-2').add_item('AMI', 'ami-16fd7026').add_item('TestAZ', 'us-west-2a')
    )

    p = t.parameters(Parameter('EnvType')
        .description('Environment type.')
        .type('String')
        .default('test')
        .attributes('AllowedValues', ['prod', 'test'])
        .attributes('ConstraintDescription', 'must specify prod or test.')
    )

    c = t.conditions(Condition('CreateProdResources').expression(Intrinsics.fn_equals(Intrinsics.ref('EnvType'), 'prod')))

    r = t.resources(Resource('EC2Instance').type('AWS::EC2::Instance').properties([
        Attributes.of('ImageId', m.find_in_map(Pseudos.region(), 'AMI'))
    ]))

    new_volume = {
        'Type': 'AWS:EC2::Volume',
        'Condition': c.name,
        'Properties': {
            'Size': '100',
            'AvailabilityZone': Intrinsics.get_att(r.name, 'AvailabilityZone')
        }
    }

    mount_point = {
        'Type': 'AWS::EC2::VolumeAttachment',
        'Condition': c.name,
        'Properties': {
            'InstanceId': Intrinsics.ref(r),
            'VolumeId': Intrinsics.ref('NewVolume'),
            'Device': '/dev/sdh'
        }
    }

    r.attributes('MountPoint', mount_point)
    r.attributes('NewVolume', new_volume)

    o = t.outputs(Output('VolumeId').value(Intrinsics.ref('NewVolume')).attributes('Condition', c.name))

    return t
