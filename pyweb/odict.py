# Copyright 2008 David Anderson
#
# Redistribution of this file is permitted under
# the terms of the GNU Public License (GPL) version 2.

"""Ordered dictionary implementation.

This type fully emulates the dict interface, but iterators yield
keys/values in insertion order, as opposed to undefined order.
"""

__author__ = 'David Anderson <dave@natulte.net>'


import UserDict


class OrderedDict(UserDict.DictMixin):
    def __init__(self, sequence=[]):
        self._dict = {}
        self._keys = []
        for k,v in sequence:
            self[k] = v

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, value):
        if not key in self._dict:
            self._keys.append(key)
        self._dict[key] = value

    def __delitem__(self, key):
        if key in self._dict:
            del self._dict[key]
            self._keys.remove(key)

    def __contains__(self, key):
        return key in self._dict

    def keys(self):
        return self._keys[:]

    def __iter__(self):
        for k in self._keys:
            yield k

    def iteritems(self):
        for k in self._keys:
            yield k, self._dict[k]

    def __len__(self):
        return len(self._dict)
