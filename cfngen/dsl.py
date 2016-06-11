# -*- coding: utf-8 -*-

from collections import OrderedDict


class Template(object):

    def __init__(self, version='2010-09-09', description=''):
        self.version = version
        self.description = description
        self.elements = OrderedDict()

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

    def category(self, category):
        self._category = category
        if not self.attrs.has_key(category):
            self.attributes(category, OrderedDict())
            return self

    def item(self, key, value):
        m = self.attrs[self._category]
        m[key] = value
        return self

    def find_in_map(self, top_level_key, second_level_key):
        if not self.attrs.has_key(top_level_key):
            raise ValueError('missing top_level_key. top_level_key: %r' % top_level_key)
        m = self.attrs[top_level_key]
        if not m.has_key(second_level_key):
            raise ValueError('missing second_level_key. second_level_key: %r' % second_level_key)
        return Intrinsics.find_in_map(self, top_level_key, second_level_key)


class Resource(Element):

    def __init__(self, name):
        super(Resource, self).__init__(name)

    def type(self, name):
        return self.attributes('Type', name)

    def dependsOn(self, resource):
        return self.attributes('DependsOn', resource.name)

    def properties(self, props):
        m = self.attrs['Properties'] if self.attrs.has_key('Properties') else OrderedDict()
        for p in props:
            for k, v in p.items():
                m[k] = v
        return self.attributes('Properties', m)

    def property(self, prop):
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
            m = mapping.attrs[top_level_key]
            return {'Fn::FindInMap': [mapping.name, top_level_key, second_level_key]}
        else:
            raise ValueError('value should be map name or mapping. but %r' % type(map_name_or_mapping))

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


class Pseudo(object):

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


if __name__ == '__main__':
    t = Template(description='Sample Template')

    key_name = t.parameters(Parameter('KeyName')
        .description('Name of an existing EC2 KeyPair to enable SSH access to the server')
        .type('String')
        .default('Key')
    )

    group_to_cidr = t.mappings(Mapping('GroupToCIDR')
        .category('VPC').item('CIDR', '10.104.0.0/16')
        .category('ApiServerSubnet').item('CIDR', '10.104.128.0/24')
        .category('ComputingServerSubnet').item('CIDR', '10.104.144.0/20')
        .category('MongoDBSubnet').item('CIDR', '10.104.129.0/24')
    )

    vpc = t.resources(Resource('VPC').type('AWS::EC2::VPC').properties([
        Attributes.of('CidrBlock', group_to_cidr.find_in_map('VPC', 'CIDR')),
        Attributes.of('InstanceTenancy', 'default')
    ]))

    igw = t.resources(Resource('InternetGateway').type('AWS:EC2::InternetGateway'))

    attach_igw = t.resources(Resource('AttachInternetGateway').type('AWS::EC2::VPCGatewayAttachment').properties([
        Attributes.of('VpcId', vpc),
        Attributes.of('InternetGatewayId', igw)
    ]))

    t.resources(Resource('NatGatewayEIP').type('AWS::EC2::EIP').dependsOn(attach_igw).properties([
        Attributes.of('Domain', 'vpc')
    ]))

    nat_gw = t.resources(Resource('NatGateway').type('AWS::EC2::NatGateway').properties([
        Attributes.of('AllocationId', Intrinsics.get_att('NatGatewayEIP', 'AllocationId'))
    ]))

    public_route_table = t.resources(Resource('PublicRouteTable').type('AWS::EC2::RouteTable').dependsOn(attach_igw).properties([
        Attributes.of('VpcId', vpc)
    ]))

    private_route_table = t.resources(Resource('PrivateRouteTable').type('AWS::EC2::RouteTable').dependsOn(attach_igw).properties([
        Attributes.of('VpcId', vpc)
    ]))

    t.resources(Resource('PublicRoute').type('AWS::EC2::Route').dependsOn(attach_igw).properties([
        Attributes.of('RouteTableId', public_route_table),
        Attributes.of('DestinationCidrBlock', '0.0.0.0/0'),
        Attributes.of('GatewayId', igw)
    ]))

    t.resources(Resource('PrivateRoute').type('AWS::EC2::Route').dependsOn(attach_igw).properties([
        Attributes.of('RouteTableId', private_route_table),
        Attributes.of('DestinationCidrBlock', '0.0.0.0/0'),
        Attributes.of('GatewayId', nat_gw)
    ]))

    api_server_subnet = t.resources(Resource('ApiServerSubnet').type('AWS::EC2::Subnet').dependsOn(attach_igw).properties([
        Attributes.of('VpcId', vpc),
        Attributes.of('AvailabilityZone', Intrinsics.select('0', Intrinsics.get_azs())),
        Attributes.of('CidrBlock', group_to_cidr.find_in_map('ApiServerSubnet', 'CIDR')),
        Attributes.of('MapPublicIpOnLaunch', 'true')
    ]))
    nat_gw.property(Attributes.of('SubnetId', api_server_subnet))

    computing_server_subnet = t.resources(Resource('ComputingServerSubnet').type('AWS::EC2::Subnet').dependsOn(attach_igw).properties([
        Attributes.of('VpcId', vpc),
        Attributes.of('AvailabilityZone', Intrinsics.select('0', Intrinsics.get_azs())),
        Attributes.of('CidrBlock', group_to_cidr.find_in_map('ComputingServerSubnet', 'CIDR')),
        Attributes.of('MapPublicIpOnLaunch', 'false')
    ]))

    mongo_db_subnet = t.resources(Resource('MongoDBSubnet').type('AWS::EC2::Subnet').dependsOn(attach_igw).properties([
        Attributes.of('VpcId', vpc),
        Attributes.of('AvailabilityZone', Intrinsics.select('0', Intrinsics.get_azs())),
        Attributes.of('CidrBlock', group_to_cidr.find_in_map('MongoDBSubnet', 'CIDR')),
        Attributes.of('MapPublicIpOnLaunch', 'false')
    ]))

    t.resources(Resource('ApiServerSubnetRouteTableAssociation').type('AWS::EC2::SubnetRouteTableAssociation').properties([
        Attributes.of('SubnetId', api_server_subnet),
        Attributes.of('RouteTableId', public_route_table)
    ]))

    t.resources(Resource('ComputingServerSubnetRouteTableAssociation').type('AWS::EC2::SubnetRouteTableAssociation').properties([
        Attributes.of('SubnetId', computing_server_subnet),
        Attributes.of('RouteTableId', private_route_table)
    ]))

    t.resources(Resource('MongoDBSubnetRouteTableAssociation').type('AWS::EC2::SubnetRouteTableAssociation').properties([
        Attributes.of('SubnetId', mongo_db_subnet),
        Attributes.of('RouteTableId', private_route_table)
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
        Attributes.of('ImageId', 'ami-12345678'),
        Attributes.of('InstanceType', 't2.micro'),
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
    api_server.property(UserData.of([
        'yum update -y\n',
        'yum update -y aws-cfn-bootstrap\n'
        '/opt/aws/bin/cfn-init -v ',
        '    --stack ', Pseudo.stack_id(),
        '    --resource ', api_server.name,
        '    --region ', Pseudo.region(), '\n',
        '/opt/aws/bin/cfn-signal -e $? ',
        '    --stack ', Pseudo.stack_id(),
        '    --resource ', api_server.name,
        '    --region ', Pseudo.region(), '\n'
    ]))

    t.outputs(Output('VpcId').description('-').value(Intrinsics.ref(vpc)))
    t.outputs(Output('ApiServerSubnet').description('-').value(Intrinsics.ref(api_server_subnet)))
    t.outputs(Output('ComputingServerSubnet').description('-').value(Intrinsics.ref(computing_server_subnet)))
    t.outputs(Output('MongoDBSubnet').description('-').value(Intrinsics.ref(mongo_db_subnet)))
    t.outputs(Output('VPCDefaultSecurityGroup').description('-').value(Intrinsics.ref(vpc_default_security_group)))

    from json import dumps
    print(dumps(t.to_template(), indent=2, separators=(',', ': ')))
