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
import util


class MissingInputDirectory(error.Error):
    """The input directory is missing"""


class NoProcessorFound(error.Error):
    """No processor was found to process an input file."""


class Generator(object):
    def __init__(self, input_root, use_processors):
        self._input_root = os.path.abspath(input_root)
        self._processors = processors.GetProcessors(use_processors)

    def Generate(self, output_root, timestamp=None, manifest_path=None):
        """Generate the website into the given output root."""
        self._Prepare(output_root, timestamp, manifest_path)
        self._GenerateTree()
        self._Cleanup()

    def _Prepare(self, output_root, timestamp, manifest_path):
        self._output_root = os.path.abspath(output_root)
        timestamp = timestamp or time.localtime()
        self._manifest_path = manifest_path

        if not os.path.isdir(self._input_root):
            raise MissingInputDirectory(self._input_root)

        self._ctx = {
            'timestamp': time.asctime(timestamp),
            'input_root': self._input_root,
            'output_root': output_root
            }

        self._manifest = []

        for processor in self._processors:
            processor.StartProcessing(self._ctx)

    def _Cleanup(self):
        for processor in self._processors:
            processor.EndProcessing()

        self._OutputManifest()

        del self._manifest
        del self._ctx
        del self._output_root

    def _GenerateTree(self):
        for input_dir, dirs, files in os.walk(self._input_root):
            util.CreateDir(self._InputToOutput(input_dir))
            self._manifest.append(
                util.PathAsSuffix(input_dir, self._input_root))

            # Process each file.
            for file in files:
                self._ProcessFile(os.path.join(input_dir, file))

            # Filter directories to process.
            dirs[:] = [d for d in dirs if d[0] not in ('.', '_')]

    def _ProcessFile(self, input_path):
        for processor in self._processors:
            if processor.CanProcessFile(input_path):
                output_path = self._InputToOutput(input_path)
                if processor.ProcessFile(input_path, output_path):
                    self._manifest.append(
                        util.PathAsSuffix(output_path, self._output_root))
                return

        raise NoProcessorFound(input_path)

    def _OutputManifest(self):
        if not self._manifest_path:
            return

        # Append '' to get an \n at the end of the file, and remove
        # the first entry because it's the '' for the output root.
        self._manifest.append('')
        util.WriteFileContent(self._manifest_path,
                              '\n'.join(self._manifest[1:]))

    def _InputToOutput(self, path):
        return util.RelocatePath(path, self._input_root, self._output_root)
