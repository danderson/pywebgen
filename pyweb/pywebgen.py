# Copyright 2008 David Anderson
#
# Redistribution of this file is permitted under
# the terms of the GNU Public License (GPL) version 2.

"""The main pyweb executable.

This file, when executed (via the `pywebgen` stub), generates a
website by taking data out of source, optionally applying a filter,
and dropping the file in a generated output directory.
"""

__author__ = 'David Anderson <dave@natulte.net>'

import optparse
import sys

import deploy
import generator
import odict


VERSION = '0.1.0'
OPTPARSE_VERSION = '%prog ' + VERSION

def generate_cmd(cmdline):
    GENERATE_USAGE = '%prog generate [options] <input dir> <output dir>'
    parser = optparse.OptionParser(usage=GENERATE_USAGE,
                                   version=OPTPARSE_VERSION,
                                   add_help_option=False)
    parser.add_option("-m", "--manifest", action="store",
                      type="string", dest="manifest")

    (options, args) = parser.parse_args(cmdline)

    if len(args) != 2:
        parser.print_help()
        return 2

    gen = generator.Generator(args[0], ['HtmlJinja', 'CssYaml'])
    gen.Generate(args[1], manifest_path=options.manifest)
    return 0


def deploy_cmd(cmdline):
    DEPLOY_USAGE = ('%prog deploy <webgen output dir> '
                    '<deploy dir> <webgen manifest>')
    parser = optparse.OptionParser(usage=DEPLOY_USAGE,
                                   version=OPTPARSE_VERSION,
                                   add_help_option=False)
    (options, args) = parser.parse_args(cmdline)

    if len(args) != 3:
        parser.print_help()
        return 2

    deploy.Deploy(args[0], args[1], args[2])
    return 0


def undeploy_cmd(cmdline):
    UNDEPLOY_USAGE = ('%prog undeploy <webgen output dir> '
                      '<deploy dir> <webgen manifest>')
    parser = optparse.OptionParser(usage=UNDEPLOY_USAGE,
                                   version=OPTPARSE_VERSION,
                                   add_help_option=False)
    (options, args) = parser.parse_args(cmdline)

    if len(args) != 3:
        parser.print_help()
        return 2

    deploy.Undeploy(args[0], args[1], args[2])
    return 0


COMMANDS = odict.OrderedDict((
    ('generate', generate_cmd),
    ('deploy', deploy_cmd),
    ('undeploy', undeploy_cmd)))


def main():
    USAGE = ('%prog <command> [options] <command args>\n\nCommands:\n  ' +
             '\n  '.join(COMMANDS.keys()))
    parser = optparse.OptionParser(usage=USAGE, version=OPTPARSE_VERSION)
    parser.disable_interspersed_args()
    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        return 2

    if args[0] not in COMMANDS:
        print 'No such command.'
        return 2

    return COMMANDS[args[0]](args[1:])
