# Copyright 2008 David Anderson
#
# Redistribution of this file is permitted under
# the terms of the GNU Public License (GPL) version 2.

"""Container management overlay for the versionned overlay.

versions.py lets you manage several versions of a website, with
automatic deployment to external directories and such. But the
commandlines are starting to get a little cumbersome. This module
provides a "container" model, where you have in a single directory the
source subdir, a versions subdir, and a script that provides DRY
management and deployment.
"""

__author__ = 'David Anderson <dave@natulte.net>'

import os
import os.path
import shutil
import stat

import util
import versions


_SOURCE_DIR = 'source'
_VERSIONS_DIR = 'versions'
_DEPLOY_DIR = 'deploy'
_CURRENT_DIR = 'current'
_LATEST_DIR = 'latest'

_CONTAINER_SCRIPT_NAME = 'pwg'
_CONTAINER_SCRIPT = '''#!/usr/bin/env python
# Copyright 2008 David Anderson
#
# Redistribution of this file is permitted under
# the terms of the GNU Public License (GPL) version 2.

import sys
from pyweb.container_main import main

sys.exit(main())
'''


def _CopyModule(module, out):
    module_path = module.__file__
    if module_path.endswith('.pyc'):
        module_path = module_path[:-1]
    if module_path.endswith('__init__.py'):
        module_path = os.path.dirname(module_path)

    print module_path

    util.CreateDir(os.path.dirname(out))

    if os.path.isdir(module_path):
        shutil.copytree(module_path, out)
        for root, dirs, files in os.walk(out):
            for f in files:
                if f.endswith('.pyc') or f.endswith('~'):
                    os.remove(os.path.join(root, f))
    else:
        shutil.copy(module_path, out)


class Container(object):
    def __init__(self, root_path):
        self.root = os.path.abspath(root_path)

        self.source_dir = self._PathInRoot(_SOURCE_DIR)
        self.versions_dir = self._PathInRoot(_VERSIONS_DIR)
        self.deploy_dir = self._PathInRoot(_DEPLOY_DIR)
        self.current_dir = self._PathInRoot(_CURRENT_DIR)
        self.latest_dir = self._PathInRoot(_LATEST_DIR)

        if not os.path.exists(self.deploy_dir):
            self.deploy_dir = None

        self._versions = versions.VersionnedGenerator(self.versions_dir,
                                                      self.deploy_dir)

    def _PathInRoot(self, path):
        return os.path.join(self.root, path)

    def Generate(self):
        ret = self._versions.Generate(self.source_dir,
                                      ['HtmlJinja', 'CssYaml'])
        return ret[0], ret[3]

    def Versions(self):
        return self._versions.Versions()

    def SetCurrent(self, version):
        return self._versions.ChangeCurrent(version)

    def Gc(self):
        return self._versions.GarbageCollect()

    @classmethod
    def Create(cls, root_path, deploy_dir=None, embed_pyweb=False):
        root_path = os.path.abspath(root_path)
        if deploy_dir:
            deploy_dir = os.path.abspath(deploy_dir)

        util.CreateDir(root_path)

        c = cls(root_path)
        util.CreateDir(c.source_dir)
        util.CreateDir(c.versions_dir)
        if deploy_dir:
            os.symlink(deploy_dir, c.deploy_dir)
        os.symlink(os.path.join(c.versions_dir, 'current'), c.current_dir)
        os.symlink(os.path.join(c.versions_dir, 'latest'), c.latest_dir)

        util.WriteFileContent(c._PathInRoot(_CONTAINER_SCRIPT_NAME),
                              _CONTAINER_SCRIPT)
        os.chmod(c._PathInRoot(_CONTAINER_SCRIPT_NAME),
                 stat.S_IRWXU | stat.S_IRWXG)

        if embed_pyweb:
            import pyweb
            _CopyModule(pyweb, c._PathInRoot('pyweb'))

        # Build a new container now that everything is in place, and
        # use it to bootstrap versionning and deployment.
        c = cls(root_path)
        c.Generate()
