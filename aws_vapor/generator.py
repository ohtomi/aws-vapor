# -*- coding: utf-8 -*-

from typing import Any, List, Tuple
from argparse import ArgumentParser

from aws_vapor import dsl, utils
from cliff.command import Command
from json import dumps

import os
import sys


class Generator(Command):
    """This class generates an AWS CloudFormation template from Python objects."""

    def get_parser(self, program_name: str) -> ArgumentParser:
        parser = super(Generator, self).get_parser(program_name)
        parser.add_argument('vaporfile',
                            help='a file path to vaporfile')
        parser.add_argument('task', nargs='?',
                            help='a task name defined in vaporfile')
        parser.add_argument('--contrib',
                            help='a module search path of contrib recipes')
        parser.add_argument('--recipe', nargs='+',
                            help='a module name of contrib recipe')
        parser.add_argument('--output',
                            help='an output file name')
        return parser

    def take_action(self, args: Any):
        file_path = args.vaporfile
        task_name = args.task
        (vaporfile, task, directory) = load_vaporfile(file_path, task_name)

        os.chdir(directory)
        template = task()

        if args.recipe is not None:
            contrib = args.contrib or utils.get_property_from_config_file('defaults', 'contrib')
            recipes = args.recipe
            apply_recipes(template, contrib, recipes)

        output_template(self, template, args.output)


def load_vaporfile(file_path: str, task_name: str) -> Tuple[object, any, str]:
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

    return vaporfile, task, directory


def apply_recipes(template: dsl.Template, contrib: str, recipes: List[str]):
    edited_module_search_path = False
    if contrib is not None and contrib not in sys.path:
        sys.path.insert(0, contrib)
        edited_module_search_path = True

    for recipe in recipes:
        recipe_file = __import__(os.path.splitext(recipe)[0])
        task = getattr(recipe_file, 'recipe')
        task(template)

    if edited_module_search_path:
        del sys.path[0]


def output_template(command: Command, template: dsl.Template, relative_file_path: str = None):
    json_document = dumps(template.to_template(), indent=2, separators=(',', ': '))

    if relative_file_path is None:
        command.app.stdout.write('{0}\n'.format(json_document))
    else:
        with utils.open_output_file(relative_file_path) as output_file:
            output_file.write('{0}\n'.format(json_document))
