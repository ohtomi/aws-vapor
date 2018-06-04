# -*- coding: utf-8 -*-

from typing import Any
from argparse import ArgumentParser

from aws_vapor import utils
from cliff.command import Command


class Configure(Command):
    """This class shows the current configuration or sets a new configuration."""

    def get_parser(self, program_name: str) -> ArgumentParser:
        parser = super(Configure, self).get_parser(program_name)
        subparsers = parser.add_subparsers(help='sub-command', title='sub-commands')

        list_sub_parser = subparsers.add_parser('list', help='lists all values within config file')
        list_sub_parser.set_defaults(func=list_configuration, command=self)

        set_sub_parser = subparsers.add_parser('set', help='sets key to specified value')
        set_sub_parser.set_defaults(func=set_configuration)
        set_sub_parser.add_argument('--system', action='store_true', default=False,
                                    help='a flag whether or not a new configuration will be saved globally')
        set_sub_parser.add_argument('section',
                                    help='a name of a configuration section block')
        set_sub_parser.add_argument('key',
                                    help='a name of a configuration property')
        set_sub_parser.add_argument('value',
                                    help='a value of a configuration property')

        return parser

    def take_action(self, args: Any):
        args.func(args)


def list_configuration(args: Any):
    """Show the current configuration."""
    props = utils.load_from_config_file()
    for section, entries in list(props.items()):
        args.command.app.stdout.write('[{0}]\n'.format(section))
        for key, value in list(entries.items()):
            args.command.app.stdout.write('{0} = {1}\n'.format(key, value))


def set_configuration(args: Any):
    """Set a new configuration."""
    save_on_global = args.system

    config_directory = [utils.GLOBAL_CONFIG_DIRECTORY] if save_on_global else [utils.LOCAL_CONFIG_DIRECTORY]
    props = utils.load_from_config_file(config_directories=config_directory)

    if args.section not in props:
        props[args.section] = {}
    section = props[args.section]
    section[args.key] = args.value

    utils.save_to_config_file(props, save_on_global)
