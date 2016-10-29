# -*- coding: utf-8 -*-

from aws_vapor import utils
from cliff.command import Command


class Configure(Command):
    '''show current configuration or set new configuration'''

    def get_parser(self, prog_name):
        parser = super(Configure, self).get_parser(prog_name)
        subparsers = parser.add_subparsers(help='sub-command', title='sub-commands')

        list_subparser = subparsers.add_parser('list', help='lists all values within config file')
        list_subparser.set_defaults(func=self.list_configuration)

        set_subparser = subparsers.add_parser('set', help='sets key to specified value')
        set_subparser.set_defaults(func=self.set_configuration)
        set_subparser.add_argument('--system', action='store_true', default=False)
        set_subparser.add_argument('section')
        set_subparser.add_argument('key')
        set_subparser.add_argument('value')

        return parser

    def take_action(self, args):
        args.func(args)

    def list_configuration(self, args):
        props = utils.load_from_config_file()
        for section, entries in list(props.items()):
            self.app.stdout.write('[{0}]\n'.format(section))
            for key, value in list(entries.items()):
                self.app.stdout.write('{0} = {1}\n'.format(key, value))

    def set_configuration(self, args):
        save_on_global = args.system

        config_directory = [utils.GLOBAL_CONFIG_DIRECTORY] if save_on_global else [utils.LOCAL_CONFIG_DIRECTORY]
        props = utils.load_from_config_file(config_directories=config_directory)

        if args.section not in props:
            props[args.section] = {}
        section = props[args.section]
        section[args.key] = args.value

        utils.save_to_config_file(props, save_on_global)
