# -*- coding: utf-8 -*-

from cliff.app import App
from cliff.commandmanager import CommandManager

import sys

import aws_vapor.meta as meta


class CliApp(App):
    def __init__(self):
        super(CliApp, self).__init__(
            description='Generates AWS CloudFormation template from python object',
            version=meta.version,
            command_manager=CommandManager('aws_vapor.command'),
        )


def main(argv=sys.argv[1:]) -> int:
    app = CliApp()
    return app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
