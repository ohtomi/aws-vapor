# -*- coding: utf-8 -*-

from os import mkdir
from os.path import (exists, expanduser)

import ConfigParser


CONFIG_DIRECTORY = expanduser('~/.aws-cfn-gen')
CONFIG_FILE_NAME = 'config'


def load_from_config_file():
    props = {}

    if not exists(CONFIG_DIRECTORY + '/' + CONFIG_FILE_NAME):
        return props

    config = ConfigParser.RawConfigParser()
    config.read(CONFIG_DIRECTORY + '/' + CONFIG_FILE_NAME)

    for section in config.sections():
        for key, value in config.items(section):
            if not section in props:
                props[section] = {}
            props[section][key] = value

    return props


def save_to_config_file(props):
    config = ConfigParser.RawConfigParser()

    for section, entries in props.items():
        config.add_section(section)
        for key, value in entries.items():
            config.set(section, key, value)

    if not exists(CONFIG_DIRECTORY):
        mkdir(CONFIG_DIRECTORY)

    with open(CONFIG_DIRECTORY + '/' + CONFIG_FILE_NAME, 'wb') as configfile:
        config.write(configfile)
