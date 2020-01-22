#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import sphinx_rtd_theme
sys.path.insert(0, os.path.abspath('../..'))
# sys.path.insert(0, os.path.abspath('/Users/piccinal/reframe.git/'))
import reframechecks
# import reframechecks.common
# import sphexa
# import reframe
# needs_sphinx = '1.6.3'
extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.autosummary',
              'sphinx.ext.doctest',
              'sphinx.ext.todo',
              'sphinx.ext.coverage',
              'sphinx.ext.imgmath',
              'sphinx.ext.intersphinx',
              'sphinx.ext.ifconfig',
              'sphinx.ext.viewcode',
              'sphinx.ext.githubpages']
intersphinx_mapping = {
    'python': ('http://docs.python.org/3', None),
}
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
autodoc_mock_imports = ['reframe', 'sphexa']
# ---
project = 'HPCTools'
copyright = '2020, Swiss National Supercomputing Center (CSCS), All rights reserved.'
author = 'SCS/CSCS'
# The full version, including alpha/beta/rc tags
release = '0.1'
# version = reframe.VERSION
# release = reframe.VERSION
language = None
# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'html/*']
# exclude_patterns = []
# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'
# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True
# -- Options for HTML output -------------------------------------------------
html_show_sourcelink = False
html_favicon = '_static/img/favicon.png'
last_updated = True
# html_theme = 'alabaster'
html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_theme_options = {
    'collapse_navigation': True,
    'display_version': True,
    'navigation_depth': 5,
    #     # 'canonical_url': True,
}
html_context = {
    'display_github': True,
    'github_user': 'eth-cscs',
    'github_repo': 'hpctools',
}
# autodoc_default_flags is now deprecated. Please use autodoc_default_options instead:
autodoc_default_flags = ['members']
# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
# This is required for the alabaster theme
# refs: http://alabaster.readthedocs.io/en/latest/installation.html#sidebars
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',  # needs 'show_related': True theme option to display
        'searchbox.html',
        'donate.html',
    ]
}
# -- Options for HTMLHelp output ------------------------------------------
# Output file base name for HTML help builder.
htmlhelp_basename = 'hpctoolsdoc'

# -- Options for manual (man) page output ---------------------------------
# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
# man_pages = [
#     (master_doc, 'reframe', 'ReFrame Documentation',
#      [author], 1)
# ]

