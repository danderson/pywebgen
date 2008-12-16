# Copyright 2008 David Anderson
#
# Redistribution of this file is permitted under
# the terms of the GNU Public License (GPL) version 2.

"""The generator is the main driver of the website compile process."""

__author__ = 'David Anderson <dave@natulte.net>'

import os.path
import shutil
import time


class Error(Exception):
    """Base class for generator errors"""

class MissingInputDirectory(Error):
    """The input directory is missing"""

class ObstructedOutputPath(Error):
    """The given output path is obstructed by a non-directory."""


def _create_dir(path):
    if os.path.exists(path) and not os.path.isdir(path):
        raise ObstructedOutputPath(path)
    if not os.path.exists(path):
        os.makedirs(path)


class Generator(object):
    def __init__(self, input_dir, output_dir):
        """Initializer.

        Args:
          input_dir: the directory containing the website input files.
          output_dir: the directory that will contain the website.

        Raises:
          MissingInputDirectory: the given path is absent, or not a directory.
          ObstructedOutputPath: the output path is not a directory.
        """
        self._in_dir = os.path.abspath(input_dir)
        if not os.path.isdir(self._in_dir):
            raise MissingInputDirectory(self._in_dir)

        self._out_dir = os.path.abspath(output_dir)
        _create_dir(self._out_dir)

    def Generate(self):
        """Generate a new version of the website."""
        ts = time.strftime('%Y%m%d.%H%M%S')
        out_dir = os.path.join(self._out_dir, ts)
        _create_dir(out_dir)

        for root, dirs, files in os.walk(self._in_dir):
            out_root = os.path.join(out_dir, root[len(self._in_dir):])
            _create_dir(out_root)

            # Process each file
            for file in files:
                self._ProcessFile(root, out_root, file)

            # Filter the subdirectories to process.
            dirs[:] = [d for d in dirs if d[0] not in ('.', '_')]

    def _ProcessFile(self, in_dir, out_dir, file):
        # TODO(dave): more complex stuff here.
        i = os.path.join(in_dir, file)
        o = os.path.join(out_dir, file)

        shutil.copyfile(i, o)
        shutil.copymode(i, o)
