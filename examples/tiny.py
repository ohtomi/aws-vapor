# -*- coding: utf-8 -*-

from aws_vapor.dsl import Template
from aws_vapor.dsl import Metadatum
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


def generate():
    t = Template(description='see. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/conditions-section-structure.html')

    meta = t.metadata(Metadatum('MetadataKey').attributes('name', 'value'))

    m = t.mappings(Mapping('RegionMap')
        .add_category('us-east-1').add_item('AMI', 'ami-7f418316').add_item('TestAZ', 'us-east-1a')
        .add_category('us-west-1').add_item('AMI', 'ami-951945d0').add_item('TestAZ', 'us-west-1a')
        .add_category('us-west-2').add_item('AMI', 'ami-16fd7026').add_item('TestAZ', 'us-west-2a')
    )

    p = t.parameters(Parameter('EnvType')
        .description('Environment type.')
        .type('String')
        .default('test')
        .allowed_values(['prod', 'test'])
        .constraint_description('must specify prod or test.')
    )

    c = t.conditions(Condition('CreateProdResources').expression(Intrinsics.fn_equals(Intrinsics.ref('EnvType'), 'prod')))

    r_ec2instance = t.resources(Resource('EC2Instance').type('AWS::EC2::Instance').properties([
        Attributes.of('ImageId', m.find_in_map(Pseudos.region(), 'AMI'))
    ]))

    r_new_volume = t.resources(Resource('NewVolume').type('AWS:EC2::Volume').properties([
        Attributes.of('Size', '100'),
        Attributes.of('AvailabilityZone', Intrinsics.get_att(r_ec2instance.name, 'AvailabilityZone'))
    ])).attributes('Condition', c.name)

    r_mount_point = t.resources(Resource('MountPoint').type('AWS::EC2::VolumeAttachment').properties([
        Attributes.of('InstanceId', Intrinsics.ref(r_ec2instance)),
        Attributes.of('VolumeId', Intrinsics.ref('NewVolume')),
        Attributes.of('Device', '/dev/sdh')
    ])).attributes('Condition', c.name)

    o = t.outputs(Output('VolumeId').value(Intrinsics.ref('NewVolume')).attributes('Condition', c.name))

    return t
