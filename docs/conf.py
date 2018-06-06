# -*- coding: utf-8 -*-

import os
import sys
import sphinx_rtd_theme

sys.path.insert(0, os.path.abspath('../'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon'
]
templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'
project = 'aws-vapor'
copyright = '2018, Kenichi Ohtomi'
author = 'Kenichi Ohtomi'
version = '0.0'
release = '0.0.14'
exclude_patterns = [
    '_build',
    'Thumbs.db',
    '.DS_Store'
]
pygments_style = 'sphinx'

language = 'en'

todo_include_todos = True

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
# html_theme_options = {}
