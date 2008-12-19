# Copyright 2008 David Anderson
#
# Redistribution of this file is permitted under
# the terms of the GNU Public License (GPL) version 2.

"""Version management overlay for the basic website generator.

generator.py provides a simple one-shot website generator. However,
ideally we'd like to be able to keep at least 2 versions of the
website at all times, and switch the "live" version atomically, after
generation has completed.

This module provides that support, by controlling the base generator
to generate timestamped instances of a website, and manages a
"current" symlink that can be atomically repointed between these
versions.
"""

__author__ = 'David Anderson <dave@natulte.net>'

import os
import os.path
import re
import shutil
import time

import deploy
import error
import generator
import util


_TS_RE_FORM = r'(\d{8}-\d{6})'
_TS_RE = re.compile(_TS_RE_FORM)
_MANIFEST_RE = re.compile(_TS_RE_FORM + r'\.MANIFEST')


# The name of the various symlinks we maintain.
_CURRENT_LINK = 'current'
_LATEST_LINK = 'latest'


class InvalidLinkError(error.Error):
    """Version symlink is not valid."""


class NoVersionsError(error.Error):
    """No website versions exist."""


class VersionnedGenerator(object):
    def __init__(self, output_root, deploy_dir=None):
        self._output_root = os.path.abspath(output_root)
        self._deploy_dir = os.path.abspath(deploy_dir)
        util.CreateDir(self._output_root)

    def _FindTimestamps(self):
        timestamps = []
        for filename in os.listdir(self._output_root):
            match = _MANIFEST_RE.match(filename)
            if match:
                timestamps.append(match.group(1))
        timestamps.sort(reverse=True)
        return timestamps

    def _SiteLocation(self, ts):
        return os.path.join(self._output_root, ts)

    def _ManifestLocation(self, ts):
        return os.path.join(self._output_root, '%s.MANIFEST' % ts)

    def _LinkLocation(self, link):
        return os.path.join(self._output_root, link)

    def _LinkTimestamp(self, link):
        if not self._LinkExists(link):
            return None

        # Resolve the symlink and grab the timestamp
        #
        # TODO(dave): Detect if the symlink points outside the output
        # dir, which would be an invalid symlink.
        pointed_path = os.path.realpath(self._LinkLocation(link))
        pointed_ts = os.path.basename(pointed_path)
        if not _TS_RE.match(pointed_ts):
            raise InvalidLinkError(link)
        return pointed_ts

    def _LinkExists(self, link):
        link_path = self._LinkLocation(link)
        if not os.path.exists(link_path):
            return False
        elif not os.path.islink(link_path) or not os.path.exists(link_path):
            raise InvalidLinkError(link)
        return True

    def _SetLink(self, link, ts):
        link_path = self._LinkLocation(link)
        if self._LinkExists(link):
            os.remove(link_path)

        os.symlink(os.path.join(self._output_root, ts), link_path)

    def Generate(self, input_root, use_processors):
        ts = time.localtime()
        ts_str = time.strftime('%Y%m%d-%H%M%S', ts)
        out_dir = self._SiteLocation(ts_str)
        manifest_file = self._ManifestLocation(ts_str)

        generator.Generator(input_root, use_processors).Generate(
            out_dir, timestamp=ts, manifest_path=manifest_file)

        self._SetLink(_LATEST_LINK, ts_str)

        if not self._LinkExists(_CURRENT_LINK):
            self._SetLink(_CURRENT_LINK, ts_str)
            if self._deploy_dir:
                deploy.Deploy(out_dir, self._deploy_dir, manifest_file)
            current = True
        else:
            current = False

        return ts_str, out_dir, manifest_file, current

    def Versions(self):
        ts = self._FindTimestamps()
        current = self._LinkTimestamp(_CURRENT_LINK)
        return ts, current

    def ChangeCurrent(self, version=0):
        ts = self._FindTimestamps()
        if not ts:
            raise NoVersionsError()
        if version >= len(ts):
            raise ArgumentError('Invalid version %d specified, '
                                'only %d available' % (version, len(ts)))

        current = self._LinkTimestamp(_CURRENT_LINK)

        if current and current == ts[version]:
            # Nothing to do, we're current already.
            return

        # (re)point the symlink
        if self._deploy_dir:
            deploy.Undeploy(self._SiteLocation(current),
                            self._deploy_dir,
                            self._ManifestLocation(current))
        self._SetLink(_CURRENT_LINK, ts[version])
        if self._deploy_dir:
            deploy.Deploy(self._SiteLocation(ts[version]),
                          self._deploy_dir,
                          self._ManifestLocation(ts[version]))

        return ts[version]

    def GarbageCollect(self):
        ts = self._FindTimestamps()
        current = self._LinkTimestamp(_CURRENT_LINK)

        # If there is no current pointer, we don't know what to GC.
        if not current:
            return []

        to_gc = ts[ts.index(current)+1:]
        for version in to_gc:
            os.remove(os.path.join(self._output_root, '%s.MANIFEST' % version))
            shutil.rmtree(os.path.join(self._output_root, version))

        return to_gc
