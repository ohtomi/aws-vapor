# -*- coding: utf-8 -*-

from cliff.app import App
from cliff.commandmanager import CommandManager

import sys


class CliApp(App):
    def __init__(self):
        super(CliApp, self).__init__(
            description='AWS Cloudformation Template Generator',
            version='0.0.1',
            command_manager=CommandManager('cfngen.command'),
        )


def main(argv=sys.argv[1:]):
    app = CliApp()
    return app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))