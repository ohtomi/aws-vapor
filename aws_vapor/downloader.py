# -*- coding: utf-8 -*-

from typing import Any
from argparse import ArgumentParser

from aws_vapor import utils
from cliff.command import Command
from os import path
from urllib import parse, request


class Downloader(Command):
    """This class downloads recipe from remote repository."""

    def get_parser(self, prog_name: str) -> ArgumentParser:
        parser = super(Downloader, self).get_parser(prog_name)
        parser.add_argument('url',
                            help='an URL of downloading recipe')
        return parser

    def take_action(self, args: Any):
        file_url = args.url
        filename = parse.urlsplit(file_url).path.split('/')[-1:][0]
        contrib = utils.get_property_from_config_file('defaults', 'contrib')
        download_recipe(file_url, filename, contrib)


def download_recipe(file_url: str, filename: str, contrib: str):
    file_path = path.join(contrib, filename)
    request.urlretrieve(file_url, file_path)
