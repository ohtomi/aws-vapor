# -*- coding: utf-8 -*-

from collections import OrderedDict


class Template(object):

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


class Mapping(Element):

    def __init__(self, name):
        super(Mapping, self).__init__(name)


class Resource(Element):

    def __init__(self, name):
        super(Resource, self).__init__(name)

    def type(self, name):
        return self.attributes(ScalarAttribute('Type', name))

    def dependsOn(self, resource):
        return self.attributes(ReferenceAttribute('DependsOn', resource))

    def properties(self, props):
        return self.attribute('Properties', props)


class Output(Element):

    def __init__(self, name):
        super(Output, self).__init__(name)


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
    t.parameters(Element('KeyName')
        .attribute('Description', 'Name of an existing EC2 KeyPair to enable SSH access to the server')
        .attribute('Type', 'String')
    )
    t.parameters(Element('InstanceType')
        .attribute('Description', 'EC2 instance type')
        .attribute('Type', 'String')
        .attribute('Default', 't1.micro')
    )
    t.mappings(Element('RegionToAMI')
        .attribute('ap-northeast-1', [
            ScalarAttribute('AMI1', 'ami-a1bec3a0'),
            ScalarAttribute('AMI2', 'ami-a1bec3a1')
        ])
    )

    vpc = Resource('VPC').type('AWS::EC2::VPC').properties([
        ScalarAttribute('CidrBlock', '10.104.0.0/16'),
        ScalarAttribute('InstanceTenancy', 'default')
    ])
    t.resources(vpc)

    igw = Resource('InternetGateway').type('AWS:EC2::InternetGateway')
    t.resources(igw)

    attachIgw = Resource('AttachInternetGateway').type('AWS::EC2::VPCGatewayAttachment').properties([
        ReferenceAttribute('VpcId', vpc),
        ReferenceAttribute('InternetGatewayId', igw)
    ])
    t.resources(attachIgw)

    t.outputs(Element('VpcId')
        .attribute('Description', '-')
        .attribute('Value', vpc)
    )

    from json import dumps
    print(dumps(t.to_template(), indent=2, separators=(',', ': ')))
