# Copyright 2008 David Anderson
#
# Redistribution of this file is permitted under
# the terms of the GNU Public License (GPL) version 2.

"""Base class for pyweb exceptions."""

__author__ = 'David Anderson <dave@natulte.net>'


class Error(Exception):
    pass


class MissingPythonModule(Error):
    """A required python module is missing."""
