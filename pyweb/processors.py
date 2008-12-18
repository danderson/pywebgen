# Copyright 2008 David Anderson
#
# Redistribution of this file is permitted under
# the terms of the GNU Public License (GPL) version 2.

"""Processors take input files and munge them into an output file."""

__author__ = 'David Anderson <dave@natulte.net>'

import shutil

import error
import util


class UnknownProcessor(error.Error):
    """Unknown input processor."""


class _Processor(object):
    """Base class for file processors."""
    def __init__(self, ctx):
        self.ctx = ctx

    def CanProcessFile(self, filename):
        raise NotImplementedError()

    def ProcessFile(self, in_path, out_path):
        raise NotImplementedError()


#
# General processors
#
class HtmlJinjaProcessor(_Processor):
    """Generate HTML from a Jinja2 template."""
    def __init__(self, ctx):
        try:
            import jinja2
        except ImportError:
            raise error.MissingPythonModule('jinja2')

        super(HtmlJinjaProcessor, self).__init__(ctx)
        loader = jinja2.FileSystemLoader(ctx['input_root'])
        self._env = jinja2.Environment(loader=loader)

    def CanProcessFile(self, filename):
        return filename.endswith('.html')

    def ProcessFile(self, in_path, out_path):
        # Assuming UTF-8, else screw you.
        in_str = util.ReadFileContent(in_path)

        template = self._env.from_string(in_str)
        out_str = template.render(**self.ctx)

        util.WriteFileContent(out_path, out_str)


class CssYamlProcessor(_Processor):
    """Generate CSS from a YAML template."""
    def __init__(self, ctx):
        super(CssYamlProcessor, self).__init__(ctx)

        # This import will make the processor fail at instanciation
        # time if the cssyaml module is missing dependencies.
        import cssyaml

    def CanProcessFile(self, filename):
        return filename.endswith('.css')

    def ProcessFile(self, in_path, out_path):
        import cssyaml

        css = cssyaml.GenerateCss(util.ReadFileContent(in_path),
                                  self.ctx['timestamp'])

        util.WriteFileContent(out_path, css)


#
# Special internal processors.
#
class IgnoreProtectedFileProcessor(object):
    """Ignore temporary and hidden files."""
    @staticmethod
    def CanProcessFile(filename):
        return filename[0] == '_' or filename[-1] == '~'

    @staticmethod
    def ProcessFile(in_path, out_path):
        # Do nothing, effectively skipping this file.
        pass


class CopyFileProcessor(object):
    """Copy any files given to it."""
    @staticmethod
    def CanProcessFile(filename):
        return True

    @staticmethod
    def ProcessFile(in_path, out_path):
        shutil.copy(in_path, out_path)


PROCESSORS = {
    'HtmlJinja': HtmlJinjaProcessor,
    'CssYaml': CssYamlProcessor,
}


def ListProcessors():
    return PROCESSORS.keys()


def GetProcessors(processors, ctx):
    processor_objs = []
    for processor in processors:
        if processor not in PROCESSORS:
            raise UnknownProcessor(processor)
        processor_objs.append(PROCESSORS[processor](ctx))

    return ([IgnoreProtectedFileProcessor] +
            processor_objs +
            [CopyFileProcessor])
