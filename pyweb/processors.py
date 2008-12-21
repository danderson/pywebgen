# Copyright 2008 David Anderson
#
# Redistribution of this file is permitted under
# the terms of the GNU Public License (GPL) version 2.

"""Processors take input files and munge them into an output file."""

__author__ = 'David Anderson <dave@natulte.net>'

import os.path
import shutil

import error
import util


class UnknownProcessor(error.Error):
    """Unknown input processor."""


class _Processor(object):
    """Base class for file processors."""
    def StartProcessing(self, ctx):
        """Called once the context is established, before generation begins."""
        pass

    def CanProcessFile(self, filename):
        """Called to determine if this processor is suitable for a file."""
        raise NotImplementedError()

    def ProcessFile(self, in_path, out_path):
        raise NotImplementedError()

    def EndProcessing(self):
        """Called after generation of all files has finished."""
        pass


#
# General processors
#
class HtmlJinjaProcessor(_Processor):
    """Generate HTML from a Jinja2 template."""
    def __init__(self):
        try:
            import jinja2
        except ImportError:
            raise error.MissingPythonModule('jinja2')

    def StartProcessing(self, ctx):
        import jinja2
        self._ctx = ctx
        loader = jinja2.FileSystemLoader(ctx['input_root'])
        self._env = jinja2.Environment(loader=loader)

    def CanProcessFile(self, filename):
        return filename.endswith('.html')

    def ProcessFile(self, in_path, out_path):
        # Assuming UTF-8, else screw you.
        in_str = util.ReadFileContent(in_path)

        template = self._env.from_string(in_str)
        out_str = template.render(**self._ctx)

        util.WriteFileContent(out_path, out_str)

        return True

    def EndProcessing(self):
        del self._env
        del self._ctx


class CssYamlProcessor(_Processor):
    """Generate CSS from a YAML template."""
    def __init__(self):
        # This import will make the processor fail at instanciation
        # time if the cssyaml module is missing dependencies.
        import cssyaml

    def StartProcessing(self, ctx):
        self._ctx = ctx

    def CanProcessFile(self, filename):
        return filename.endswith('.css')

    def ProcessFile(self, in_path, out_path):
        import cssyaml

        css = cssyaml.GenerateCss(util.ReadFileContent(in_path),
                                  self._ctx['timestamp'])

        util.WriteFileContent(out_path, css)

        return True

    def EndProcessing(self):
        del self._ctx


#
# Special internal processors.
#
class IgnoreProtectedFileProcessor(_Processor):
    """Ignore temporary and hidden files."""
    def CanProcessFile(self, filename):
        base = os.path.basename(filename)
        if base.startswith('_') or base.startswith('.#') or base.endswith('~'):
            return True
        else:
            return False

    def ProcessFile(self, in_path, out_path):
        # Do nothing, effectively skipping this file.
        pass


class CopyFileProcessor(_Processor):
    """Copy any files given to it."""
    def CanProcessFile(self, filename):
        return True

    def ProcessFile(self, in_path, out_path):
        shutil.copy(in_path, out_path)
        return True


PROCESSORS = {
    'HtmlJinja': HtmlJinjaProcessor,
    'CssYaml': CssYamlProcessor,
}


def ListProcessors():
    return PROCESSORS.keys()


def GetProcessors(processors):
    processor_objs = []
    for processor in processors:
        if processor not in PROCESSORS:
            raise UnknownProcessor(processor)
        processor_objs.append(PROCESSORS[processor]())

    return ([IgnoreProtectedFileProcessor()] +
            processor_objs +
            [CopyFileProcessor()])
