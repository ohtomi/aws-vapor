# -*- coding: utf-8 -*-

from cliff.command import Command
from json import dumps
from os import (chdir, path)

import aws_vapor.utils as utils
import sys


class Generator(Command):
    '''generates AWS CloudFormation template from python object'''

    def get_parser(self, prog_name):
        parser = super(Generator, self).get_parser(prog_name)
        parser.add_argument('vaporfile', help='file path of vaporfile')
        parser.add_argument('task', nargs='?', help='task name within vaporfile')
        parser.add_argument('--contrib', help='contrib repository url')
        parser.add_argument('--recipe', nargs='+', help='file paths of recipe on contrib repository')
        return parser

    def take_action(self, args):
        file_path = args.vaporfile
        task_name = args.task
        (vaporfile, task, directory) = self._load_vaporfile(file_path, task_name)

        chdir(directory)
        template = task()

        if args.recipe is not None:
            contrib = args.contrib # TODO use default value within config file if missing parameter
            recipes = args.recipe
            self._apply_recipes(template, contrib, recipes)

        json_document = dumps(template.to_template(), indent=2, separators=(',', ': '))
        self.app.stdout.write('{0}\n'.format(json_document))

    def _load_vaporfile(self, file_path, task_name):
        directory, filename = path.split(file_path)
        if directory not in sys.path:
            sys.path.insert(0, directory)
        vaporfile = __import__(path.splitext(filename)[0])
        del sys.path[0]

        task_name = task_name or 'generate'
        task = getattr(vaporfile, task_name)

        return (vaporfile, task, directory)

    def _apply_recipes(self, template, contrib, recipes):
        if contrib not in sys.path:
            sys.path.insert(0, contrib)
        for recipe in recipes:
            recipefile = __import__(path.splitext(recipe)[0])
            task = getattr(recipefile, 'recipe')
            task(template)
        del sys.path[0]
