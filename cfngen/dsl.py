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

    def category(self, category):
        self._category = category
        if not self.attrs.has_key(category):
            self.attributes(category, OrderedDict())
            return self

    def item(self, key, value):
        m = self.attrs[self._category]
        m[key] = value
        return self


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
        if isinstance(value, list):
            return {name: value}
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
            raise ValueError('value should be logical name or element. but %r' % logical_name_or_element)


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
        .category('VPC').item('CIDR', '10.104.0.0/16')
        .category('ApiServerSubnet').item('CIDR', '10.104.128.0/24')
        .category('ComputingServerSubnet').item('CIDR', '10.104.144.0/20')
        .category('MongoDBSubnet').item('CIDR', '10.104.129.0/24')
    )

    vpc = Resource('VPC').type('AWS::EC2::VPC').properties([
        Attributes.of('CidrBlock', Intrinsics.find_in_map('GroupToCIDR', 'VPC', 'CIDR')),
        Attributes.of('InstanceTenancy', 'default')
    ])
    t.resources(vpc)

    igw = Resource('InternetGateway').type('AWS:EC2::InternetGateway')
    t.resources(igw)

    attach_igw = Resource('AttachInternetGateway').type('AWS::EC2::VPCGatewayAttachment').properties([
        Attributes.of('VpcId', vpc),
        Attributes.of('InternetGatewayId', igw)
    ])
    t.resources(attach_igw)

    t.resources(Resource('NatGatewayEIP').type('AWS::EC2::EIP').dependsOn(attach_igw).properties([
        Attributes.of('Domain', 'vpc')
    ]))

    nat_gw = Resource('NatGateway').type('AWS::EC2::NatGateway').properties([
        Attributes.of('AllocationId', Intrinsics.get_att('NatGatewayEIP', 'AllocationId'))
    ])
    t.resources(nat_gw)

    public_route_table = Resource('PublicRouteTable').type('AWS::EC2::RouteTable').dependsOn(attach_igw).properties([
        Attributes.of('VpcId', vpc)
    ])
    t.resources(public_route_table)

    private_route_table = Resource('PrivateRouteTable').type('AWS::EC2::RouteTable').dependsOn(attach_igw).properties([
        Attributes.of('VpcId', vpc)
    ])
    t.resources(private_route_table)

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

    api_server_subnet = Resource('ApiServerSubnet').type('AWS::EC2::Subnet').dependsOn(attach_igw).properties([
        Attributes.of('VpcId', vpc),
        Attributes.of('AvailabilityZone', Intrinsics.select('0', Intrinsics.get_azs())),
        Attributes.of('CidrBlock', Intrinsics.find_in_map('GroupToCIDR', 'ApiServerSubnet', 'CIDR')),
        Attributes.of('MapPublicIpOnLaunch', 'true')
    ])
    t.resources(api_server_subnet)
    nat_gw.property(Attributes.of('SubnetId', api_server_subnet))

    computing_server_subnet = Resource('ComputingServerSubnet').type('AWS::EC2::Subnet').dependsOn(attach_igw).properties([
        Attributes.of('VpcId', vpc),
        Attributes.of('AvailabilityZone', Intrinsics.select('0', Intrinsics.get_azs())),
        Attributes.of('CidrBlock', Intrinsics.find_in_map('GroupToCIDR', 'ComputingServerSubnet', 'CIDR')),
        Attributes.of('MapPublicIpOnLaunch', 'false')
    ])
    t.resources(computing_server_subnet)

    mongo_db_subnet = Resource('MongoDBSubnet').type('AWS::EC2::Subnet').dependsOn(attach_igw).properties([
        Attributes.of('VpcId', vpc),
        Attributes.of('AvailabilityZone', Intrinsics.select('0', Intrinsics.get_azs())),
        Attributes.of('CidrBlock', Intrinsics.find_in_map('GroupToCIDR', 'MongoDBSubnet', 'CIDR')),
        Attributes.of('MapPublicIpOnLaunch', 'false')
    ])
    t.resources(mongo_db_subnet)

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

    vpc_default_security_group = Resource('VPCDefaultSecurityGroup').type('AWS::EC2::SecurityGroup').properties([
        Attributes.of('VpcId', vpc),
        Attributes.of('GroupDescription', 'Allow all communications in VPC'),
        Attributes.of('SecurityGroupIngress', [ # TODO
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
