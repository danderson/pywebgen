# Copyright 2008 David Anderson
#
# Redistribution of this file is permitted under
# the terms of the GNU Public License (GPL) version 2.

"""Website development server."""

__author__ = 'David Anderson <dave@natulte.net>'


import os
import os.path
import BaseHTTPServer
import SimpleHTTPServer
import shutil
import time

import generator


REFRESH_INTERVAL = 2


class DevHTTPRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_HEAD(self):
        self.RefreshSite()
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_HEAD(self)

    def do_GET(self):
        self.RefreshSite()
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

    def RefreshSite(self):
        if self.server.RefreshSite():
            print 'Regenerated website'


class DevHTTPServer(BaseHTTPServer.HTTPServer):
    def __init__(self, address, in_dir, out_dir):
        BaseHTTPServer.HTTPServer.__init__(self, address, DevHTTPRequestHandler)

        self._out_dir = os.path.abspath(out_dir)
        in_dir = os.path.abspath(in_dir)
        self._generator = generator.Generator(in_dir, ['HtmlJinja', 'CssYaml'])
        self._last_generation = 0
        self._previous_cwd = os.getcwd()
        self.RefreshSite()

    def RefreshSite(self):
        t = time.time()
        if (t - self._last_generation) < REFRESH_INTERVAL:
            return False

        self._last_generation = t
        self.CleanupSite()
        self._generator.Generate(self._out_dir)
        os.chdir(self._out_dir)
        return True

    def CleanupSite(self):
        if os.path.isdir(self._out_dir):
            shutil.rmtree(self._out_dir)


def RunDevServer(address, in_dir, out_dir):
    try:
        s = DevHTTPServer(address, in_dir, out_dir)
        s.serve_forever()
    except KeyboardInterrupt:
        print
        s.CleanupSite()
