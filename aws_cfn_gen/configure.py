# -*- coding: utf-8 -*-

from cliff.command import Command

import aws_cfn_gen.utils as utils


CONFIG_SECTION_VOCABULARY = 'vocabulary'
CONFIG_SECTION_VARIABLES = 'variables'


class Configure(Command):
    '''configure this tool'''

    def get_parser(self, prog_name):
        parser = super(Configure, self).get_parser(prog_name)
        parser.add_argument('mode', choices=['show', 'create'])
        return parser

    def take_action(self, parsed_args):
        if parsed_args.mode == 'show':
            self.show_current_configuration()
        elif parsed_args.mode == 'create':
            self.create_new_configuration()
        else:
            raise ValueError('unknown mode')

    def show_current_configuration(self):
        props = utils.load_config_file()
        for section, entries in props.items():
            self.app.stdout.write(u'[{0}]\n'.format(section))
            for key, value in entries.items():
                self.app.stdout.write(u'{0} = {1}\n'.format(key, value))

    def create_new_configuration(self):
        props = {}

        entries = {}
        # TODO
        props[CONFIG_SECTION_VOCABULARY] = entries

        entries = {}
        # TODO
        props[CONFIG_SECTION_VARIABLES] = entries

        utils.save_configuration(props)
