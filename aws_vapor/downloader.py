# -*- coding: utf-8 -*-

from aws_vapor import utils
from cliff.command import Command
from os import path
from six.moves.urllib import parse
from six.moves.urllib import request


class Downloader(Command):
    '''download contributed recipe from url'''

    def get_parser(self, prog_name):
        parser = super(Downloader, self).get_parser(prog_name)
        parser.add_argument('url', help='url of recipe')
        return parser

    def take_action(self, args):
        file_url = args.url
        filename = parse.urlsplit(file_url).path.split('/')[-1:][0]
        contrib = utils.get_property_from_config_file('defaults', 'contrib')
        self._download_recipe(file_url, filename, contrib)

    def _download_recipe(self, file_url, filename, contrib):
        file_path = path.join(contrib, filename)
        request.urlretrieve(file_url, file_path)
