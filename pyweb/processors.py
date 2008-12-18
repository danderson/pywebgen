# Copyright 2008 David Anderson
#
# Redistribution of this file is permitted under
# the terms of the GNU Public License (GPL) version 2.

"""Processors take input files and munge them in some way."""

__author__ = 'David Anderson <dave@natulte.net>'

import jinja2
import shutil

import cssdsl


class _Processor(object):
    def __init__(self, ctx):
        self.ctx = ctx


class JinjaHtmlProcessor(_Processor):
    def __init__(self, ctx):
        super(JinjaHtmlProcessor, self).__init__(ctx)
        loader = jinja2.FileSystemLoader(ctx['in_root'])
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
    def CanProcessFile(self, filename):
        return filename.endswith('.css')

    def ProcessFile(self, in_path, out_path):
        css = cssdsl.GenerateCss(open(in_path, 'rb').read().decode('utf-8'),
                                 self.ctx['timestamp_str'])

        f = open(out_path, 'wb')
        f.write(css)
        f.close()


class IgnoreProtectedFileProcessor(_Processor):
    def CanProcessFile(self, filename):
        return filename[0] == '_' or filename[-1] == '~'

    def ProcessFile(self, in_path, out_path):
        # Do nothing, effectively skipping this file.
        pass


class CopyFileProcessor(_Processor):
    def CanProcessFile(self, filename):
        return True

    def ProcessFile(self, in_path, out_path):
        shutil.copy(in_path, out_path)


PROCESSORS = [IgnoreProtectedFileProcessor,
              JinjaHtmlProcessor,
              YamlCssProcessor,
              CopyFileProcessor]
