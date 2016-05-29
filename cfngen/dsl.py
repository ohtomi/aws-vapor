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
        return self

    def mappings(self, element):
        section = self.get_section('Mappings')
        section.append(element)
        return self

    def resources(self, element):
        section = self.get_section('Resources')
        section.append(element)
        return self

    def outputs(self, element):
        section = self.get_section('Outputs')
        section.append(element)
        return self

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


class Mapping(Element):

    def __init__(self, name):
        super(Mapping, self).__init__(name)

    def define(self, category, tuples):
        return self.attributes(category, [{k: v} for k, v in tuples])


class Resource(Element):

    def __init__(self, name):
        super(Resource, self).__init__(name)

    def type(self, name):
        return self.attributes('Type', name)

    def dependsOn(self, resource):
        return self.attributes('DependsOn', resource.name)

    def properties(self, props):
        return self.attributes('Properties', props)

    def property(self, prop):
        for name, maybe_props in self.attrs.items():
            if name == 'Properties':
                maybe_props.append(prop)
                return self
        return self.properties([prop])


class Output(Element):

    def __init__(self, name):
        super(Output, self).__init__(name)

    def description(self, desc):
        return self.attributes('Description', desc)

    def value(self, value):
        return self.attributes('Value', value)


class Attribute(object):

    @staticmethod
    def of(name, value):
        if isinstance(value, list):
            m = OrderedDict()
            for any in value:
                if isinstance(any, dict):
                    for k, v in any.iteritems():
                        m[k] = v
                else:
                    raise ValueError('TODO')
            return m
        elif isinstance(value, Element):
            return {name: Intrinsics.ref(value)}
        else:
            return {name: value}


class Intrinsics(object):

    @staticmethod
    def base64(value_to_encode):
        return {'Fn::Base64': value_to_encode}

    @staticmethod
    def find_in_map(map_name, top_level_key, second_level_key):
        return {'Fn::FindInMap': [map_name, top_level_key, second_level_key]}

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
            return {'Ref': logical_name_or_element}
        elif isinstance(logical_name_or_element, Element):
            return {'Ref': logical_name_or_element.name}
        else:
            raise ValueError('TODO')


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



if __name__ == '__main__':
    t = Template(description='Sample Template')

    t.parameters(Parameter('KeyName')
        .description('Name of an existing EC2 KeyPair to enable SSH access to the server')
        .type('String')
    )

    t.mappings(Mapping('GroupToCIDR')
        .define('VPC', [
            ('CIDR', '10.104.0.0/16')
        ])
        .define('ApiServerSubnet', [
            ('CIDR', '10.104.128.0/24')
        ])
        .define('ComputingServerSubnet', [
            ('CIDR', '10.104.144.0/20')
        ])
        .define('MongoDBSubnet', [
            ('CIDR', '10.104.129.0/24')
        ])
    )

    vpc = Resource('VPC').type('AWS::EC2::VPC').properties([
        Attribute.of('CidrBlock', Intrinsics.find_in_map('GroupToCIDR', 'VPC', 'CIDR')),
        Attribute.of('InstanceTenancy', 'default')
    ])
    t.resources(vpc)

    igw = Resource('InternetGateway').type('AWS:EC2::InternetGateway')
    t.resources(igw)

    attach_igw = Resource('AttachInternetGateway').type('AWS::EC2::VPCGatewayAttachment').properties([
        Attribute.of('VpcId', vpc),
        Attribute.of('InternetGatewayId', igw)
    ])
    t.resources(attach_igw)

    t.resources(Resource('NatGatewayEIP').type('AWS::EC2::EIP').dependsOn(attach_igw).properties([
        Attribute.of('Domain', 'vpc')
    ]))

    nat_gw = Resource('NatGateway').type('AWS::EC2::NatGateway').properties([
        Attribute.of('AllocationId', Intrinsics.get_att('NatGatewayEIP', 'AllocationId'))
    ])
    t.resources(nat_gw)

    public_route_table = Resource('PublicRouteTable').type('AWS::EC2::RouteTable').dependsOn(attach_igw).properties([
        Attribute.of('VpcId', vpc)
    ])
    t.resources(public_route_table)

    private_route_table = Resource('PrivateRouteTable').type('AWS::EC2::RouteTable').dependsOn(attach_igw).properties([
        Attribute.of('VpcId', vpc)
    ])
    t.resources(private_route_table)

    t.resources(Resource('PublicRoute').type('AWS::EC2::Route').dependsOn(attach_igw).properties([
        Attribute.of('RouteTableId', public_route_table),
        Attribute.of('DestinationCidrBlock', '0.0.0.0/0'),
        Attribute.of('GatewayId', igw)
    ]))

    t.resources(Resource('PrivateRoute').type('AWS::EC2::Route').dependsOn(attach_igw).properties([
        Attribute.of('RouteTableId', private_route_table),
        Attribute.of('DestinationCidrBlock', '0.0.0.0/0'),
        Attribute.of('GatewayId', nat_gw)
    ]))

    api_server_subnet = Resource('ApiServerSubnet').type('AWS::EC2::Subnet').dependsOn(attach_igw).properties([
        Attribute.of('VpcId', vpc),
        Attribute.of('AvailabilityZone', Intrinsics.select('0', Intrinsics.get_azs())),
        Attribute.of('CidrBlock', Intrinsics.find_in_map('GroupToCIDR', 'ApiServerSubnet', 'CIDR')),
        Attribute.of('MapPublicIpOnLaunch', 'true')
    ])
    t.resources(api_server_subnet)
    nat_gw.property(Attribute.of('SubnetId', api_server_subnet))

    computing_server_subnet = Resource('ComputingServerSubnet').type('AWS::EC2::Subnet').dependsOn(attach_igw).properties([
        Attribute.of('VpcId', vpc),
        Attribute.of('AvailabilityZone', Intrinsics.select('0', Intrinsics.get_azs())),
        Attribute.of('CidrBlock', Intrinsics.find_in_map('GroupToCIDR', 'ComputingServerSubnet', 'CIDR')),
        Attribute.of('MapPublicIpOnLaunch', 'false')
    ])
    t.resources(computing_server_subnet)

    mongo_db_subnet = Resource('MongoDBSubnet').type('AWS::EC2::Subnet').dependsOn(attach_igw).properties([
        Attribute.of('VpcId', vpc),
        Attribute.of('AvailabilityZone', Intrinsics.select('0', Intrinsics.get_azs())),
        Attribute.of('CidrBlock', Intrinsics.find_in_map('GroupToCIDR', 'MongoDBSubnet', 'CIDR')),
        Attribute.of('MapPublicIpOnLaunch', 'false')
    ])
    t.resources(mongo_db_subnet)

    t.resources(Resource('ApiServerSubnetRouteTableAssociation').type('AWS::EC2::SubnetRouteTableAssociation').properties([
        Attribute.of('SubnetId', api_server_subnet),
        Attribute.of('RouteTableId', public_route_table)
    ]))

    t.resources(Resource('ComputingServerSubnetRouteTableAssociation').type('AWS::EC2::SubnetRouteTableAssociation').properties([
        Attribute.of('SubnetId', computing_server_subnet),
        Attribute.of('RouteTableId', private_route_table)
    ]))

    t.resources(Resource('MongoDBSubnetRouteTableAssociation').type('AWS::EC2::SubnetRouteTableAssociation').properties([
        Attribute.of('SubnetId', mongo_db_subnet),
        Attribute.of('RouteTableId', private_route_table)
    ]))

    vpc_default_security_group = Resource('VPCDefaultSecurityGroup').type('AWS::EC2::SecurityGroup').properties([
        Attribute.of('VpcId', vpc),
        Attribute.of('GroupDescription', 'Allow all communications in VPC'),
        Attribute.of('SecurityGroupIngress', [ # TODO
            {'IpProtocol': 'tcp', 'FromPort': '0', 'ToPort': '65535', 'CidrIp': Intrinsics.find_in_map('GroupToCIDR', 'VPC', 'CIDR')},
            {'IpProtocol': 'udp', 'FromPort': '0', 'ToPort': '65535', 'CidrIp': Intrinsics.find_in_map('GroupToCIDR', 'VPC', 'CIDR')},
            {'IpProtocol': 'icmp', 'FromPort': '-1', 'ToPort': '-1', 'CidrIp': Intrinsics.find_in_map('GroupToCIDR', 'VPC', 'CIDR')}
        ])
    ])
    t.resources(vpc_default_security_group)

    t.outputs(Output('VpcId').description('-').value(Intrinsics.ref(vpc)))
    t.outputs(Output('ApiServerSubnet').description('-').value(Intrinsics.ref(api_server_subnet)))
    t.outputs(Output('ComputingServerSubnet').description('-').value(Intrinsics.ref(computing_server_subnet)))
    t.outputs(Output('MongoDBSubnet').description('-').value(Intrinsics.ref(mongo_db_subnet)))
    t.outputs(Output('VPCDefaultSecurityGroup').description('-').value(Intrinsics.ref(vpc_default_security_group)))

    from json import dumps
    print(dumps(t.to_template(), indent=2, separators=(',', ': ')))
