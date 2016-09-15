# -*- coding: utf-8 -*-

from aws_vapor import utils
from cliff.command import Command
from json import dumps

import os
import sys


class Generator(Command):
    '''generate AWS CloudFormation template from python object'''

    def get_parser(self, prog_name):
        parser = super(Generator, self).get_parser(prog_name)
        parser.add_argument('vaporfile', help='file path of vaporfile')
        parser.add_argument('task', nargs='?', help='task name within vaporfile')
        parser.add_argument('--contrib', help='contrib repository url')
        parser.add_argument('--recipe', nargs='+', help='file paths of recipe on contrib repository')
        parser.add_argument('--output', help='output file name')
        return parser

    def take_action(self, args):
        file_path = args.vaporfile
        task_name = args.task
        (vaporfile, task, directory) = self._load_vaporfile(file_path, task_name)

        os.chdir(directory)
        template = task()

        if args.recipe is not None:
            contrib = args.contrib or utils.get_property_from_config_file('defaults', 'contrib')
            recipes = args.recipe
            self._apply_recipes(template, contrib, recipes)

        self._output_template(template, args.output)

    def _load_vaporfile(self, file_path, task_name):
        directory, filename = os.path.split(file_path)

        edited_module_search_path = False
        if directory not in sys.path:
            sys.path.insert(0, directory)
            edited_module_search_path = True

        vaporfile = __import__(os.path.splitext(filename)[0])

        if edited_module_search_path:
            del sys.path[0]

        task_name = task_name or 'generate'
        task = getattr(vaporfile, task_name)

        return (vaporfile, task, directory)

    def _apply_recipes(self, template, contrib, recipes):
        edited_module_search_path = False
        if contrib is not None and contrib not in sys.path:
            sys.path.insert(0, contrib)
            edited_module_search_path = True

        for recipe in recipes:
            recipefile = __import__(os.path.splitext(recipe)[0])
            task = getattr(recipefile, 'recipe')
            task(template)

        if edited_module_search_path:
            del sys.path[0]

    def _output_template(self, template, relative_file_path=None):
        json_document = dumps(template.to_template(), indent=2, separators=(',', ': '))

        if relative_file_path is None:
            self.app.stdout.write('{0}\n'.format(json_document))
        else:
            with utils.open_outputfile(relative_file_path) as outputfile:
                outputfile.write('{0}\n'.format(json_document))
