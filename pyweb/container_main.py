# Copyright 2008 David Anderson
#
# Redistribution of this file is permitted under
# the terms of the GNU Public License (GPL) version 2.

import optparse
import os.path
import sys

import pyweb.container
import pyweb.devserver
import pyweb.pywebgen

USAGE = '''%prog command args...

Commands:
  generate
    Generate a new version of the website.

  versions
    Output a list of available versions.
    Also indicates which one is current.

  setcurrent <version num or 'latest'>
    Set the current version. Will automatically redeploy as needed.

  gc
    Garbage collect all website versions older than 'current'.

  devel
    Run a development webserver on localhost:8000
'''


def _MakeEnv():
    env_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    return pyweb.container.Container(env_dir)


def GenerateCmd(_):
    ts, current = _MakeEnv().Generate()

    print 'Generated version %s' % ts
    if current:
        print 'This version is now the current version.'

    return 0


def VersionsCmd(_):
    versions, current = _MakeEnv().Versions()

    if not versions:
        print 'No website versions.'
        return 0

    print 'Versions:'
    for i, ts in enumerate(versions):
        if ts == current:
            print '  %2d. %s (current)' % (i, ts)
        else:
            print '  %2d. %s' % (i, ts)

    return 0


def SetCurrentCmd(args):
    if len(args) != 1:
        print "A version (numeric or 'latest') is required."
        return 2

    if args[0] == 'latest':
        version = 0
    else:
        try:
            version = int(args[0])
        except ValueError:
            print 'Invalid version specified.'
            return 2

    ts = _MakeEnv().SetCurrent(version)
    print 'Set current version to %s.' % ts

    return 0

def GcCmd(_):
    versions = _MakeEnv().Gc()

    if not versions:
        print 'Nothing to garbage collect.'
    else:
        print 'Garbage collected %d versions:' % len(versions)
        print '\n'.join(['  %s' % v for v in versions])

    return 0


def DevCmd(_):
    e = _MakeEnv()
    print 'Listening on http://localhost:8000/'
    pyweb.devserver.RunDevServer(
        ('127.0.0.1', 8000), e.source_dir, e.devel_dir)
    print 'Shutting down.'


_COMMANDS = {
    'generate': GenerateCmd,
    'versions': VersionsCmd,
    'setcurrent': SetCurrentCmd,
    'gc': GcCmd,
    'dev': DevCmd
}

def main():
    parser = optparse.OptionParser(usage=USAGE,
                                   version=pyweb.pywebgen.OPTPARSE_VERSION)
    (_, args) = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        return 2

    if args[0] not in _COMMANDS:
        print 'Unknown command %s.' % args[0]
        parser.print_help()
        return 2

    return _COMMANDS[args[0]](args[1:])
