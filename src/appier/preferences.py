#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2021 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2021 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import os
import shelve
import pickle

from . import util
from . import common
from . import config
from . import redisdb
from . import component
from . import exceptions

class Preferences(component.Component):

    def __init__(self, name = "preferences", owner = None, *args, **kwargs):
        component.Component.__init__(self, name = name, owner = owner, *args, **kwargs)
        load = kwargs.pop("load", True)
        if load: self.load(*args, **kwargs)

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
        return self._get(name, default = default, strict = strict, *args, **kwargs)

    def set(self, name, value, *args, **kwargs):
        flush = kwargs.get("flush", True)
        result = self._set(name, value, *args, **kwargs)
        if flush: self.flush()
        return result

    def delete(self, name, *args, **kwargs):
        return self._delete(name, *args, **kwargs)

    def flush(self, *args, **kwargs):
        return self._flush(*args, **kwargs)

    def clear(self, *args, **kwargs):
        return self._clear(*args, **kwargs)

    def _get(self, name, default = None, strict = False, *args, **kwargs):
        raise exceptions.NotImplementedError()

    def _set(self, name, value, *args, **kwargs):
        raise exceptions.NotImplementedError()

    def _delete(self, name, *args, **kwargs):
        raise exceptions.NotImplementedError()

    def _flush(self, *args, **kwargs):
        raise exceptions.NotImplementedError()

    def _clear(self, *args, **kwargs):
        raise exceptions.NotImplementedError()

class MemoryPreferences(Preferences):

    def __init__(self, name = "memory", owner = None, *args, **kwargs):
        Preferences.__init__(self, name = name, owner = owner, *args, **kwargs)

    def _load(self, *args, **kwargs):
        Preferences._load(self, *args, **kwargs)
        self._preferences = dict()

    def _unload(self, *args, **kwargs):
        Preferences._unload(self, *args, **kwargs)
        self._preferences = None

    def _get(self, name, default = None, strict = False, *args, **kwargs):
        if strict: return self._preferences[name]
        return self._preferences.get(name, default)

    def _set(self, name, value, *args, **kwargs):
        self._preferences[name] = value

    def _delete(self, name, *args, **kwargs):
        del self._preferences[name]

    def _flush(self, *args, **kwargs):
        pass

    def _clear(self, *args, **kwargs):
        self._preferences.clear()

class FilePreferences(Preferences):

    def __init__(self, name = "file", owner = None, *args, **kwargs):
        Preferences.__init__(self, name = name, owner = owner, *args, **kwargs)

    def _load(self, *args, **kwargs):
        Preferences._load(self, *args, **kwargs)
        self.preferences_path = kwargs.pop("preferences_path", None)
        self._open()

    def _unload(self, *args, **kwargs):
        Preferences._unload(self, *args, **kwargs)
        self._close()

    def _get(self, name, default = None, strict = False, *args, **kwargs):
        if strict: return self._shelve[name]
        return self._shelve.get(name, default)

    def _set(self, name, value, *args, **kwargs):
        self._shelve[name] = value

    def _delete(self, name, *args, **kwargs):
        del self._shelve[name]

    def _flush(self, *args, **kwargs):
        self._sync()

    def _clear(self, *args, **kwargs):
        if not os.path.exists(self.preferences_path): return
        os.remove(self.preferences_path)

    def _open(self):
        self._ensure_path()
        self._shelve = shelve.open(
            self.preferences_path,
            protocol = 2,
            writeback = True
        )

    def _close(self):
        if not self._shelve: return
        self._shelve.close()
        self._shelve = None

    def _ensure_path(self):
        if self.preferences_path: return
        app_path = common.base().get_base_path()
        util.verify(not app_path == None, message = "No app path available")
        preferences_path = os.path.join(app_path, "preferences.shelve")
        preferences_path = config.conf("PREFERENCES_PATH", preferences_path)
        preferences_path = os.path.expanduser(preferences_path)
        preferences_path = os.path.abspath(preferences_path)
        preferences_path = os.path.normpath(preferences_path)
        self.preferences_path = preferences_path

    def _sync(self, secure = None):
        if secure == None:
            secure = self._db_secure()
        if secure:
            self._shelve.close()
            self._open()
        else:
            self._shelve.sync()

    def _db_secure(self):
        return self._db_type() == "dbm"

    def _db_type(self):
        shelve_cls = type(self._shelve.dict)
        shelve_dbm = shelve_cls.__name__
        return shelve_dbm

class RedisPreferences(Preferences):

    SERIALIZER = pickle
    """ The serializer to be used for the values contained in
    the preferences (used on top of the class) """

    PREFIX = "appier_preferences_"
    """The default prefix value that is going to
    be prepended to the key name to handle preferences"""

    def __init__(self, name = "redis", owner = None, *args, **kwargs):
        Preferences.__init__(self, name = name, owner = owner, *args, **kwargs)

    def _load(self, *args, **kwargs):
        Preferences._load(self, *args, **kwargs)
        self._serializer = kwargs.pop("serializer", self.__class__.SERIALIZER)
        self._prefix = kwargs.pop("prefix", self.__class__.PREFIX)
        self._prefix += self.owner.name + "_" if self.owner else ""
        self._open()

    def _unload(self, *args, **kwargs):
        Preferences._unload(self, *args, **kwargs)
        self._close()

    def _get(self, name, default = None, strict = False, *args, **kwargs):
        name = self._fqn(name)
        value = self._redis.get(name)
        if not value:
            if strict: raise KeyError("not found")
            return default
        try: return self._serializer.loads(value)
        except Exception: return default

    def _set(self, name, value, *args, **kwargs):
        name = self._fqn(name)
        value = self._serializer.dumps(value)
        self._redis.set(name, value)

    def _delete(self, name, *args, **kwargs):
        name = self._fqn(name)
        self._redis.delete(name)

    def _flush(self, *args, **kwargs):
        pass

    def _clear(self, *args, **kwargs):
        self._redis.flushdb()

    def _open(self):
        self._redis = redisdb.get_connection()
        self._redis.ping()

    def _close(self):
        self._redis = None

    def _fqn(self, name):
        return self._prefix + name
