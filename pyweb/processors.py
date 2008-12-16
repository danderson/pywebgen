# Copyright 2008 David Anderson
#
# Redistribution of this file is permitted under
# the terms of the GNU Public License (GPL) version 2.

"""Processors take input files and munge them in some way."""

__author__ = 'David Anderson <dave@natulte.net>'

import jinja2
import shutil


class JinjaHtmlProcessor(object):
    def CanProcessFile(self, filename):
        return filename.endswith('.html')

    def ProcessFile(self, ctx, in_path, out_path):
        # Assuming UTF-8, else screw you.
        in_str = open(in_path, 'rb').read().decode('utf-8')
        template = jinja2.Template(in_str)
        out_str = template.render(**ctx).encode('utf-8')

        f = open(out_path, 'wb')
        f.write(out_str)
        f.close()


class IgnoreProtectedFileProcessor(object):
    def CanProcessFile(self, filename):
        return filename[0] == '_'

    def ProcessFile(self, ctx, in_path, out_path):
        # Do nothing, effectively skipping this file.
        pass


class CopyFileProcessor(object):
    def CanProcessFile(self, filename):
        return True

    def ProcessFile(self, ctx, in_path, out_path):
        shutil.copy(in_path, out_path)


PROCESSORS = [IgnoreProtectedFileProcessor,
              JinjaHtmlProcessor,
              CopyFileProcessor]
