# Copyright 2008 David Anderson
#
# Redistribution of this file is permitted under
# the terms of the GNU Public License (GPL) version 2.

"""The generator is the main driver of the website compile process."""

__author__ = 'David Anderson <dave@natulte.net>'

import os.path
import shutil
import time

import processors

class Error(Exception):
    """Base class for generator errors"""

class MissingInputDirectory(Error):
    """The input directory is missing"""

class ObstructedOutputPath(Error):
    """The given output path is obstructed by a non-directory."""

class NoProcessorFound(Error):
    """No processor was found to process an input file."""


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
        out_dir = self._PrepareGenerate()
        for root, dirs, files in os.walk(self._in_dir):
            out_root = os.path.join(out_dir, root[len(self._in_dir):])
            _create_dir(out_root)

            # Process each file
            for file in files:
                self._ProcessFile(root, out_root, file)

            # Filter the subdirectories to process.
            dirs[:] = [d for d in dirs if d[0] not in ('.', '_')]

        del self._processors
        del self._ctx

    def _PrepareGenerate(self):
        ts = time.localtime()
        ts_dir = time.strftime('%Y%m%d.%H%M%S', ts)
        out_dir = os.path.join(self._out_dir, ts_dir)
        _create_dir(out_dir)

        self._ctx = {
            'timestamp': time.mktime(ts),
            'in_root': self._in_dir,
            'out_root': out_dir
            }
        self._processors = [c(self._ctx) for c in processors.PROCESSORS]

        return out_dir

    def _ProcessFile(self, in_dir, out_dir, file):
        # TODO(dave): more complex stuff here.
        i = os.path.join(in_dir, file)
        o = os.path.join(out_dir, file)

        for processor in self._processors:
            if processor.CanProcessFile(file):
                processor.ProcessFile(i, o)
                return

        raise NoProcessorFound(i)
