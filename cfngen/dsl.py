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

    def attribute(self, attr):
        self.attrs.append(attr)
        return self

    def attribute_scalar(self, name, value):
        return self.attribute(ScalarAttribute(name, value))

    def attribute_list(self, name, values):
        return self.attribute(ListAttribute(name, values))

    def attribute_reference(self, name, element):
        return self.attribute(ReferenceAttribute(name, element))

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
        self.attribute(ScalarAttribute('Type', name))
        return self

    def dependsOn(self, resource):
        self.attribute(ReferenceAttribute('DependsOn', resource))
        return self


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
                pass # TODO


class ReferenceAttribute(Attribute):

    def __init__(self, name, element):
        super(ReferenceAttribute, self).__init__(name)
        self.element = element

    def to_template(self, template):
        template[self.name] = {'Ref': self.element.name}


if __name__ == '__main__':
    t = Template(description='Sample Template')
    t.parameters(Element('KeyName')
        .attribute_scalar('Description', 'Name of an existing EC2 KeyPair to enable SSH access to the server')
        .attribute_scalar('Type', 'String')
    )
    t.parameters(Element('InstanceType')
        .attribute_scalar('Description', 'EC2 instance type')
        .attribute_scalar('Type', 'String')
        .attribute_scalar('Default', 't1.micro')
    )
    t.mappings(Element('RegionToAMI')
        .attribute_list('ap-northeast-1', [
            ScalarAttribute('AMI1', 'ami-a1bec3a0'),
            ScalarAttribute('AMI2', 'ami-a1bec3a1')
        ])
    )

    vpc = Resource('VPC').type('AWS::EC2::VPC').attribute_list('Properties', [
        ScalarAttribute('CidrBlock', '10.104.0.0/16'),
        ScalarAttribute('InstanceTenancy', 'default')
    ])
    t.resources(vpc)

    igw = Resource('InternetGateway').type('AWS:EC2::InternetGateway')
    t.resources(igw)

    attachIgw = Resource('AttachInternetGateway').type('AWS::EC2::VPCGatewayAttachment').attribute_list('Properties', [
        ReferenceAttribute('VpcId', vpc),
        ReferenceAttribute('InternetGatewayId', igw)
    ])
    t.resources(attachIgw)

    t.outputs(Element('VpcId')
        .attribute_scalar('Description', '-')
        .attribute_reference('Value', vpc)
    )

    from json import dumps
    print(dumps(t.to_template(), indent=2, separators=(',', ': ')))
