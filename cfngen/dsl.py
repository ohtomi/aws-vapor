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
            self.elements[section_name] = {}
        return self.elements[section_name]

    def add_parameter(self, name, value):
        section = self.get_section('Parameters')
        section[name] = value

    def add_mappings(self, name, value):
        section = self.get_section('Mappings')
        section[name] = value

    def add_resources(self, name, value):
        section = self.get_section('Resources')
        section[name] = value

    def add_outputs(self, name, value):
        section = self.get_section('Outputs')
        section[name] = value

    def to_template(self):
        template = {}
        template['AWSTemplateFormatVersion'] = self.version
        template['Description'] = self.description
        for section_name, entries in self.elements.items():
            section = template[section_name] = {}
            for name, value in entries.items():
                # TODO
                section[name] = value

        return template


if __name__ == '__main__':
    t = Template(description='Sample Template')
    t.add_parameter('KeyName', {
            'Description': 'Name of an existing EC2 KeyPair to enable SSH access to the bastion server',
            'Type': 'String'})
    t.add_parameter('InstanceType', {
            'Description': 'EC2 instance type',
            'Type': 'String',
            'Default': 't1.micro'})

    from pprint import PrettyPrinter
    PrettyPrinter(indent=2).pprint(t.to_template())
