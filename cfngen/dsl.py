# -*- coding: utf-8 -*-

from collections import OrderedDict
from cfngen.utils import (combine_user_data, inject_params)


class Template(object):

    def __init__(self, version='2010-09-09', description=''):
        self.version = version
        self.description = description
        self.elements = OrderedDict()

    def description(self, description):
        self.description = description

    def get_section(self, section_name):
        if not self.elements.has_key(section_name):
            self.elements[section_name] = []
        return self.elements[section_name]

    def parameters(self, element):
        section = self.get_section('Parameters')
        section.append(element)
        return element

    def mappings(self, element):
        section = self.get_section('Mappings')
        section.append(element)
        return element

    def conditions(self, element):
        section = self.get_section('Conditions')
        section.append(element)
        return element

    def resources(self, element):
        section = self.get_section('Resources')
        section.append(element)
        return element

    def outputs(self, element):
        section = self.get_section('Outputs')
        section.append(element)
        return element

    def to_template(self):
        template = OrderedDict()
        template['AWSTemplateFormatVersion'] = self.version
        template['Description'] = self.description
        for section_name, entries in self.elements.items():
            section = template[section_name] = OrderedDict()
            for element in entries:
                element.to_template(section)

        return template


class Element(object):

    def __init__(self, name):
        self.name = name
        self.attrs = OrderedDict()

    def attributes(self, name, value):
        self.attrs[name] = value
        return self

    def to_template(self, template):
        template[self.name] = self.attrs


class Parameter(Element):

    def __init__(self, name):
        super(Parameter, self).__init__(name)

    def description(self, desc):
        return self.attributes('Description', desc)

    def type(self, name):
        return self.attributes('Type', name)

    def default(self, value):
        return self.attributes('Default', value)


class Mapping(Element):

    def __init__(self, name):
        super(Mapping, self).__init__(name)

    def add_category(self, category):
        self._category = category
        if not self.attrs.has_key(category):
            self.attributes(category, OrderedDict())
            return self

    def add_item(self, key, value):
        m = self.attrs[self._category]
        m[key] = value
        return self

    def find_in_map(self, top_level_key, second_level_key):
        if isinstance(top_level_key, str):
            if not self.attrs.has_key(top_level_key):
                raise ValueError('missing top_level_key. top_level_key: %r' % top_level_key)
            if isinstance(second_level_key, str):
                if not self.attrs[top_level_key].has_key(second_level_key):
                    raise ValueError('missing second_level_key. second_level_key: %r' % second_level_key)

        return Intrinsics.find_in_map(self, top_level_key, second_level_key)


class Condition(Element):

    def __init__(self, name):
        super(Condition, self).__init__(name)

    def expression(self, expression):
        self.expression = expression
        return self

    def to_template(self, template):
        template[self.name] = self.expression


class Resource(Element):

    def __init__(self, name):
        super(Resource, self).__init__(name)

    def type(self, name):
        return self.attributes('Type', name)

    def metadata(self, metadata):
        return self.attributes('Metadata', metadata)

    def dependsOn(self, resource):
        return self.attributes('DependsOn', resource.name)

    def properties(self, props):
        m = self.attrs['Properties'] if self.attrs.has_key('Properties') else OrderedDict()
        for p in props:
            for k, v in p.items():
                m[k] = v
        return self.attributes('Properties', m)

    def add_property(self, prop):
        return self.properties([prop])


class Output(Element):

    def __init__(self, name):
        super(Output, self).__init__(name)

    def description(self, desc):
        return self.attributes('Description', desc)

    def value(self, value):
        return self.attributes('Value', value)


class Attributes(object):

    @staticmethod
    def of(name, value):
        if isinstance(value, Element):
            return {name: Intrinsics.ref(value)}
        else:
            return {name: value}


class Intrinsics(object):

    @staticmethod
    def base64(value_to_encode):
        return {'Fn::Base64': value_to_encode}

    @staticmethod
    def find_in_map(map_name_or_mapping, top_level_key, second_level_key):
        if isinstance(map_name_or_mapping, str):
            map_name = map_name_or_mapping
            return {'Fn::FindInMap': [map_name, top_level_key, second_level_key]}
        elif isinstance(map_name_or_mapping, Mapping):
            mapping = map_name_or_mapping
            return {'Fn::FindInMap': [mapping.name, top_level_key, second_level_key]}
        else:
            raise ValueError('value should be map name or mapping. but %r' % type(map_name_or_mapping))

    @staticmethod
    def fn_and(condions):
        return {'Fn::And': condions}

    @staticmethod
    def fn_equals(value_1, value_2):
        return {'Fn::Equals': [value_1, value_2]}

    @staticmethod
    def fn_if(condition_name, value_if_true, value_if_false):
        return {'Fn::If': [condition_name, value_if_true, value_if_false]}

    @staticmethod
    def fn_not(conditions):
        return {'Fn::Not': conditions}

    @staticmethod
    def fn_or(conditions):
        return {'Fn::Or': conditions}

    @staticmethod
    def get_att(logical_name_of_resource, attribute_name):
        return {'Fn::GetAtt': [logical_name_of_resource, attribute_name]}

    @staticmethod
    def get_azs(region=''):
        return {'Fn::GetAZs': region}

    @staticmethod
    def join(delimiter, list_of_values):
        return {'Fn::Join': [delimiter, list_of_values]}

    @staticmethod
    def select(index, list_of_objects):
        return {'Fn::Select': [index, list_of_objects]}

    @staticmethod
    def ref(logical_name_or_element):
        if isinstance(logical_name_or_element, str):
            logical_name = logical_name_or_element
            return {'Ref': logical_name}
        elif isinstance(logical_name_or_element, Element):
            resource = logical_name_or_element
            return {'Ref': resource.name}
        else:
            raise ValueError('value should be logical name or resource. but %r' % type(logical_name_or_element))


class Pseudos(object):

    @staticmethod
    def account_id():
        return {'Ref': 'AWS::AccountId'}

    @staticmethod
    def notification_arns():
        return {'Ref': 'AWS::NotificationARNs'}

    @staticmethod
    def no_value():
        return {'Ref': 'AWS::NoValue'}

    @staticmethod
    def region():
        return {'Ref': 'AWS::Region'}

    @staticmethod
    def stack_id():
        return {'Ref': 'AWS::StackId'}

    @staticmethod
    def stack_name():
        return {'Ref': 'AWS::StackName'}


class UserData(object):

    @staticmethod
    def of(values):
        return {'UserData': Intrinsics.base64(Intrinsics.join('', values))}

    @staticmethod
    def from_files(files, params):
        user_data = inject_params(combine_user_data(files), params)
        return {'UserData': Intrinsics.base64(Intrinsics.join('', user_data))}


class CfnInitMetadata(object):

    @staticmethod
    def of(values):
        return {'AWS::CloudFormation::Init': values}


if __name__ == '__main__':
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

    api_server.metadata(CfnInitMetadata.of({
        'configSets': {
            'default': ['SetupRepos', 'Install', 'Configure', 'Start']
        },
        'SetupRepos': {
            'commands': {
                'import_td-agent_GPG-KEY': {'command': 'rpm --import https://packages.treasuredata.com/GPG-KEY-td-agent'}
            }
        },
        'Install': {
            'packages': {
                'yum': {
                    'dstat': [],
                    'td-agent': []
                }
            },
            'commands': {
                'install_plugins': {'command': 'td-agent-gem install fluent-plugin-dstat'}
            }
        },
        'Configure': {
            'files': {
                '/etc/td-agent/td-agent.conf': {
                    'content': Intrinsics.join('', [
                        '<source>\n',
                        '  type dstat\n',
                        '  tag dstat\n',
                        '  option -cdnm --tcp --udp\n',
                        '  delay 10\n',
                        '</source>\n'
                    ]),
                    'mode': '000644',
                    'owner': 'root',
                    'group': 'root'
                }
            }
        },
        'Start': {
            'services': {
                'sysvinit': {
                    'td-agent': {'enabled': 'true', 'ensureRunning': 'true'}
                }
            }
        }
    }))

    from os import remove
    remove('my_script.sh')
    remove('my_config.yml')

    t.outputs(Output('VpcId').description('-').value(Intrinsics.ref(vpc)))
    t.outputs(Output('ApiServerSubnet').description('-').value(Intrinsics.ref(api_server_subnet)))
    t.outputs(Output('VPCDefaultSecurityGroup').description('-').value(Intrinsics.ref(vpc_default_security_group)))

    from json import dumps
    print(dumps(t.to_template(), indent=2, separators=(',', ': ')))
