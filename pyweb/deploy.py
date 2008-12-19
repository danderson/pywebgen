# Copyright 2008 David Anderson
#
# Redistribution of this file is permitted under
# the terms of the GNU Public License (GPL) version 2.

"""Website deployment functions.

Once a website is generated, it is common to want to deploy the
generated files in a directory tree that contains other non-generated
files.

This module assists in that task. Given a generated-only output tree
and a manifest describing it, the generated files can be deployed or
undeployed to/from a mixed origin directory tree.
"""

__author__ = 'David Anderson <dave@natulte.net>'

import os
import os.path
import shutil

import error
import util


def _ManifestFileIterator(in_root, out_root, manifest_file):
    in_root = os.path.abspath(in_root)
    out_root = os.path.abspath(out_root)
    manifest = util.ReadFileContent(manifest_file)

    for file in (f for f in manifest.splitlines() if f.strip()):
        in_file = os.path.join(in_root, file)
        out_file = os.path.join(out_root, file)
        yield in_file, out_file


def Deploy(in_root, out_root, manifest_file):
    for in_file, out_file in _ManifestFileIterator(in_root, out_root,
                                                   manifest_file):
        if in_file == out_file:
            continue

        if os.path.isdir(in_file):
            util.CreateDir(out_file)
        else:
            shutil.copy(in_file, out_file)


def Undeploy(in_root, out_root, manifest_file):
    for in_file, out_file in _ManifestFileIterator(in_root, out_root,
                                                   manifest_file):
        if in_file == out_file:
            continue

        if os.path.isdir(in_file):
            # Only delete an output directory if it's still a
            # directory, and it's empty.
            if os.path.isdir(out_file) and not os.listdir(out_file):
                os.rmdir(out_file)
        else:
            # Only delete if it's still a file.
            if os.path.isfile(out_file):
                os.remove(out_file)
