# -*- coding: utf-8 -*-

from aws_vapor import utils
from collections import OrderedDict


class Template(object):

    def __init__(self, version='2010-09-09', description=''):
        self.version = version
        self.description = description
        self.elements = OrderedDict()

    def description(self, description):
        self.description = description

    def get_section(self, section_name):
        if section_name not in self.elements:
            self.elements[section_name] = []
        return self.elements[section_name]

    def index_of_section(self, section, element_name):
        if len([item for item in section if item.name == element_name]) >= 1:
            return [item.name for item in section].index(element_name)
        else:
            return -1

    def merge_or_replace_element(self, section_name, element, merge):
        section = self.get_section(section_name)
        index = self.index_of_section(section, element.name)

        if index == -1:
            section.append(element)
        elif merge:
            existing = section[index]
            for k, v in list(element.attrs.items()):
                existing.attrs[k] = v
        else:
            section[index] = element

        return element

    def parameters(self, element, merge=False):
        return self.merge_or_replace_element('Parameters', element, merge)

    def mappings(self, element, merge=False):
        return self.merge_or_replace_element('Mappings', element, merge)

    def conditions(self, element, merge=False):
        return self.merge_or_replace_element('Conditions', element, merge)

    def resources(self, element, merge=False):
        return self.merge_or_replace_element('Resources', element, merge)

    def outputs(self, element, merge=False):
        return self.merge_or_replace_element('Outputs', element, merge)

    def to_template(self):
        template = OrderedDict()
        template['AWSTemplateFormatVersion'] = self.version
        template['Description'] = self.description
        for section_name, entries in list(self.elements.items()):
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
        if category not in self.attrs:
            self.attributes(category, OrderedDict())
            return self

    def add_item(self, key, value):
        m = self.attrs[self._category]
        m[key] = value
        return self

    def find_in_map(self, top_level_key, second_level_key):
        if isinstance(top_level_key, str):
            if top_level_key not in self.attrs:
                raise ValueError('missing top_level_key. top_level_key: %r' % top_level_key)
            if isinstance(second_level_key, str):
                if second_level_key not in self.attrs[top_level_key]:
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

    def condition(self, condition):
        return self.attributes('Condition', condition)

    def metadata(self, metadata):
        return self.attributes('Metadata', metadata)

    def dependsOn(self, resource):
        if not hasattr(resource, 'name'):
            raise ValueError('missing name of resource. resource: %r' % resource)
        return self.attributes('DependsOn', resource.name)

    def properties(self, props):
        m = self.attrs['Properties'] if 'Properties' in self.attrs else OrderedDict()
        for p in props:
            for k, v in list(p.items()):
                m[k] = v
        return self.attributes('Properties', m)

    def add_property(self, prop):
        return self.properties([prop])


class Output(Element):

    def __init__(self, name):
        super(Output, self).__init__(name)

    def description(self, desc):
        return self.attributes('Description', desc)

    def condition(self, condition):
        return self.attributes('Condition', condition)

    def value(self, value):
        return self.attributes('Value', value)

    def export(self, name):
        return self.attributes('Export', {'Name': name})


class Attributes(object):

    @classmethod
    def of(cls, name, value):
        if isinstance(value, Element):
            return {name: Intrinsics.ref(value)}
        else:
            return {name: value}


class Intrinsics(object):

    @classmethod
    def base64(cls, value_to_encode):
        return {'Fn::Base64': value_to_encode}

    @classmethod
    def find_in_map(cls, map_name_or_mapping, top_level_key, second_level_key):
        if isinstance(map_name_or_mapping, str):
            map_name = map_name_or_mapping
            return {'Fn::FindInMap': [map_name, top_level_key, second_level_key]}
        elif isinstance(map_name_or_mapping, Mapping):
            mapping = map_name_or_mapping
            return {'Fn::FindInMap': [mapping.name, top_level_key, second_level_key]}
        else:
            raise ValueError('value should be map name or mapping. but %r' % type(map_name_or_mapping))

    @classmethod
    def fn_and(cls, conditions=list()):
        if 2 <= len(conditions) <= 10:
            return {'Fn::And': [condition.expression for condition in conditions]}
        else:
            raise ValueError('the minimum number of conditions is 2, and the maximum is 10. but %r' % len(conditions))

    @classmethod
    def fn_equals(cls, value_1, value_2):
        return {'Fn::Equals': [value_1, value_2]}

    @classmethod
    def fn_if(cls, condition_name, value_if_true, value_if_false):
        return {'Fn::If': [condition_name, value_if_true, value_if_false]}

    @classmethod
    def fn_not(cls, condition):
        return {'Fn::Not': [condition.expression]}

    @classmethod
    def fn_or(cls, conditions=list()):
        if 2 <= len(conditions) <= 10:
            return {'Fn::Or': [condition.expression for condition in conditions]}
        else:
            raise ValueError('the minimum number of conditions is 2, and the maximum is 10. but %r' % len(conditions))

    @classmethod
    def get_att(cls, logical_name_of_resource, attribute_name):
        return {'Fn::GetAtt': [logical_name_of_resource, attribute_name]}

    @classmethod
    def get_azs(cls, region=''):
        return {'Fn::GetAZs': region}

    @classmethod
    def import_value(cls, value_to_import):
        return {'Fn::ImportValue': value_to_import}

    @classmethod
    def join(cls, delimiter, list_of_values):
        return {'Fn::Join': [delimiter, list_of_values]}

    @classmethod
    def select(cls, index, list_of_objects):
        return {'Fn::Select': [index, list_of_objects]}

    @classmethod
    def sub(cls, template, dict_of_parameters=None):
        if dict_of_parameters is None:
            return {'Fn::Sub': template}
        else:
            return {'Fn::Sub': [template, dict_of_parameters]}

    @classmethod
    def ref(cls, logical_name_or_element):
        if isinstance(logical_name_or_element, str):
            logical_name = logical_name_or_element
            return {'Ref': logical_name}
        elif isinstance(logical_name_or_element, Element):
            resource = logical_name_or_element
            return {'Ref': resource.name}
        else:
            raise ValueError('value should be logical name or resource. but %r' % type(logical_name_or_element))


class Pseudos(object):

    @classmethod
    def account_id(cls):
        return {'Ref': 'AWS::AccountId'}

    @classmethod
    def notification_arns(cls):
        return {'Ref': 'AWS::NotificationARNs'}

    @classmethod
    def no_value(cls):
        return {'Ref': 'AWS::NoValue'}

    @classmethod
    def region(cls):
        return {'Ref': 'AWS::Region'}

    @classmethod
    def stack_id(cls):
        return {'Ref': 'AWS::StackId'}

    @classmethod
    def stack_name(cls):
        return {'Ref': 'AWS::StackName'}


class UserData(object):

    @classmethod
    def of(cls, values):
        return {'UserData': Intrinsics.base64(Intrinsics.join('', values))}

    @classmethod
    def from_files(cls, files, params):
        user_data = utils.inject_params(utils.combine_user_data(files), params)
        return {'UserData': Intrinsics.base64(Intrinsics.join('', user_data))}


class CfnInitMetadata(object):

    @classmethod
    def of(cls, config_or_config_sets):
        m = OrderedDict()
        if isinstance(config_or_config_sets, CfnInitMetadata.Config):
            config = config_or_config_sets
            m[config.name] = config.value
        else:
            config_sets = config_or_config_sets
            cs = m['configSets'] = OrderedDict()
            for config_set in config_sets:
                cs[config_set.name] = [config.name for config in config_set.configs]
                for config in config_set.configs:
                    m[config.name] = config.value
        return {'AWS::CloudFormation::Init': m}

    class ConfigSet(object):

        def __init__(self, name, configs):
            self.name = name
            self.configs = configs

    class Config(object):

        def __init__(self, name):
            self.name = name
            self.value = OrderedDict()

        def _create_and_get_map(self, keys):
            m = self.value
            for key in keys:
                if key not in m:
                    m[key] = OrderedDict()
                m = m[key]
            return m

        def commands(self, key, command, env=None, cwd=None, test=None, ignore_errors=None, wait_after_completion=None):
            m = OrderedDict()
            m['command'] = command
            if env is not None:
                m['env'] = env
            if cwd is not None:
                m['cwd'] = cwd
            if test is not None:
                m['test'] = test
            if ignore_errors is not None:
                m['ignoreErrors'] = ignore_errors
            if wait_after_completion is not None:
                m['waitAfterCompletion'] = wait_after_completion

            v = self._create_and_get_map(['commands'])
            v[key] = m
            return self

        def files(self, key, content=None, source=None, encoding=None, group=None, owner=None, mode=None, authentication=None, context=None):
            m = OrderedDict()
            if content is not None:
                m['content'] = content
            if source is not None:
                m['source'] = source
            if encoding is not None:
                m['encoding'] = encoding
            if group is not None:
                m['group'] = group
            if owner is not None:
                m['owner'] = owner
            if mode is not None:
                m['mode'] = mode
            if authentication is not None:
                m['authentication'] = authentication
            if context is not None:
                m['context'] = context

            v = self._create_and_get_map(['files'])
            v[key] = m
            return self

        def groups(self, key, gid=None):
            m = OrderedDict()
            if gid is not None:
                m['gid'] = str(gid)

            v = self._create_and_get_map(['groups'])
            v[key] = m
            return self

        def packages(self, package_manager, key, versions=[]):
            v = self._create_and_get_map(['packages', package_manager])
            v[key] = versions
            return self

        def services(self, service_manager, key, ensure_running=None, enabled=None, files=None, sources=None, packages=None, commands=None):
            m = OrderedDict()
            if ensure_running is not None:
                m['ensureRunning'] = 'true' if ensure_running else 'false'
            if enabled is not None:
                m['enabled'] = 'true' if enabled else 'false'
            if files is not None:
                m['files'] = files
            if sources is not None:
                m['sources'] = sources
            if packages is not None:
                m['packages'] = packages
            if commands is not None:
                m['commands'] = commands

            v = self._create_and_get_map(['services', service_manager])
            v[key] = m
            return self

        def sources(self, key, url):
            v = self._create_and_get_map(['sources'])
            v[key] = url
            return self

        def users(self, key, uid, groups, home_dir):
            m = OrderedDict()
            m['groups'] = groups
            m['uid'] =  str(uid)
            m['homeDir'] = home_dir

            v = self._create_and_get_map(['users'])
            v[key] = m
            return self

    @classmethod
    def from_file(cls, filename, params={}):
        with open(filename) as fh:
            c = fh.read()
        content = utils.inject_params(c, params)
        joined_content = Intrinsics.join('', content)
        return joined_content
