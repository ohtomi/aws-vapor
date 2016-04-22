# -*- coding: utf-8 -*-


class Template(object):

    def __init__(self, version='2010-09-09', description=''):
        self.version = version
        self.description = description
        self.elements = {}

    def __getattr(self, name):
        pass

    def get_section(self, section_name):
        if not self.elements.has_key(section_name):
            self.elements[section_name] = []
        return self.elements[section_name]

    def add_parameter(self, element):
        section = self.get_section('Parameters')
        section.append(element)
        return self

    def add_mappings(self, element):
        section = self.get_section('Mappings')
        section.append(element)
        return self

    def add_resources(self, element):
        section = self.get_section('Resources')
        section.append(element)
        return self

    def add_outputs(self, element):
        section = self.get_section('Outputs')
        section.append(element)
        return self

    def to_template(self):
        template = {}
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
        self.props = []

    def add_property(self, name, value):
        self.props.append((name, value))
        return self

    def to_template(self, template):
        element = template[self.name] = {}
        for name, value in self.props:
            element[name] = value


if __name__ == '__main__':
    t = Template(description='Sample Template')
    t.add_parameter(
        Element('KeyName')
            .add_property('Description', 'Name of an existing EC2 KeyPair to enable SSH access to the bastion server')
            .add_property('Type', 'String'))
    t.add_parameter(
        Element('InstanceType')
            .add_property('Description', 'EC2 instance type')
            .add_property('Type', 'String')
            .add_property('Default', 't1.micro'))

    from pprint import PrettyPrinter
    PrettyPrinter(indent=2).pprint(t.to_template())
