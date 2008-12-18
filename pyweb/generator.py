# Copyright 2008 David Anderson
#
# Redistribution of this file is permitted under
# the terms of the GNU Public License (GPL) version 2.

"""The generator is the main driver of the website compile process."""

__author__ = 'David Anderson <dave@natulte.net>'

import os.path
import shutil
import time

import error
import processors


class MissingInputDirectory(error.Error):
    """The input directory is missing"""


class ObstructedOutputPath(error.Error):
    """The given output path is obstructed by a non-directory."""


class NoProcessorFound(error.Error):
    """No processor was found to process an input file."""


def Generate(input_root, output_root, use_processors, timestamp=None):
    """Generate a new version of the website."""
    input_root = os.path.abspath(input_root)
    output_root = os.path.abspath(output_root)

    ctx, processor_objs = _PrepareGenerate(input_root, output_root,
                                           use_processors, timestamp)

    for input_dir, dirs, files in os.walk(input_root):
        output_dir = os.path.join(output_root, input_dir[len(input_root):])
        _CreateDir(output_dir)

        # Process each file
        for file in files:
            _ProcessFile(processor_objs, input_dir, output_dir, file)

        # Filter the subdirectories to process.
        dirs[:] = [d for d in dirs if d[0] not in ('.', '_')]


def _PrepareGenerate(input_root, output_root, use_processors, timestamp=None):
    """Prepare website generation and return relevant data."""
    timestamp = timestamp or time.localtime()

    if not os.path.isdir(input_root):
        raise MissingInputDirectory(input_root)

    ctx = {
        'timestamp': time.asctime(timestamp),
        'input_root': input_root,
        'output_root': output_root
        }
    processor_objs = processors.GetProcessors(use_processors, ctx)

    return ctx, processor_objs


def _ProcessFile(processor_objs, in_dir, out_dir, file):
    i = os.path.join(in_dir, file)
    o = os.path.join(out_dir, file)

    for processor in processor_objs:
        if processor.CanProcessFile(file):
            processor.ProcessFile(i, o)
            return

    raise NoProcessorFound(i)


def _CreateDir(path):
    if os.path.exists(path):
        raise ObstructedOutputPath(path)
    else:
        os.makedirs(path)
