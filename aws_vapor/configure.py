# -*- coding: utf-8 -*-

from aws_vapor import utils
from cliff.command import Command


class Configure(Command):
    """This is a subclass of :class:`cliff.command.Command`,
    which shows the current configuration or sets a new configuration."""

    def get_parser(self, prog_name):
        """Return an :class:`argparse.ArgumentParser`."""
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
        """Show the current configuration or set a new configuration.

        The first parsed command line argument is a sub command name.
        Show the current configuration if the sub command is "list",
        Or set a new configuration if the sub command is "set".

        Args:
            args (:obj:`dict`): Parsed command line arguments.
                "func" is a method object of this class.
                other keys may be used by "func".
        """
        args.func(args)

    def list_configuration(self, args):
        """Show the current configuration.

        Args:
            args (:obj:`dict`): not be used.
        """
        props = utils.load_from_config_file()
        for section, entries in list(props.items()):
            self.app.stdout.write('[{0}]\n'.format(section))
            for key, value in list(entries.items()):
                self.app.stdout.write('{0} = {1}\n'.format(key, value))

    def set_configuration(self, args):
        """Set a new configuration.

        Args:
            args (:obj:`dict`): Parsed command line arguments.
                "system" is a flag whether or not a new configuration will be saved globaly.
                "section" is a name of configuration section block.
                "key" is a name of configuration property.
                "value" is a value of configuration property.
        """
        save_on_global = args.system

        config_directory = [utils.GLOBAL_CONFIG_DIRECTORY] if save_on_global else [utils.LOCAL_CONFIG_DIRECTORY]
        props = utils.load_from_config_file(config_directories=config_directory)

        if args.section not in props:
            props[args.section] = {}
        section = props[args.section]
        section[args.key] = args.value

        utils.save_to_config_file(props, save_on_global)
