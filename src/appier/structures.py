#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2019 Hive Solutions Lda.
#
# This file is part of Hive Appier Framework.
#
# Hive Appier Framework is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Appier Framework is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Appier Framework. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2019 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import os

class OrderedDict(dict):

    def __init__(self, value = None, *args, **kwargs):
        object.__init__(self, *args, **kwargs)
        self._list = list()
        self._dict = dict()
        self._items = dict()
        is_dict = isinstance(value, dict)
        if not is_dict: return
        self._from_dict(value)

    def __str__(self):
        self._verify()
        return self._list.__str__()

    def __unicode__(self):
        self._verify()
        return self._list.__unicode__()

    def __repr__(self):
        self._verify()
        return self._list.__repr__()

    def __len__(self):
        self._verify()
        return self._dict.__len__()

    def __getitem__(self, key):
        self._verify()
        return self._dict.__getitem__(key)

    def __setitem__(self, key, value):
        self._verify()
        return self.set(key, value)

    def __delitem__(self, key):
        self._verify()
        return self.delete(key)

    def __contains__(self, item):
        self._verify()
        return self._dict.__contains__(item)

    def __iter__(self, verify = True):
        self._verify(force = verify)
        return self._list.__iter__()

    def items(self, verify = True):
        self._verify(force = verify)
        return self

    def iteritems(self, verify = True):
        self._verify(force = verify)
        return self

    def item(self, key):
        self._verify()
        return self._items.__getitem__(key)

    def sort(self, *args, **kwargs):
        self._verify()
        return self._list.sort(*args, **kwargs)

    def append(self, value):
        self._verify()
        return self.push(value)

    def pop(self, index = -1):
        self._verify()
        value = self._list.pop(index)
        key, _value = value
        del self._dict[key]
        del self._items[key]
        return value

    def push(self, value):
        self._verify()
        key, value = value
        self.set(key, value)

    def get(self, key, default = None):
        self._verify()
        if not key in self._dict: return default
        return self._dict[key]

    def set(self, key, value):
        self._verify()
        if key in self:
            item = self.item(key)
            item[1] = value
        else:
            item = [key, value]
            self._list.append(item)
        self._dict[key] = value
        self._items[key] = item

    def delete(self, key):
        self._verify()
        value = self.__getitem__(key)
        self._list.remove([key, value])
        del self._dict[key]
        del self._items[key]

    def empty(self):
        del self._list[:]
        self._dict.clear()
        self._items.clear()

    def _from_dict(self, base, empty = True):
        """
        Builds the ordered dictionary from a base (unordered) one
        sorting all of its items accordingly.

        Notice that the reference to the base dictionary object
        is kept untouched so that any change in this dict implies
        also a change in the underlying base dictionary.

        :type base: Dictionary
        :param base: The base dictionary to be used in the construction
        of this ordered one.
        :type clear: bool
        :param empty: If the current structure should be cleared
        to an empty state before using the dictionary.
        """

        if empty: self.empty()
        keys = list(base.keys())
        keys.sort()
        for key in keys:
            value = base[key]
            self.set(key, value)
        if empty: self._dict = base

    def _verify(self, force = False):
        """
        Runs the consistency check on the current structure so that
        if any change occurs in the base dictionary (either adding
        or removal) it gets reflected on the current ordered one.

        This method should be as efficient as possible as it's going
        to run on every single iteration process.

        :type force: bool
        :param force: Flag that control if the verification process
        should be executed if if the length of the structures is
        exactly the same.
        """

        if not force and len(self._list) == len(self._dict): return

        for value in list(self._list):
            key, _value = value
            exists = True
            exists &= key in self._dict
            exists &= key in self._items
            if exists: continue
            self._list.remove(value)

        if len(self._list) == len(self._dict): return

        for key, value in self._dict.items():
            item = [key, value]
            if item in self._list: continue
            self._list.append(item)
            self._items[key] = item

class LazyDict(dict):

    def __getitem__(self, key, force = False, resolve = False):
        value = dict.__getitem__(self, key)
        if force: return value
        if not isinstance(value, LazyValue): return value
        return value.resolve(force = resolve)

    def resolve(self, force = False):
        result = dict()
        for key in self:
            value = self.__getitem__(key, resolve = force)
            result[key] = value
        return result

    def to_dict(self, force = True):
        return self.resolve(force = force)

class LazyValue(object):

    def __init__(self, callable):
        self.callable = callable

    def __call__(self):
        return self.call()

    def resolve(self, force = False):
        if hasattr(self, "_value") and not force:
            return self._value
        self._value = self.callable()
        return self._value

    def call(self):
        return self.resolve()

class GeneratorFile(object):
    """
    File like class that encapsulates an underlying
    stream generator (first yield is size) into a
    file, to be used as a normal file.

    Notice that there are certain limitation to this
    strategy like the fact that the read operation
    (chunk) size parameter is not respected.
    """

    def __init__(self, generator):
        self._generator = generator
        self._size = next(generator)
        self._position = 0

    def seek(self, offset, whence = os.SEEK_SET):
        if whence == os.SEEK_SET:
            self._position = offset
        if whence == os.SEEK_CUR:
            self._position += offset
        if whence == os.SEEK_END:
            self._position = self._size + offset

    def tell(self):
        return self._position

    def read(self, size):
        try: data = next(self._generator)
        except StopIteration: data = b""
        return data

    def close(self):
        self._generator.close()

lazy_dict = LazyDict
lazy = LazyValue
