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
    t = Template(description='td-agent Template')

    ami_id = t.parameters(Parameter('AmiId')
        .description('EC2 machine image ID of the sample server')
        .type('AWS::EC2::Image::Id')
    )

    instance_type = t.parameters(Parameter('InstanceType')
        .description('EC2 instance type of the sample server')
        .type('AWS::EC2::KeyPair::KeyName')
    )

    security_group_ids = t.parameters(Parameter('SecurityGroupIds')
        .description('List of security group IDs of the sample server')
        .type('List<AWS::EC2::SecurityGroup::Id>')
    )

    key_name = t.parameters(Parameter('KeyName')
        .description('Name of an existing EC2 key pair to enable SSH access to the sample server')
        .type('AWS::EC2::KeyPair::KeyName')
    )

    subnet_id = t.parameters(Parameter('SubnetId')
        .description('Subnet ID which the sample server runs on')
        .type('AWS::EC2::Subnet::Id')
    )

    sample_server = t.resources(Resource('MongoDBServer').type('AWS::EC2::Instance').properties([
        Attributes.of('ImageId', ami_id),
        Attributes.of('InstanceType', instance_type),
        Attributes.of('SecurityGroupIds', security_group_ids),
        Attributes.of('KeyName', key_name),
        Attributes.of('SubnetId', subnet_id)
    ]))

    sample_server.add_property(UserData.from_files([
        ('files/x-shellscript', 'x-shellscript'),
        ('files/cloud-config', 'cloud-config')
    ], {
        'stack_id': Pseudos.stack_id(),
        'resource_name': sample_server.name,
        'region': Pseudos.region()
    }))

    sample_server.metadata(CfnInitMetadata.of([
        CfnInitMetadata.Init([
            CfnInitMetadata.ConfigSet('default', [
                CfnInitMetadata.Config('SetupRepos')
                    .commands('import_td-agent_GPG-KEY', 'rpm --import https://packages.treasuredata.com/GPG-KEY-td-agent')
                ,
                CfnInitMetadata.Config('Install')
                    .packages('yum', 'dstat')
                    .packages('yum', 'td-agent')
                    .commands('install_td-agent_plugin', 'td-agnet-gem install fluent-plugin-dstat fluent-plugin-map fluent-plugin-forest')
                ,
                CfnInitMetadata.Config('Configure')
                    .files('/etc/td-agent/td-agent.conf', local_file_path='files/td-agent.conf', mode='000644', owner='root', group='root')
                ,
                CfnInitMetadata.Config('Start')
                    .services('sysvinit', 'td-agent', enabled=True, ensure_running=True)
            ])
        ])
    ]))

    return t
