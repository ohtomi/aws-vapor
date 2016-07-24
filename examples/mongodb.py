# -*- coding: utf-8 -*-

from aws_vapor.dsl import (
    Template, Parameter, Mapping, Condition, Resource, Output,
    Attributes, Intrinsics, Pseudos,
    UserData, CfnInitMetadata
)


def generate():
    t = Template(description='MongoDB Template')

    ami_id = t.parameters(Parameter('AmiId')
        .description('EC2 machine image ID of the MongoDB server')
        .type('AWS::EC2::Image::Id')
    )

    instance_type = t.parameters(Parameter('InstanceType')
        .description('EC2 instance type of the MongoDB server')
        .type('AWS::EC2::KeyPair::KeyName')
    )

    security_group_ids = t.parameters(Parameter('SecurityGroupIds')
        .description('List of security group IDs of the MongoDB server')
        .type('List<AWS::EC2::SecurityGroup::Id>')
    )

    key_name = t.parameters(Parameter('KeyName')
        .description('Name of an existing EC2 key pair to enable SSH access to the MongoDB server')
        .type('AWS::EC2::KeyPair::KeyName')
    )

    subnet_id = t.parameters(Parameter('SubnetId')
        .description('Subnet ID which the MongoDB server runs on')
        .type('AWS::EC2::Subnet::Id')
    )

    mongodb_server = t.resources(Resource('MongoDBServer').type('AWS::EC2::Instance').properties([
        Attributes.of('ImageId', ami_id),
        Attributes.of('InstanceType', instance_type),
        Attributes.of('SecurityGroupIds', security_group_ids),
        Attributes.of('KeyName', key_name),
        Attributes.of('SubnetId', subnet_id)
    ]))

    mongodb_server.add_property(UserData.from_files([
        ('files/x-shellscript', 'x-shellscript'),
        ('files/cloud-config', 'cloud-config')
    ], {
        'stack_id': Pseudos.stack_id(),
        'resource_name': mongodb_server.name,
        'region': Pseudos.region()
    }))

    mongodb_server.metadata(CfnInitMetadata.of([
        CfnInitMetadata.ConfigSet('default', [
            CfnInitMetadata.Config('SetupRepos')
                .files('/etc/yum.repos.d/mongodb-org.3.2.repo', CfnInitMetadata.from_file('files/mongodb-org-3.2.repo'), mode='00644', owner='root', group='root')
                .commands('import_mongodb_public_key', 'rpm --import https://www.mongodb.org/static/pgp/server-3.2.asc')
            ,
            CfnInitMetadata.Config('Install')
                .packages('yum', 'mongodb-org-server')
                .packages('yum', 'mongodb-org-shell')
                .packages('yum', 'mongodb-org-tools')
            ,
            CfnInitMetadata.Config('Configure')
                .files('/etc/mongod.conf', CfnInitMetadata.from_file('files/mongod.conf'), mode='000644', owner='root', group='root')
                .commands('make_data_directory', 'mkdir -p /data/db; chmod 777 /data/db')
            ,
            CfnInitMetadata.Config('Start')
                .services('sysvinit', 'mongod', enabled=True, ensure_running=True)
        ])
    ]))

    return t
