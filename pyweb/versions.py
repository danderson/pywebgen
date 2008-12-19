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
import time

import error
import generator
import util


_TS_RE_FORM = r'(\d{8}-\d{6})'
_TS_RE = re.compile(_TS_RE_FORM)
_MANIFEST_RE = re.compile(_TS_RE_FORM + r'\.MANIFEST')


class InvalidCurrentLinkError(error.Error):
    """The 'current' symlink is not valid."""


class NoVersionsError(error.Error):
    """No website versions exist."""


class VersionnedGenerator(object):
    def __init__(self, output_root):
        self._output_root = os.path.abspath(output_root)
        self._current_link = os.path.join(self._output_root, 'current')
        util.CreateDir(self._output_root)

    def _FindTimestamps(self):
        timestamps = []
        for filename in os.listdir(self._output_root):
            match = _MANIFEST_RE.match(filename)
            if match:
                timestamps.append(match.group(1))
        timestamps.sort(reverse=True)
        return timestamps

    def _CurrentTimestamp(self):
        if not self._CurrentExists():
            return None

        # Resolve the symlink and grab the timestamp
        #
        # TODO(dave): Detect if the symlink points outside the output
        # dir, which would be an invalid symlink.
        pointed_path = os.path.realpath(self._current_link)
        pointed_ts = os.path.basename(pointed_path)
        if not _TS_RE.match(pointed_ts):
            raise InvalidCurrentLinkError(self._current_link)
        return pointed_ts

    def _CurrentExists(self):
        if not os.path.exists(self._current_link):
            return False
        elif not os.path.islink(self._current_link):
            raise InvalidCurrentLinkError(self._current_link)
        return True

    def _SetCurrent(self, ts):
        if self._CurrentExists():
            os.remove(self._current_link)

        os.symlink(os.path.join(self._output_root, ts),
                   self._current_link)

    def Generate(self, input_root, use_processors):
        ts = time.localtime()
        ts_str = time.strftime('%Y%m%d-%H%M%S', ts)
        out_dir = os.path.join(self._output_root, ts_str)
        manifest_file = os.path.join(self._output_root, '%s.MANIFEST' % ts_str)

        generator.Generator(input_root, use_processors).Generate(
            out_dir, timestamp=ts, manifest_path=manifest_file)

        if not self._CurrentExists():
            self._SetCurrent(ts_str)
            current = True
        else:
            current = False

        return ts_str, out_dir, manifest_file, current

    def Versions(self):
        ts = self._FindTimestamps()
        current = self._CurrentTimestamp()
        return ts, current

    def ChangeCurrent(self, version=0):
        ts = self._FindTimestamps()
        if not ts:
            raise NoVersionsError()
        if version >= len(ts):
            raise ArgumentError('Invalid version %d specified, '
                                'only %d available' % (version, len(ts)))

        current = self._CurrentTimestamp()

        if current and current == ts[version]:
            # Nothing to do, we're current already.
            return

        # (re)point the symlink
        self._SetCurrent(ts[version])

        return ts[version]
