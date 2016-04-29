# -*- coding: utf-8 -*-

from collections import OrderedDict


class Root(object):

    def __init__(self, version='2010-09-09', description=''):
        self.version = version
        self.description = description
        self.elements = OrderedDict()

    def __getattr(self, name):
        pass

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
            section = template[section_name] = {}
            for element in entries:
                element.to_template(section)

        return template


class Element(object):

    def __init__(self, name):
        self.name = name
        self.attrs = []

    def attribute(self, attr):
        self.attrs.append(attr)
        return self

    def to_template(self, template):
        element = template[self.name] = {}
        for attr in self.attrs:
            attr.to_template(element)


class Parameter(Element):

    def __init__(self, name):
        super(Parameter, self).__init__(name)


class Mapping(Element):

    def __init__(self, name):
        super(Mapping, self).__init__(name)


class Resource(Element):

    def __init__(self, name):
        super(Resource, self).__init__(name)

    def type(self, name):
        self.attribute(Attribute.scalar('Type', name))

    def dependsOn(self, resource):
        self.attribute(Attribute.reference('DependsOn', resource))


class Output(Element):

    def __init__(self, name):
        super(Output, self).__init__(name)


class Attribute(object):

    def __init__(self, name, to_template):
        self.name = name
        self.to_template = to_template

    def to_template(self, template):
        self.to_template(template)

    @staticmethod
    def scalar(name, value):
        def to_template(template):
            template[name] = value
        return Attribute(name, to_template)

    @staticmethod
    def list(name, value):
        def to_template(template):
            attr = template[name] = {}
            for item in value:
                if isinstance(item, dict):
                    for k, v in item.iteritems():
                        attr[k] = v
                elif hasattr(item, 'to_template'):
                    item.to_template(attr)
                else:
                    pass # TODO
        return Attribute(name, to_template)

    @staticmethod
    def reference(name, element):
        def to_template(template):
            template[name] = {'Ref': element.name}
        return Attribute(name, to_template)


if __name__ == '__main__':
    t = Root(description='Sample Template')
    t.parameters(
        Element('KeyName')
            .attribute(Attribute.scalar('Description', 'Name of an existing EC2 KeyPair to enable SSH access to the server'))
            .attribute(Attribute.scalar('Type', 'String'))
    )
    t.parameters(
        Element('InstanceType')
            .attribute(Attribute.scalar('Description', 'EC2 instance type'))
            .attribute(Attribute.scalar('Type', 'String'))
            .attribute(Attribute.scalar('Default', 't1.micro'))
    )
    t.mappings(
        Element('RegionToAMI')
            .attribute(Attribute.scalar('ap-northeast-1', {'AMI': 'ami-a1bec3a0'}))
    )

    vpc = Resource('VPC')
    vpc.type('AWS::EC2::VPC')
    vpc.attribute(Attribute.list('Properties', [
        {'CidrBlock': '10.104.0.0/16'},
        {'InstanceTenancy': 'default'}
    ]))
    t.resources(vpc)

    igw = Resource('InternetGateway')
    igw.type('AWS:EC2::InternetGateway')
    t.resources(igw)

    attachIgw = Resource('AttachInternetGateway')
    attachIgw.type('AWS::EC2::VPCGatewayAttachment')
    attachIgw.attribute(Attribute.list('Properties', [
        Attribute.reference('VpcId', vpc),
        Attribute.reference('InternetGatewayId', igw)
    ]))
    t.resources(attachIgw)

    t.outputs(
        Element('VpcId')
            .attribute(Attribute.scalar('Description', '-'))
            .attribute(Attribute.reference('Value', vpc))
    )

    from json import dumps
    print(dumps(t.to_template(), indent=2, separators=(',', ': ')))
