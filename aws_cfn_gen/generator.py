# -*- coding: utf-8 -*-

from cliff.command import Command


class Generator(Command):
    '''generate AWS Cloudformation template'''

    def get_parser(self, prog_name):
        parser = super(Generator, self).get_parser(prog_name)
        parser.add_argument('data', nargs=1, metavar='<template.py>', help='template script filename')
        return parser

    def take_action(self, parsed_args):
        self.app.stdout.write('data -> %s\n' % parsed_args.data[0])
