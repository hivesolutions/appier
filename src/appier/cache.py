#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2015 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2015 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

class Cache(object):

    def __init__(self, name = "cache"):
        object.__init__(self)
        self.dirty = True

    def __len__(self):
        return 0

    def __getitem__(self, key):
        raise KeyError("not found")

    def __setitem__(self, key, value):
        self.mark()

    def __delitem__(self, key):
        self.mark()

    def __contains__(self, item):
        return False

    def __nonzero__(self):
        return True

    def __bool__(self):
        return True

    @classmethod
    def new(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    def flush(self):
        self.mark(dirty = False)

    def mark(self, dirty = True):
        self.dirty = dirty

class MemoryCache(Cache):

    def __init__(self, name = "session", *args, **kwargs):
        Cache.__init__(self, name = name, *args, **kwargs)
        self.data = {}

    def __len__(self):
        return self.data.__len__()

    def __getitem__(self, key):
        return self.data.__getitem__(key)

    def __setitem__(self, key, value):
        self.mark(); return self.data.__setitem__(key, value)

    def __delitem__(self, key):
        self.mark(); return self.data.__delitem__(key)

    def __contains__(self, item):
        return self.data.__contains__(item)
