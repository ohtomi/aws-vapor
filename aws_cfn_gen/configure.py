# -*- coding: utf-8 -*-

from cliff.command import Command
from os import mkdir
from os.path import (exists, expanduser)

import ConfigParser


CONFIG_SECTION_DICT = 'dictionary'
CONFIG_SECTION_VARS = 'variables'
CONFIG_DIRECTORY = expanduser('~/.aws-cfn-gen')


class Configure(Command):
    '''configure this tool'''

    def take_action(self, parsed_args):
        config = ConfigParser.RawConfigParser()

        config.add_section(CONFIG_SECTION_DICT)
        # TODO
        config.add_section(CONFIG_SECTION_VARS)
        # TODO

        if not exists(CONFIG_DIRECTORY):
            mkdir(CONFIG_DIRECTORY)

        with open(CONFIG_DIRECTORY + '/config', 'wb') as configfile:
            config.write(configfile)
