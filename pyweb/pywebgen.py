# Copyright 2008 David Anderson
#
# Redistribution of this file is permitted under
# the terms of the GNU Public License (GPL) version 2.

"""The main pyweb executable.

This file, when executed (via the `pywebgen` stub), generates a
website by taking data out of source, optionally applying a filter,
and dropping the file in a generated output directory.
"""

__author__ = 'David Anderson <dave@natulte.net>'

import optparse
import sys

import generator


USAGE = '%prog <input directory> <output directory>'
VERSION = '0.1.0'


def main():
    parser = optparse.OptionParser(usage=USAGE, version='%prog ' + VERSION)
    (options, args) = parser.parse_args()

    if len(args) != 2:
        parser.print_help()
        return 1

    generator.Generate(args[0], args[1])

    return 0
