# -*- coding: utf-8 -*-

from aws_vapor import utils
from cliff.command import Command
from os import path
from urllib import parse, request


class Downloader(Command):
    """This is a subclass of :class:`cliff.command.Command`,
    which downloads a contributed recipe from URL."""

    def get_parser(self, prog_name):
        """Return an :class:`argparse.ArgumentParser`."""
        parser = super(Downloader, self).get_parser(prog_name)
        parser.add_argument('url', help='url of recipe')
        return parser

    def take_action(self, args):
        """Download a recipe from remote URL and save it to a local file under contrib directory.

        Args:
            args (:obj:`dict`): Parsed command line arguments.
                "url" is an URL where a recipe will be downloaded from.
        """
        file_url = args.url
        filename = parse.urlsplit(file_url).path.split('/')[-1:][0]
        contrib = utils.get_property_from_config_file('defaults', 'contrib')
        self._download_recipe(file_url, filename, contrib)

    @staticmethod
    def _download_recipe(file_url, filename, contrib):
        file_path = path.join(contrib, filename)
        request.urlretrieve(file_url, file_path)
