# -*- coding: utf-8 -*-

from json import dumps
from aws_vapor.dsl.basic import (
    Template, Parameter, Mapping, Condition, Resource, Output,
    Attributes, Intrinsics, Pseudos
)
from aws_vapor.dsl.metadata import (
    UserData, CfnInitMetadata
)


t = Template(description='Sample Template')

key_name = t.parameters(Parameter('KeyName')
    .description('Name of an existing EC2 KeyPair to enable SSH access to the api server')
    .type('String')
    .default('Key')
)

instance_type = t.parameters(Parameter('InstanceType')
    .description('EC2 instance type of the api server')
    .type('String')
    .default('t2.micro')
)

group_to_cidr = t.mappings(Mapping('GroupToCIDR')
    .add_category('VPC').add_item('CIDR', '10.104.0.0/16')
    .add_category('ApiServerSubnet').add_item('CIDR', '10.104.128.0/24')
)

region_to_ami = t.mappings(Mapping('RegionToAMI')
    .add_category('ap-northeast-1').add_item('AMI', 'ami-a1bec3a0')
)

t.conditions(Condition('CreateProdResources').expression(Intrinsics.fn_equals(Intrinsics.ref('EnvType'), 'prod')))

vpc = t.resources(Resource('VPC').type('AWS::EC2::VPC').properties([
    Attributes.of('CidrBlock', group_to_cidr.find_in_map('VPC', 'CIDR')),
    Attributes.of('InstanceTenancy', 'default')
]))

igw = t.resources(Resource('InternetGateway').type('AWS:EC2::InternetGateway'))

attach_igw = t.resources(Resource('AttachInternetGateway').type('AWS::EC2::VPCGatewayAttachment').properties([
    Attributes.of('VpcId', vpc),
    Attributes.of('InternetGatewayId', igw)
]))

public_route_table = t.resources(Resource('PublicRouteTable').type('AWS::EC2::RouteTable').dependsOn(attach_igw).properties([
    Attributes.of('VpcId', vpc)
]))

t.resources(Resource('PublicRoute').type('AWS::EC2::Route').dependsOn(attach_igw).properties([
    Attributes.of('RouteTableId', public_route_table),
    Attributes.of('DestinationCidrBlock', '0.0.0.0/0'),
    Attributes.of('GatewayId', igw)
]))

api_server_subnet = t.resources(Resource('ApiServerSubnet').type('AWS::EC2::Subnet').dependsOn(attach_igw).properties([
    Attributes.of('VpcId', vpc),
    Attributes.of('AvailabilityZone', Intrinsics.select('0', Intrinsics.get_azs())),
    Attributes.of('CidrBlock', group_to_cidr.find_in_map('ApiServerSubnet', 'CIDR')),
    Attributes.of('MapPublicIpOnLaunch', 'true')
]))

t.resources(Resource('ApiServerSubnetRouteTableAssociation').type('AWS::EC2::SubnetRouteTableAssociation').properties([
    Attributes.of('SubnetId', api_server_subnet),
    Attributes.of('RouteTableId', public_route_table)
]))

vpc_default_security_group = t.resources(Resource('VPCDefaultSecurityGroup').type('AWS::EC2::SecurityGroup').properties([
    Attributes.of('VpcId', vpc),
    Attributes.of('GroupDescription', 'Allow all communications in VPC'),
    Attributes.of('SecurityGroupIngress', [
        {'IpProtocol': 'tcp', 'FromPort': '0', 'ToPort': '65535', 'CidrIp': group_to_cidr.find_in_map('VPC', 'CIDR')},
        {'IpProtocol': 'udp', 'FromPort': '0', 'ToPort': '65535', 'CidrIp': group_to_cidr.find_in_map('VPC', 'CIDR')},
        {'IpProtocol': 'icmp', 'FromPort': '-1', 'ToPort': '-1', 'CidrIp': group_to_cidr.find_in_map('VPC', 'CIDR')}
    ])
]))

api_server_security_group = t.resources(Resource('ApiServerSecurityGroup').type('AWS::EC2::SecurityGroup').properties([
    Attributes.of('VpcId', vpc),
    Attributes.of('GroupDescription', 'Enable Web access to the api server via port 80'),
    Attributes.of('SecurityGroupIngress', [
        {'IpProtocol': 'tcp', 'FromPort': '80', 'ToPort': '80', 'CidrIp': '0.0.0.0/0'}
    ])
]))

api_server = t.resources(Resource('ApiServer').type('AWS::EC2::Instance').properties([
    Attributes.of('ImageId', region_to_ami.find_in_map(Pseudos.region(), 'AMI')),
    Attributes.of('InstanceType', instance_type),
    Attributes.of('SecurityGroupIds', [
        Intrinsics.ref(vpc_default_security_group),
        Intrinsics.ref(api_server_security_group)
    ]),
    Attributes.of('KeyName', key_name),
    Attributes.of('SubnetId', 'subnet-12345678'),
    Attributes.of('Tags', [
        {'Key': 'ServerRole', 'Value': 'ApiServer'}
    ])
]))

with open('my_script.sh', 'w') as f:
    f.write('#!/bin/bash -xe\n')
    f.write('yum update -y\n')
    f.write('yum update -y aws-cfn-bootstrap\n')
    f.write('/opt/aws/bin/cfn-init -v ')
    f.write('    --stack {{ stack_id }}')
    f.write('    --resource {{ resource_name }}')
    f.write('    --region {{ region }}\n')
    f.write('/opt/aws/bin/cfn-signal -e $? ')
    f.write('    --stack {{ stack_id }}')
    f.write('    --resource {{ resource_name }}')
    f.write('    --region {{ region }}\n')
with open('my_config.yml', 'w') as f:
    f.write('#cloud-config\n')
    f.write('timezone: Asia/Tokyo\n')
    f.write('locale: ja_JP.UTF-8\n')

api_server.add_property(UserData.from_files([
    ('my_script.sh', 'x-shellscript'),
    ('my_config.yml', 'cloud-config')
], {
    'stack_id': Pseudos.stack_id(),
    'resource_name': api_server.name,
    'region': Pseudos.region()
}))

with open('td-agent.conf', 'w') as f:
    f.write('<source>\n')
    f.write('  type dstat\n')
    f.write('  tag dstat\n')
    f.write('  option -cdnm --tcp --udp\n')
    f.write('  delay 10\n')
    f.write('</source>\n')

api_server.metadata(CfnInitMetadata.of([
    CfnInitMetadata.ConfigSet('default', [
        CfnInitMetadata.Config('SetupRepos')
            .commands('import_td-agent_GPG-KEY', 'rpm --import https://packages.treasuredata.com/GPG-KEY-td-agent')
        ,
        CfnInitMetadata.Config('Install')
            .packages('yum', 'dstat')
            .packages('yum', 'td-agent')
            .commands('install_plugins', 'td-agent-gem install fluent-plugin-dstat')
        ,
        CfnInitMetadata.Config('Configure')
            .files('/etc/td-agent/td-agent.conf', CfnInitMetadata.from_file('td-agent.conf'), mode='000644', owner='root', group='root')
        ,
        CfnInitMetadata.Config('Start')
            .services('sysvinit', 'td-agent', enabled=True, ensure_running=True)
    ])
]))

from os import remove
remove('my_script.sh')
remove('my_config.yml')
remove('td-agent.conf')

t.outputs(Output('VpcId').description('-').value(Intrinsics.ref(vpc)))
t.outputs(Output('ApiServerSubnet').description('-').value(Intrinsics.ref(api_server_subnet)))
t.outputs(Output('VPCDefaultSecurityGroup').description('-').value(Intrinsics.ref(vpc_default_security_group)))

print(dumps(t.to_template(), indent=2, separators=(',', ': ')))
