# -*- coding: utf-8 -*-

from cliff.command import Command
from json import dumps
from os import path

import aws_vapor.utils as utils
import sys


class Generator(Command):
    '''generates AWS CloudFormation template from python object'''

    def get_parser(self, prog_name):
        parser = super(Generator, self).get_parser(prog_name)
        parser.add_argument('vaporfile', help='file path of vaporfile')
        parser.add_argument('task', nargs='?', help='task name within vaporfile')
        return parser

    def take_action(self, args):
        file_path = args.vaporfile
        vaporfile = self._load_vaporfile(file_path)

        task_name = args.task or 'generate'
        task = getattr(vaporfile, task_name)

        template = task()
        json_document = dumps(template.to_template(), indent=2, separators=(',', ': '))
        self.app.stdout.write('{0}\n'.format(json_document))

    def _load_vaporfile(self, file_path):
        directory, filename = path.split(file_path)
        if directory not in sys.path:
            sys.path.insert(0, directory)
        imported = __import__(path.splitext(filename)[0])
        del sys.path[0]
        return imported
