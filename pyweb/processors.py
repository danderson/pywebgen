# Copyright 2008 David Anderson
#
# Redistribution of this file is permitted under
# the terms of the GNU Public License (GPL) version 2.

"""Processors take input files and munge them in some way."""

__author__ = 'David Anderson <dave@natulte.net>'

import shutil

import error


class UnknownProcessor(error.Error):
    """Unknown input processor."""


class _Processor(object):
    def __init__(self, ctx):
        self.ctx = ctx


class JinjaHtmlProcessor(_Processor):
    """Generate HTML from a Jinja2 template."""
    def __init__(self, ctx):
        try:
            import jinja2
        except ImportError:
            raise error.MissingPythonModule('jinja2')

        super(JinjaHtmlProcessor, self).__init__(ctx)
        loader = jinja2.FileSystemLoader(ctx['input_root'])
        self._env = jinja2.Environment(loader=loader)

    def CanProcessFile(self, filename):
        return filename.endswith('.html')

    def ProcessFile(self, in_path, out_path):
        # Assuming UTF-8, else screw you.
        in_str = open(in_path, 'rb').read().decode('utf-8')
        template = self._env.from_string(in_str)
        out_str = template.render(**self.ctx).encode('utf-8')

        f = open(out_path, 'wb')
        f.write(out_str)
        f.close()


class YamlCssProcessor(_Processor):
    """Generate CSS from a YAML template."""
    def CanProcessFile(self, filename):
        return filename.endswith('.css')

    def ProcessFile(self, in_path, out_path):
        import cssyaml

        css = cssyaml.GenerateCss(open(in_path, 'rb').read().decode('utf-8'),
                                  self.ctx['timestamp'])

        f = open(out_path, 'wb')
        f.write(css)
        f.close()


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
    'HtmlJinja': JinjaHtmlProcessor,
    'CssYaml': YamlCssProcessor,
}


def ListProcessors():
    return PROCESSORS.keys()


def GetProcessors(processors, ctx):
    processor_classes = []
    for processor in processors:
        if processor not in PROCESSORS:
            raise UnknownProcessor(processor)
        processor_classes.append(PROCESSORS[processor](ctx))

    return ([IgnoreProtectedFileProcessor] +
            processor_classes +
            [CopyFileProcessor])
