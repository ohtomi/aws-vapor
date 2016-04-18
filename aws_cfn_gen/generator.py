# -*- coding: utf-8 -*-

from cliff.command import Command

import aws_cfn_gen.utils as utils


class Generator(Command):
    '''generate AWS Cloudformation template'''

    def get_parser(self, prog_name):
        parser = super(Generator, self).get_parser(prog_name)
        parser.add_argument('data', nargs=1, metavar='<template.py>', help='template script filename')
        return parser

    def take_action(self, parsed_args):
        self.app.stdout.write('data -> {0}\n'.format(parsed_args.data[0]))

        props = utils.load_config_file()
        self.app.stdout.write('{0} -> {1}\n'.format('username', props['variables']['username']))
