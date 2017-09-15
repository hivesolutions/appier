#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2017 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2017 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

from . import exceptions

class Preferences(object):

    def __init__(self, owner = None):
        object.__init__(self)
        self.owner = owner

    def __getitem__(self, key):
        return self.get(key, strict = True)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __delitem__(self, key):
        self.delete(key)

    @classmethod
    def new(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    def get(self, name, default = None, strict = False, *args, **kwargs):
        raise exceptions.NotImplementedError()

    def set(self, name, value, *args, **kwargs):
        raise exceptions.NotImplementedError()

    def delete(self, name, *args, **kwargs):
        raise exceptions.NotImplementedError()

    def flush(self, *args, **kwargs):
        raise exceptions.NotImplementedError()

    def clear(self, *args, **kwargs):
        raise exceptions.NotImplementedError()

class MemoryPreferences(Preferences):

    def __init__(self, owner = None):
        Preferences.__init__(self, owner = owner)
        self._preferences = dict()

    def get(self, name, default = None, strict = False, *args, **kwargs):
        if strict: return self._preferences[name]
        return self._preferences.get(name, default)

    def set(self, name, value, *args, **kwargs):
        self._preferences[name] = value

    def delete(self, name, *args, **kwargs):
        del self._preferences[name]

    def flush(self, *args, **kwargs):
        pass

    def clear(self, *args, **kwargs):
        self._preferences.clear()

class FilePreferences(Preferences):
    pass

class RedisPreferences(Preferences):
    pass
