# -*- coding: utf-8 -*-

from contextlib import contextmanager
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os import (getcwd, mkdir, path)
from six import PY3
from six.moves import configparser


CURRENT_DIRECTORY = getcwd()
CONFIG_DIRECTORY = path.expanduser('~/.aws-vapor')
CONFIG_FILE_NAME = 'config'

FILE_WRITE_MODE = 'wt' if PY3 else 'wb'


def load_from_config_file(config_directory=CONFIG_DIRECTORY):
    props = {}

    if not path.exists(path.join(config_directory, CONFIG_FILE_NAME)):
        return props

    config = configparser.RawConfigParser()
    config.read(path.join(config_directory, CONFIG_FILE_NAME))

    for section in config.sections():
        for key, value in config.items(section):
            if not section in props:
                props[section] = {}
            props[section][key] = value

    return props


def load_from_config_files():
    # load from a config file under the user home directory
    props = load_from_config_file(CONFIG_DIRECTORY)

    # overwrite properties from a config file under the current directory
    for name, section in list(load_from_config_file(CURRENT_DIRECTORY).items()):
        if name not in props:
            props[name] = {}
        for k, v in list(section.items()):
            props[name][k] = v

    return props


def get_property_from_config_files(section, key, default_value=None):
    props = load_from_config_files()
    if section not in props:
        return default_value

    section = props[section]
    if key not in section:
        return default_value

    value = section[key]
    if value is None:
        return default_value

    return value


def save_to_config_file(props):
    config = configparser.RawConfigParser()

    for section, entries in list(props.items()):
        config.add_section(section)
        for key, value in list(entries.items()):
            config.set(section, key, value)

    if not path.exists(CONFIG_DIRECTORY):
        mkdir(CONFIG_DIRECTORY)

    with open(path.join(CONFIG_DIRECTORY, CONFIG_FILE_NAME), mode=FILE_WRITE_MODE) as configfile:
        config.write(configfile)


def combine_user_data(files):
    combined_message = MIMEMultipart()

    for filename, format_type in files:
        with open(filename) as fh:
            contents = fh.read()
        sub_message = MIMEText(contents, format_type, 'ascii')
        sub_message.add_header('Content-Disposition', 'attachment; filename="%s"' % (filename))
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
    tokens = []
    for line in lines.split('\n'):
        line += '\n'
        for token in _replace_params(line, params):
            tokens.append(token)
    return tokens


@contextmanager
def open_outputfile(relative_file_path):
    file_path = path.join(CURRENT_DIRECTORY, relative_file_path)
    directory, filename = path.split(file_path)

    if not path.exists(directory):
        mkdir(directory)

    with open(file_path, mode=FILE_WRITE_MODE) as outputfile:
        yield outputfile
