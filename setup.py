#!/usr/bin/env python
#
# Copyright 2008 David Anderson
#
# Redistribution of this file is permitted under
# the terms of the GNU Public License (GPL) version 2.

"""Distutils setup script for pywebgen."""

__author__ = 'David Anderson <dave@natulte.net>'

from distutils.core import setup
from pyweb.pywebgen import VERSION

setup(name='pywebgen',
      version=VERSION,
      description='Static website generator',
      author='David Anderson',
      author_email='dave@natulte.net',
      url='http://github.com/danderson/pywebgen',
      packages=['pyweb'],
      scripts=['pywebgen'])
