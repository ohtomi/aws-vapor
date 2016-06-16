# -*- coding: utf-8 -*-

from os import mkdir
from os.path import (exists, expanduser)
from sys import getdefaultencoding
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import ConfigParser


CONFIG_DIRECTORY = expanduser('~/.cfngen')
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


def build_multi_part_user_data(files):
    combined_message = MIMEMultipart()

    for filename, format_type in files:
        with open(filename) as fh:
            contents = fh.read()
        sub_message = MIMEText(contents, format_type, getdefaultencoding())
        sub_message.add_header('Content-Disposition', 'attachment; filename="%s"' % (filename))
        combined_message.attach(sub_message)

    return str(combined_message)
