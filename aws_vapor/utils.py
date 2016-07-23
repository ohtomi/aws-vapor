# -*- coding: utf-8 -*-

from contextlib import contextmanager
from os import (getcwd, mkdir, path)
from sys import getdefaultencoding
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import ConfigParser


CURRENT_DIRECTORY = getcwd()
CONFIG_DIRECTORY = path.expanduser('~/.aws-vapor')
CONFIG_FILE_NAME = 'config'


def load_from_config_file(config_directory=CONFIG_DIRECTORY):
    props = {}

    if not path.exists(path.join(config_directory, CONFIG_FILE_NAME)):
        return props

    config = ConfigParser.RawConfigParser()
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
    for name, section in load_from_config_file(CURRENT_DIRECTORY).items():
        if not props.has_key(name):
            props[name] = {}
        for k, v in section.items():
            props[name][k] = v

    return props


def get_property_from_config_files(section, key, default_value=None):
    props = load_from_config_files()
    if not props.has_key(section):
        return default_value

    section = props[section]
    if not section.has_key(key):
        return default_value

    value = section[key]
    if value is None:
        return default_value

    return value


def save_to_config_file(props):
    config = ConfigParser.RawConfigParser()

    for section, entries in props.items():
        config.add_section(section)
        for key, value in entries.items():
            config.set(section, key, value)

    if not path.exists(CONFIG_DIRECTORY):
        mkdir(CONFIG_DIRECTORY)

    with open(path.join(CONFIG_DIRECTORY, CONFIG_FILE_NAME), 'wb') as configfile:
        config.write(configfile)


def combine_user_data(files):
    combined_message = MIMEMultipart()

    for filename, format_type in files:
        with open(filename) as fh:
            contents = fh.read()
        sub_message = MIMEText(contents, format_type, getdefaultencoding())
        sub_message.add_header('Content-Disposition', 'attachment; filename="%s"' % (filename))
        combined_message.attach(sub_message)

    return str(combined_message)


def _replace_params(line, params):
    for k, v in params.items():
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

    with open(file_path, 'wb') as outputfile:
        yield outputfile
