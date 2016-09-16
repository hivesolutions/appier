#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2016 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2016 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import time

class Cache(object):

    def __init__(self, name = "cache"):
        object.__init__(self)
        self.name = name
        self.dirty = True

    def __len__(self):
        return self.length()

    def __getitem__(self, key):
        return self.get_item(key)

    def __setitem__(self, key, value):
        return self.set_item(key, value)

    def __delitem__(self, key):
        return self.delete_item(key)

    def __contains__(self, item):
        return self.contains(item)

    def __nonzero__(self):
        return True

    def __bool__(self):
        return True

    @classmethod
    def new(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    def length(self):
        return 0

    def get(self, key, default = None):
        try: return self.get_item(key)
        except KeyError: return default

    def get_item(self, key):
        raise KeyError("not found")

    def set(self, *args, **kwargs):
        return self.set_item(*args, **kwargs)

    def set_item(self, key, value, expires = None, timeout = None):
        self.mark()

    def delete_item(self, key):
        self.mark()

    def contains(self, item):
        try: self.get_item(item)
        except KeyError: return False
        return True

    def flush(self):
        self.mark(dirty = False)

    def mark(self, dirty = True):
        self.dirty = dirty

    def build_value(self, value, expires, timeout):
        if timeout: expires = time.time() + timeout
        return (value, expires)

class MemoryCache(Cache):

    def __init__(self, name = "memory", *args, **kwargs):
        Cache.__init__(self, name = name, *args, **kwargs)
        self.data = {}

    def length(self):
        return self.data.__len__()

    def get_item(self, key):
        value, expires = self.data.__getitem__(key)
        if not expires == None and expires < time.time():
            self.__delitem__(key)
            return self.__getitem__(key)
        return value

    def set_item(self, key, value, expires = None, timeout = None):
        self.mark()
        value = self.build_value(value, expires, timeout)
        return self.data.__setitem__(key, value)

    def delete_item(self, key):
        self.mark(); return self.data.__delitem__(key)
