# -*- coding: utf-8 -*-

from cliff.command import Command

import aws_vapor.utils as utils


class Configure(Command):
    '''shows current configuration or sets new configuration'''

    def get_parser(self, prog_name):
        parser = super(Configure, self).get_parser(prog_name)
        subparsers = parser.add_subparsers(help='sub-command', title='sub-commands')

        list_subparser = subparsers.add_parser('list', help='lists all values within config file')
        list_subparser.set_defaults(func=self.list_configuration)

        set_subparser = subparsers.add_parser('set', help='sets key to specified value')
        set_subparser.set_defaults(func=self.set_configuration)
        set_subparser.add_argument('section')
        set_subparser.add_argument('key')
        set_subparser.add_argument('value')

        return parser

    def take_action(self, args):
        args.func(args)

    def list_configuration(self, args):
        props = utils.load_from_config_files()
        for section, entries in props.items():
            self.app.stdout.write(u'[{0}]\n'.format(section))
            for key, value in entries.items():
                self.app.stdout.write(u'{0} = {1}\n'.format(key, value))

    def set_configuration(self, args):
        props = utils.load_from_config_file()

        if not props.has_key(args.section):
            props[args.section] = {}
        section = props[args.section]
        section[args.key] = args.value

        utils.save_to_config_file(props)
