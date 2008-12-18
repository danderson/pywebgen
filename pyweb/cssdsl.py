# Copyright 2008 David Anderson
#
# Redistribution of this file is permitted under
# the terms of the GNU Public License (GPL) version 2.

"""Definition of a domain-specific language for CSS generation."""

__author__ = 'David Anderson <dave@natulte.net>'

import re
import yaml
import yaml.events

import error
import odict


_CSS_HEADER = "/* Generated by pywebgen on %s. */\n"
_VARS_BLOCK_NAME = 'VARS'
_ID_FUNC_RE = re.compile(r'id\(([^\)]+)\)')
_HEX_FUNC_RE = re.compile(r'hex\(([^\)]+)\)')
_VAR_FUNC_RE = re.compile(r'(\$[^ ]+)\b')


class YamlCssError(error.Error):
    """An error occured while parsing a YAML CSS file."""


def _BuildMap(events):
    """Build an ordered dict from a yaml.events sequence describing a mapping."""
    m = odict.OrderedDict()

    for key in events:
        if isinstance(key, yaml.events.MappingEndEvent):
            return m

        # We have a key. Grab the value by advancing the iterator,
        # build it, and assign.
        if not isinstance(key, yaml.events.ScalarEvent):
            raise YamlCssError('YAML CSS mapping keys must be scalars')
        key = unicode(key.value)

        value = events.next()
        if isinstance(value, yaml.events.MappingStartEvent):
            value = _BuildMap(events)
        elif isinstance(value, yaml.events.ScalarEvent):
            value = unicode(value.value)
        else:
            raise YamlCssError('Disallowed YAML type found: %r' % value)

        m[key] = value

    # We fell off the end of the event stream. Malformed YAML CSS.
    raise YamlCssError('Truncated YAML CSS input')


def _CssYamlToDict(stream):
    """Parse a YAML CSS file to an ordered tree."""
    event_gen = yaml.parse(stream)

    # Prologue check
    if (not isinstance(event_gen.next(), yaml.events.StreamStartEvent) or
        not isinstance(event_gen.next(), yaml.events.DocumentStartEvent)):
        raise YamlCssError('Malformed document prologue')
    if not isinstance(event_gen.next(), yaml.events.MappingStartEvent):
        raise YamlCssError('The entire YAML CSS file must be a mapping')

    # Parse the entire top-level mapping
    toplevel = _BuildMap(event_gen)

    # Epilogue check
    if (not isinstance(event_gen.next(), yaml.events.DocumentEndEvent) or
        not isinstance(event_gen.next(), yaml.events.StreamEndEvent)):
        raise YamlCssError('Malformed document epilogue')

    return toplevel


def _UnescapeKey(key):
    """Unescape a YAML CSS key, substituting any id(foo) for #foo."""
    return _ID_FUNC_RE.sub(r'#\1', key)


def _GetVar(name, vars):
    """Read a variable reference from the given vars tree.

    Performs recursive resolution as needed.

    Example: _GetVar('foo.bar.baz', {'foo': {'bar': {'baz': 42}}}) -> 42
    """
    for name in name.split('.'):
        vars = vars[name]
    return vars


def _ExpandVars(value, vars):
    """Expand a YAML CSS value, substituting variable references with values.

    A variable reference is a $foo.bar.baz token, which gets looked up
    in the vars tree using _GetVar().
    """
    bits = []
    prev_start = 0
    for match in _VAR_FUNC_RE.finditer(value):
        start, end = match.span(1)
        bits.append(value[prev_start:start])

        bits.append(_GetVar(value[start+1:end], vars))

        prev_start = end

    bits.append(value[prev_start:])

    return ''.join(bits)


def _UnescapeValue(value, vars):
    """Unescape a YAML CSS value, substituting variable and hex() references."""
    value = _ExpandVars(value, vars)
    value = _HEX_FUNC_RE.sub(r'#\1', value)
    return value


def _MergeKeys(parent_str, child_str):
    """Generate a CSS selector by merging parent and child selectors.

    Example: _MergeKeys('h1, h2', 'b, i') -> ['h1 b, h1 i, h2 b, h2 i']
    """
    parents = [p.strip() for p in parent_str.split(',')]
    children = [c.strip() for c in child_str.split(',')]

    new_keys = []
    for parent in parents:
        for child in children:
            new_keys.append('%s %s' % (parent, child))

    return ', '.join(new_keys)


def _GenerateBlock(name, block_dict, vars):
    """Convert a YAML CSS dict tree into a set of CSS blocks."""
    block_defs = []
    child_blocks = []
    for k,v in block_dict.iteritems():
        if isinstance(v, odict.OrderedDict):
            child_blocks.extend(_GenerateBlock(_MergeKeys(name, k), v, vars))
        else:
            block_defs.append('  %s: %s;' % (k, _UnescapeValue(str(v), vars)))

    if block_defs:
        yield '%s {\n%s\n}\n' % (name, '\n'.join(block_defs))
    for child_block in child_blocks:
        yield child_block


def GenerateCss(in_stream, timestamp):
    """Generate a CSS string from a YAML CSS input stream."""
    data = _CssYamlToDict(in_stream)

    if _VARS_BLOCK_NAME in data:
        vars = data[_VARS_BLOCK_NAME]
        del data[_VARS_BLOCK_NAME]
    else:
        vars = {}

    blocks = [_CSS_HEADER % timestamp]
    for k,v in data.iteritems():
        blocks.extend(_GenerateBlock(_UnescapeKey(k), v, vars))

    return '\n'.join(blocks)
