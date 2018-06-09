# -*- coding: utf-8 -*-

from typing import Any, Dict, List, Union

from aws_vapor import utils
from collections import OrderedDict

RegexPattern = str
MapNameOrMapping = Union[str, 'Mapping']
IntrinsicFunction = Dict[str, Any]


class Template(object):
    """An AWS CloudFormation template builder."""

    def __init__(self, version: str = '2010-09-09', description: str = ''):
        self.version = version
        self.description = description
        self.elements = OrderedDict()

    def description(self, description: str) -> 'Template':
        self.description = description
        return self

    def _get_section(self, section_name: str) -> List['Element']:
        if section_name not in self.elements:
            self.elements[section_name] = []
        return self.elements[section_name]

    def _merge_or_replace_element(self, section_name: str, element: 'Element', merge: bool) -> 'Element':
        def index_of_section(s: List['Element'], n: str) -> int:
            if len([item for item in s if item.name == n]) >= 1:
                return [item.name for item in s].index(n)
            else:
                return -1

        section = self._get_section(section_name)
        index = index_of_section(section, element.name)

        if index == -1:
            section.append(element)
        elif merge:
            existing = section[index]
            for k, v in list(element.attrs.items()):
                existing.attrs[k] = v
        else:
            section[index] = element

        return element

    def metadata(self, element: 'Element', merge: bool = False) -> 'Element':
        return self._merge_or_replace_element('Metadata', element, merge)

    def parameters(self, element: 'Element', merge: bool = False) -> 'Element':
        return self._merge_or_replace_element('Parameters', element, merge)

    def mappings(self, element: 'Element', merge: bool = False) -> 'Element':
        return self._merge_or_replace_element('Mappings', element, merge)

    def conditions(self, element: 'Element', merge: bool = False) -> 'Element':
        return self._merge_or_replace_element('Conditions', element, merge)

    def resources(self, element: 'Element', merge: bool = False) -> 'Element':
        return self._merge_or_replace_element('Resources', element, merge)

    def outputs(self, element: 'Element', merge: bool = False) -> 'Element':
        return self._merge_or_replace_element('Outputs', element, merge)

    def to_template(self) -> OrderedDict:
        template = OrderedDict()
        template['AWSTemplateFormatVersion'] = self.version
        template['Description'] = self.description
        for section_name, entries in list(self.elements.items()):
            section = template[section_name] = OrderedDict()
            for element in entries:
                element.to_template(section)

        return template


class Element(object):
    """This is an abstract base class of a template section."""

    def __init__(self, name: str):
        self.name = name
        self.attrs = OrderedDict()

    def attributes(self, name: str, value: Any):
        """Map `name` to `value` and return `self`."""
        self.attrs[name] = value
        return self

    def to_template(self, template: OrderedDict):
        """Convert mapped key-value pairs into a top level section of an AWS CloudFormation template.

        Args:
            template: A template builder.

        Returns:
            Passed a mapping object.
        """
        template[self.name] = self.attrs


class Metadatum(Element):
    """The `Metadatum` class is a subclass of :class:`Element`,
    each instance of which represents details about the template.
    """

    def __init__(self, name: str):
        super(Metadatum, self).__init__(name)


class Parameter(Element):
    """The `Parameter` class is a subclass of :class:`Element`,
    each instance of which passes values into your template when you create a stack.
    """

    def __init__(self, name: str):
        super(Parameter, self).__init__(name)

    def description(self, desc: str) -> 'Parameter':
        """Set 'Description' to `desc` and return `self`."""
        return self.attributes('Description', desc)

    def constraint_description(self, desc: str) -> 'Parameter':
        """Set 'ConstraintDescription' to `desc` and return `self`."""
        return self.attributes('ConstraintDescription', desc)

    def type(self, name: str) -> 'Parameter':
        """Set 'Type' to `name` and return `self`."""
        return self.attributes('Type', name)

    def default(self, value: Any) -> 'Parameter':
        """Set 'Default' to `value` and return `self`."""
        return self.attributes('Default', value)

    def allowed_values(self, list_of_values: List[Any]) -> 'Parameter':
        """Set 'AllowedValues' to `list_of_values` and return `self`."""
        return self.attributes('AllowedValues', list_of_values)

    def no_echo(self) -> 'Parameter':
        """Set 'NoEcho' to `true` and return `self`."""
        return self.attributes('NoEcho', 'true')

    def allowed_pattern(self, pattern: RegexPattern) -> 'Parameter':
        """Set 'AllowedPattern' to `pattern` and return `self`."""
        return self.attributes('AllowedPattern', pattern)

    def max_length(self, length: int) -> 'Parameter':
        """Set 'MaxLength' to `length` and return `self`."""
        return self.attributes('MaxLength', str(length))

    def min_length(self, length: int) -> 'Parameter':
        """Set `MinLength` to `length` and return `self`."""
        return self.attributes('MinLength', str(length))

    def max_value(self, value: int) -> 'Parameter':
        """Set `MaxValue` to `value` and return `self`."""
        return self.attributes('MaxValue', str(value))

    def min_value(self, value: int) -> 'Parameter':
        """Set `MinValue` to `value` and return `self`."""
        return self.attributes('MinValue', str(value))


class Mapping(Element):
    """The `Mapping` class is a subclass of :class:`Element`,
    each instance of which matches a key to a corresponding set of named values.
    """

    def __init__(self, name: str):
        super(Mapping, self).__init__(name)
        self._category = None

    def add_category(self, category: str) -> 'Mapping':
        """Create a new top level section of 'Mappings' and return `self`.

        Create a new top level section of 'Mappings' if doesn't contain `category`,
        then set a current selection to `category`.

        Args:
            category: A name of a top level section.

        Returns:
            `self`.
        """
        self._category = category
        if category not in self.attrs:
            self.attributes(category, OrderedDict())
            return self
        return self

    def add_item(self, key: str, value: Any) -> 'Mapping':
        """Map `key` to `value` in a current selection and return `self`."""
        m = self.attrs[self._category]
        m[key] = value
        return self

    def find_in_map(self, top_level_key: MapNameOrMapping, second_level_key: MapNameOrMapping) -> IntrinsicFunction:
        """Call `Intrinsics.find_in_map` and return its return value."""
        if isinstance(top_level_key, str):
            if top_level_key not in self.attrs:
                raise ValueError('missing top_level_key. top_level_key: %r' % top_level_key)
            if isinstance(second_level_key, str):
                if second_level_key not in self.attrs[top_level_key]:
                    raise ValueError('missing second_level_key. second_level_key: %r' % second_level_key)

        return Intrinsics.find_in_map(self, top_level_key, second_level_key)


class Condition(Element):
    """The `Condition` class is a subclass of :class:`Element`,
    each instance of which includes statements that define when a resource is created or when a property is defined.
    """

    def __init__(self, name: str):
        super(Condition, self).__init__(name)
        self.expr = None

    def expression(self, expression: IntrinsicFunction) -> 'Condition':
        """Set `expression` and return `self`."""
        self.expr = expression
        return self

    def to_template(self, template: OrderedDict):
        """Convert `self.attrs` into a top level section of an AWS CloudFormation template.

        Args:
            template: A template builder.

        Returns:
            Passed a mapping object.
        """
        template[self.name] = self.expr


class Resource(Element):
    """The `Resource` class is a subclass of :class:`Element`,
    each instance of which declares the AWS resources that you want to include in the stack,
    such as an Amazon EC2 instance or an Amazon S3 bucket.
    """

    def __init__(self, name: str):
        super(Resource, self).__init__(name)

    def type(self, name: str) -> 'Resource':
        """Set 'Type' to `name` and return `self`."""
        return self.attributes('Type', name)

    def condition(self, condition: 'Condition') -> 'Resource':
        """Set 'Condition' to `condition` and return `self`."""
        return self.attributes('Condition', condition.name)

    def metadata(self, metadata: Any) -> 'Resource':
        """Set 'Metadata' to `metadata` and return `self`."""
        return self.attributes('Metadata', metadata)

    def depends_on(self, resource: 'Resource') -> 'Resource':
        """Set 'DependsOn' to a name of `resource` and return `self`."""
        if not hasattr(resource, 'name'):
            raise ValueError('missing name of resource. resource: %r' % resource)
        return self.attributes('DependsOn', resource.name)

    def properties(self, props: List[Dict[str, Any]]) -> 'Resource':
        """Add a :class:`list` of a new key-value pair to 'Properties' and return `self`.

        Args:
            props: A :class:`list` of a key-value pair.

        Returns:
            `self`.
        """
        m = self.attrs['Properties'] if 'Properties' in self.attrs else OrderedDict()
        for p in props:
            for k, v in list(p.items()):
                m[k] = v
        return self.attributes('Properties', m)

    def add_property(self, prop: Dict[str, Any]) -> 'Resource':
        """Add a new key-value pair to 'Properties' and return `self`."""
        return self.properties([prop])


class Output(Element):
    """The `Output` class is a subclass of :class:`Element`,
    each instance of which declares output values that you can import into other stacks (to create cross-stack
    references), return in response (to describe stack calls), or view on the AWS CloudFormation console.
    """

    def __init__(self, name: str):
        super(Output, self).__init__(name)

    def description(self, desc: str) -> 'Output':
        return self.attributes('Description', desc)

    def condition(self, condition: 'Condition') -> 'Output':
        return self.attributes('Condition', condition.name)

    def value(self, value: str) -> 'Output':
        return self.attributes('Value', value)

    def export(self, name: str) -> 'Output':
        return self.attributes('Export', {'Name': name})


class Attributes(object):
    @classmethod
    def of(cls, name: str, value: Any) -> Dict[str, Any]:
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
    def fn_and(cls, conditions=None):
        if conditions is None:
            conditions = []
        if 2 <= len(conditions) <= 10:
            return {'Fn::And': [condition.expr for condition in conditions]}
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
        return {'Fn::Not': [condition.expr]}

    @classmethod
    def fn_or(cls, conditions=None):
        if conditions is None:
            conditions = []
        if 2 <= len(conditions) <= 10:
            return {'Fn::Or': [condition.expr for condition in conditions]}
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
    def of(cls, list_of_metadata):
        m = OrderedDict()
        for metadata in list_of_metadata:
            if isinstance(metadata, CfnInitMetadata.Init):
                im = m['AWS::CloudFormation::Init'] = OrderedDict()
                for config_or_config_set in metadata.config_or_config_sets:
                    if isinstance(config_or_config_set, CfnInitMetadata.Config):
                        config = config_or_config_set
                        im[config.name] = config.value
                    elif isinstance(config_or_config_set, CfnInitMetadata.ConfigSet):
                        config_set = config_or_config_set
                        if 'configSets' not in im:
                            csm = im['configSets'] = OrderedDict()
                        else:
                            csm = im['configSets']
                        csm[config_set.name] = [config.name for config in config_set.configs]
                        for config in config_set.configs:
                            im[config.name] = config.value
                    else:
                        raise ValueError('unknown config. config: %r' % metadata.config_or_config_sets)
            elif isinstance(metadata, CfnInitMetadata.Authentication):
                am = m['AWS::CloudFormation::Authentication'] = OrderedDict()
                am[metadata.name] = metadata.value
            else:
                raise ValueError('unknown metadata. metadata: %r' % metadata)
        return m

    class Init(object):

        def __init__(self, config_or_config_sets):
            self.config_or_config_sets = config_or_config_sets

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

        def files(self, key, content=None, source=None, local_file_path=None, encoding=None, group=None, owner=None,
                  mode=None, authentication=None, context=None, local_file_params=None):
            if local_file_params is None:
                local_file_params = {}
            m = OrderedDict()
            if content is not None:
                m['content'] = content
            if source is not None:
                m['source'] = source
            if local_file_path is not None:
                with open(local_file_path) as fh:
                    c = fh.read()
                init_file_content = utils.inject_params(c, local_file_params)
                m['content'] = Intrinsics.join('', init_file_content)
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

        def packages(self, package_manager, key, versions=None):
            if versions is None:
                versions = []
            v = self._create_and_get_map(['packages', package_manager])
            v[key] = versions
            return self

        def services(self, service_manager, key, ensure_running=None, enabled=None, files=None, sources=None,
                     packages=None, commands=None):
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
            m['uid'] = str(uid)
            m['homeDir'] = home_dir

            v = self._create_and_get_map(['users'])
            v[key] = m
            return self

    class Authentication(object):

        def __init__(self, name, authentication_type):
            self.name = name
            self.type = authentication_type

            if authentication_type != 'basic' and authentication_type != 'S3':
                raise ValueError('unknown authentication type. type: %r' % authentication_type)
            self.value = OrderedDict({'type': authentication_type})

        def access_key_id(self, value):
            if self.type != 'S3':
                raise ValueError('illegal authentication type. type: %r' % self.type)
            self.value['accessKeyId'] = value
            return self

        def buckets(self, list_of_values):
            if self.type != 'S3':
                raise ValueError('illegal authentication type. type: %r' % self.type)
            self.value['buckets'] = list_of_values
            return self

        def password(self, value):
            if self.type != 'basic':
                raise ValueError('illegal authentication type. type: %r' % self.type)
            self.value['password'] = value
            return self

        def secret_key(self, value):
            if self.type != 'S3':
                raise ValueError('illegal authentication type. type: %r' % self.type)
            self.value['secretKey'] = value
            return self

        def uris(self, list_of_values):
            if self.type != 'basic':
                raise ValueError('illegal authentication type. type: %r' % self.type)
            self.value['uris'] = list_of_values
            return self

        def username(self, value):
            if self.type != 'basic':
                raise ValueError('illegal authentication type. type: %r' % self.type)
            self.value['username'] = value
            return self

        def role_name(self, value):
            self.value['roleName'] = value
            return self
