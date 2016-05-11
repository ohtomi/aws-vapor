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
        self.attrs = []

    def attributes(self, attr):
        self.attrs.append(attr)
        return self

    def attribute(self, name, value):
        if isinstance(value, str):
            return self.attributes(ScalarAttribute(name, value))
        elif isinstance(value, Element):
            return self.attributes(ReferenceAttribute(name, value))
        elif isinstance(value, list):
            return self.attributes(ListAttribute(name, value))
        else:
            raise ValueError('TODO')

    def to_template(self, template):
        element = template[self.name] = OrderedDict()
        for attr in self.attrs:
            attr.to_template(element)


class Parameter(Element):

    def __init__(self, name):
        super(Parameter, self).__init__(name)

    def description(self, desc):
        return self.attribute('Description', desc)

    def type(self, name):
        return self.attribute('Type', name)


class Mapping(Element):

    def __init__(self, name):
        super(Mapping, self).__init__(name)


class Resource(Element):

    def __init__(self, name):
        super(Resource, self).__init__(name)

    def type(self, name):
        return self.attribute('Type', name)

    def dependsOn(self, resource):
        return self.attribute('DependsOn', resource.name)

    def properties(self, props):
        return self.attribute('Properties', props)

    def property(self, prop):
        for attr in self.attrs:
            if attr.name == 'Properties':
                attr.values.append(prop)
                return self
        return self.properties([prop])


class Output(Element):

    def __init__(self, name):
        super(Output, self).__init__(name)

    def description(self, desc):
        return self.attribute('Description', desc)

    def value(self, value):
        return self.attribute('Value', value)


class Attribute(object):

    def __init__(self, name):
        self.name = name

    def to_template(self, template):
        raise NotImplementedError('override me')


class ScalarAttribute(Attribute):

    def __init__(self, name, value):
        super(ScalarAttribute, self).__init__(name)
        self.value = value

    def to_template(self, template):
        template[self.name] = self.value


class ListAttribute(Attribute):

    def __init__(self, name, values):
        super(ListAttribute, self).__init__(name)
        self.values = values

    def to_template(self, template):
        attr = template[self.name] = OrderedDict()
        for item in self.values:
            if isinstance(item, dict):
                for k, v in item.iteritems():
                    attr[k] = v
            elif hasattr(item, 'to_template'):
                item.to_template(attr)
            else:
                raise ValueError('TODO')


class ReferenceAttribute(Attribute):

    def __init__(self, name, element):
        super(ReferenceAttribute, self).__init__(name)
        self.element = element

    def to_template(self, template):
        template[self.name] = {'Ref': self.element.name}


if __name__ == '__main__':
    t = Template(description='Sample Template')

    t.parameters(Parameter('KeyName')
        .description('Name of an existing EC2 KeyPair to enable SSH access to the server')
        .type('String')
    )

    t.mappings(Mapping('GroupToCIDR')
        .attribute('VPC', [
            ScalarAttribute('CIDR', '10.104.0.0/16'),
        ])
        .attribute('ApiServerSubnet', [
            ScalarAttribute('CIDR', '10.104.128.0/24'),
        ])
        .attribute('ComputingServerSubnet', [
            ScalarAttribute('CIDR', '10.104.144.0/20'),
        ])
        .attribute('MongoDBSubnet', [
            ScalarAttribute('CIDR', '10.104.129.0/24')
        ])
    )

    vpc = Resource('VPC').type('AWS::EC2::VPC').properties([
        ScalarAttribute('CidrBlock', {'Fn::FindInMap': ['GroupToCIDR', 'VPC', 'CIDR']}), # TODO
        ScalarAttribute('InstanceTenancy', 'default')
    ])
    t.resources(vpc)

    igw = Resource('InternetGateway').type('AWS:EC2::InternetGateway')
    t.resources(igw)

    attach_igw = Resource('AttachInternetGateway').type('AWS::EC2::VPCGatewayAttachment').properties([
        ReferenceAttribute('VpcId', vpc),
        ReferenceAttribute('InternetGatewayId', igw)
    ])
    t.resources(attach_igw)

    t.resources(Resource('NatGatewayEIP').type('AWS::EC2::EIP').dependsOn(attach_igw).properties([
        ScalarAttribute('Domain', 'vpc')
    ]))

    nat_gw = Resource('NatGateway').type('AWS::EC2::NatGateway').properties([
        ScalarAttribute('AllocationId', {'Fn::GetAtt': ['NatGatewayEIP', 'AllocationId']}) # TODO
    ])
    t.resources(nat_gw)

    public_route_table = Resource('PublicRouteTable').type('AWS::EC2::RouteTable').dependsOn(attach_igw).properties([
        ReferenceAttribute('VpcId', vpc)
    ])
    t.resources(public_route_table)

    private_route_table = Resource('PrivateRouteTable').type('AWS::EC2::RouteTable').dependsOn(attach_igw).properties([
        ReferenceAttribute('VpcId', vpc)
    ])
    t.resources(private_route_table)

    t.resources(Resource('PublicRoute').type('AWS::EC2::Route').dependsOn(attach_igw).properties([
        ReferenceAttribute('RouteTableId', public_route_table),
        ScalarAttribute('DestinationCidrBlock', '0.0.0.0/0'),
        ReferenceAttribute('GatewayId', igw)
    ]))

    t.resources(Resource('PrivateRoute').type('AWS::EC2::Route').dependsOn(attach_igw).properties([
        ReferenceAttribute('RouteTableId', private_route_table),
        ScalarAttribute('DestinationCidrBlock', '0.0.0.0/0'),
        ReferenceAttribute('GatewayId', nat_gw)
    ]))

    api_server_subnet = Resource('ApiServerSubnet').type('AWS::EC2::Subnet').dependsOn(attach_igw).properties([
        ReferenceAttribute('VpcId', vpc),
        ScalarAttribute('AvailabilityZone', {'Fn::Select': ['0', {'Fn::GetAZs': {'Ref': 'AWS::Region'}}]}), # TODO
        ScalarAttribute('CidrBlock', {'Fn::FindInMap': ['GroupToCIDR', 'ApiServerSubnet', 'CIDR']}), # TODO
        ScalarAttribute('MapPublicIpOnLaunch', 'true')
    ])
    t.resources(api_server_subnet)
    nat_gw.property(ReferenceAttribute('SubnetId', api_server_subnet))

    computing_server_subnet = Resource('ComputingServerSubnet').type('AWS::EC2::Subnet').dependsOn(attach_igw).properties([
        ReferenceAttribute('VpcId', vpc),
        ScalarAttribute('AvailabilityZone', {'Fn::Select': ['0', {'Fn::GetAZs': {'Ref': 'AWS::Region'}}]}), # TODO
        ScalarAttribute('CidrBlock', {'Fn::FindInMap': ['GroupToCIDR', 'ComputingServerSubnet', 'CIDR']}), # TODO
        ScalarAttribute('MapPublicIpOnLaunch', 'false')
    ])
    t.resources(computing_server_subnet)

    mongo_db_subnet = Resource('MongoDBSubnet').type('AWS::EC2::Subnet').dependsOn(attach_igw).properties([
        ReferenceAttribute('VpcId', vpc),
        ScalarAttribute('AvailabilityZone', {'Fn::Select': ['0', {'Fn::GetAZs': {'Ref': 'AWS::Region'}}]}), # TODO
        ScalarAttribute('CidrBlock', {'Fn::FindInMap': ['GroupToCIDR', 'MongoDBSubnet', 'CIDR']}), # TODO
        ScalarAttribute('MapPublicIpOnLaunch', 'false')
    ])
    t.resources(mongo_db_subnet)

    t.resources(Resource('ApiServerSubnetRouteTableAssociation').type('AWS::EC2::SubnetRouteTableAssociation').properties([
        ReferenceAttribute('SubnetId', api_server_subnet),
        ReferenceAttribute('RouteTableId', public_route_table)
    ]))

    t.resources(Resource('ComputingServerSubnetRouteTableAssociation').type('AWS::EC2::SubnetRouteTableAssociation').properties([
        ReferenceAttribute('SubnetId', computing_server_subnet),
        ReferenceAttribute('RouteTableId', private_route_table)
    ]))

    t.resources(Resource('MongoDBSubnetRouteTableAssociation').type('AWS::EC2::SubnetRouteTableAssociation').properties([
        ReferenceAttribute('SubnetId', mongo_db_subnet),
        ReferenceAttribute('RouteTableId', private_route_table)
    ]))

    vpc_default_security_group = Resource('VPCDefaultSecurityGroup').type('AWS::EC2::SecurityGroup').properties([
        ReferenceAttribute('VpcId', vpc),
        ScalarAttribute('GroupDescription', 'Allow all communications in VPC'),
        ScalarAttribute('SecurityGroupIngress', [ # TODO
            {'IpProtocol': 'tcp', 'FromPort': '0', 'ToPort': '65535', 'CidrIp': {'Fn::FindInMap': ['GroupToCIDR', 'VPC', 'CIDR']}},
            {'IpProtocol': 'udp', 'FromPort': '0', 'ToPort': '65535', 'CidrIp': {'Fn::FindInMap': ['GroupToCIDR', 'VPC', 'CIDR']}},
            {'IpProtocol': 'icmp', 'FromPort': '-1', 'ToPort': '-1', 'CidrIp': {'Fn::FindInMap': ['GroupToCIDR', 'VPC', 'CIDR']}}
        ])
    ])
    t.resources(vpc_default_security_group)

    t.outputs(Output('VpcId').description('-').value(vpc))
    t.outputs(Output('ApiServerSubnet').description('-').value(api_server_subnet))
    t.outputs(Output('ComputingServerSubnet').description('-').value(computing_server_subnet))
    t.outputs(Output('MongoDBSubnet').description('-').value(mongo_db_subnet))
    t.outputs(Output('VPCDefaultSecurityGroup').description('-').value(vpc_default_security_group))

    from json import dumps
    print(dumps(t.to_template(), indent=2, separators=(',', ': ')))
