# -*- coding: utf-8 -*-

from contextlib import contextmanager
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from six import PY3
from six.moves import configparser

import os

LOCAL_CONFIG_DIRECTORY = CURRENT_DIRECTORY = os.getcwd()
GLOBAL_CONFIG_DIRECTORY = os.path.expanduser('~/.aws-vapor')
CONFIG_FILE_NAME = 'config'

FILE_WRITE_MODE = 'wt' if PY3 else 'wb'


def load_from_config_file(config_directories=None):
    """Load properties from a config file.

    Args:
        config_directories (:class:`list` of :class:`str`): A path to config directory having 'config'.
            If not specified, locating 'config' on `GLOBAL_CONFIG_DIRECTORY` and `LOCAL_CONFIG_DIRECTORY`.

    Returns:
        A :class:`dict` of properties loaded from a config file.

        example::

            {
                'section': {
                    'key1': 'value1',
                    'key2': 'value2'
                }
            }
    """
    if config_directories is None:
        config_directories = [GLOBAL_CONFIG_DIRECTORY, LOCAL_CONFIG_DIRECTORY]
    props = {}

    config = configparser.RawConfigParser()
    config.read([os.path.join(config_directory, CONFIG_FILE_NAME) for config_directory in config_directories])

    for section in config.sections():
        for key, value in config.items(section):
            if section not in props:
                props[section] = {}
            props[section][key] = value

    return props


def get_property_from_config_file(section, key, default_value=None):
    """Get a property value from a config file.

    Args:
        section (:class:`str`): A name of a section.

        key (:class:`str`): A name of a property.

        default_value (:class:`str`): A value will be returned when a property is not defined.

    Returns:
        A property value corresponding to the `key`, which is property name, in the `section`,
        or `default_value` if the `section` is not defined or the `key` is not defined.
    """
    props = load_from_config_file()
    if section not in props:
        return default_value

    section = props[section]
    if key not in section:
        return default_value

    value = section[key]
    if value is None:
        return default_value

    return value


def save_to_config_file(props, save_on_global=False):
    """Save properties to a config file.

    Args:
        props (:class:`dict`): A :class:`dict` of properties.

        save_on_global (bool): A flag whether or not a new configuration will be saved globaly.
    """
    config = configparser.RawConfigParser()

    for section, entries in list(props.items()):
        config.add_section(section)
        for key, value in list(entries.items()):
            config.set(section, key, value)

    if save_on_global:
        if not os.path.exists(GLOBAL_CONFIG_DIRECTORY):
            os.mkdir(GLOBAL_CONFIG_DIRECTORY)

        with open(os.path.join(GLOBAL_CONFIG_DIRECTORY, CONFIG_FILE_NAME), mode=FILE_WRITE_MODE) as configfile:
            config.write(configfile)

    else:
        with open(os.path.join(LOCAL_CONFIG_DIRECTORY, CONFIG_FILE_NAME), mode=FILE_WRITE_MODE) as configfile:
            config.write(configfile)


def combine_user_data(files):
    """Make a multipart/* message from a file content.

    Args:
        files (:class:`list` of :class:`str`): Paths to a file, a content of which will be used as 'UserData'.

    Returns:
        A multipart/* message attached a file content to.
    """
    combined_message = MIMEMultipart()

    for filename, format_type in files:
        with open(filename) as fh:
            contents = fh.read()
        sub_message = MIMEText(contents, format_type, 'ascii')
        sub_message.add_header('Content-Disposition', 'attachment; filename="%s"' % filename)
        combined_message.attach(sub_message)

    return str(combined_message)


def _replace_params(line, params):
    for k, v in list(params.items()):
        key = '{{ %s }}' % k
        if line.find(key) != -1:
            pos = line.index(key)
            l_line = line[:pos]
            r_line = line[pos + len(key):]
            return _replace_params(l_line, params) + [v] + _replace_params(r_line, params)
    return [line]


def inject_params(lines, params):
    """Replace placeholders with parameters.

    Args:
        lines (:class:`list` of :class:`str`): A file content including placeholders (`{{ ... }}`).

        params (:class:`dict`): A :class:`dict` mapping a name of placeholders to a value.

    Returns:
        A file content replaced placeholders with parameters.
    """
    tokens = []
    for line in lines.split('\n'):
        line += '\n'
        for token in _replace_params(line, params):
            tokens.append(token)
    return tokens


@contextmanager
def open_outputfile(relative_file_path):
    """Open an output file.

    Args:
        relative_file_path (:class:`str`): A path to an output file.

    Retruns:
        A file descriptor of an output file.
    """
    file_path = os.path.join(CURRENT_DIRECTORY, relative_file_path)
    directory, filename = os.path.split(file_path)

    if not os.path.exists(directory):
        os.mkdir(directory)

    with open(file_path, mode=FILE_WRITE_MODE) as outputfile:
        yield outputfile
