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

import os
import time
import shutil

from . import legacy
from . import common
from . import config
from . import redisdb
from . import component

class Cache(component.Component):

    def __init__(self, name = "cache", owner = None, *args, **kwargs):
        component.Component.__init__(self, name = name, owner = owner, *args, **kwargs)
        load = kwargs.get("load", True)
        if load: self.load()

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

    def clear(self):
        pass

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

    def contains(self, key):
        try: self.get_item(key)
        except KeyError: return False
        return True

    def build_value(self, value, expires, timeout):
        if timeout: expires = time.time() + timeout
        return (value, expires)

class MemoryCache(Cache):

    def __init__(self, name = "memory", owner = None, *args, **kwargs):
        Cache.__init__(self, name = name, owner = owner, *args, **kwargs)

    def length(self):
        return self._data.__len__()

    def clear(self):
        self._data.clear()

    def get_item(self, key):
        value, expires = self._data.__getitem__(key)
        if not expires == None and expires < time.time():
            self.delete_item(key)
            return self.get_item(key)
        return value

    def set_item(self, key, value, expires = None, timeout = None):
        value = self.build_value(value, expires, timeout)
        return self._data.__setitem__(key, value)

    def delete_item(self, key):
        return self._data.__delitem__(key)

    def _load(self, *args, **kwargs):
        Cache._load(self, *args, **kwargs)
        self._data = dict()

    def _unload(self, *args, **kwargs):
        Cache._unload(self, *args, **kwargs)
        self._data = None

class FileCache(Cache):

    def __init__(self, name = "file", owner = None, *args, **kwargs):
        Cache.__init__(self, name = name, owner = owner, *args, **kwargs)

    def length(self):
        if not os.path.exists(self.base_path): return 0
        return len(os.listdir(self.base_path))

    def clear(self):
        if not os.path.exists(self.base_path): return
        shutil.rmtree(self.base_path)

    def get_item(self, key):
        file_path = os.path.join(self.base_path, key)
        if not os.path.exists(file_path): raise KeyError("not found")
        if not os.path.exists(file_path + ".expires"): raise KeyError("not found")
        expires = self._read_file(file_path + ".expires")
        expires = int(expires) if expires else None
        if not expires == None and expires < time.time():
            self.delete_item(key)
            return self.get_item(key)
        value = self._read_file(file_path)
        return value

    def set_item(self, key, value, expires = None, timeout = None):
        file_path = os.path.join(self.base_path, key)
        value, expires = self.build_value(value, expires, timeout)
        expires = str(int(expires)) if expires else None
        expires_s = legacy.bytes(expires, force = True) if expires else b""
        self._write_file(file_path, value)
        self._write_file(file_path + ".expires", expires_s)

    def delete_item(self, key):
        file_path = os.path.join(self.base_path, key)
        os.remove(file_path)
        os.remove(file_path + ".expires")

    def _load(self, *args, **kwargs):
        Cache._load(self, *args, **kwargs)
        self.base_path = kwargs.pop("base_path", None)
        self._ensure_path()

    def _read_file(self, file_path):
        file = open(file_path, "rb")
        try: data = file.read()
        finally: file.close()
        return data

    def _write_file(self, file_path, data):
        self._ensure_exists()
        file = open(file_path, "wb")
        try: file.write(data)
        finally: file.close()

    def _ensure_exists(self):
        if os.path.exists(self.base_path): return
        os.makedirs(self.base_path)

    def _ensure_path(self):
        if self.base_path: return
        app_path = common.base().get_base_path()
        cache_path = os.path.join(app_path, "cache")
        cache_path = config.conf("CACHE_PATH", cache_path)
        cache_path = os.path.expanduser(cache_path)
        cache_path = os.path.abspath(cache_path)
        cache_path = os.path.normpath(cache_path)
        self.base_path = cache_path

class RedisCache(Cache):

    def __init__(self, name = "redis", owner = None, *args, **kwargs):
        Cache.__init__(self, name = name, owner = owner, *args, **kwargs)

    def length(self):
        keys = self._redis.keys()
        return len(keys)

    def clear(self):
        self._redis.flushdb()

    def get_item(self, key):
        if not self._redis.exists(key): raise KeyError("not found")
        return self._redis.get(key)

    def set_item(self, key, value, expires = None, timeout = None):
        if expires: timeout = expires - time.time()
        if timeout and timeout > 0: self._redis.setex(key, value, int(timeout))
        elif timeout: self._redis.delete(key)
        else: self._redis.set(key, value)

    def delete_item(self, key):
        self._redis.delete(key)

    def _load(self, *args, **kwargs):
        Cache._load(self, *args, **kwargs)
        self._redis = redisdb.get_connection()
        self._redis.ping()

    def _unload(self, *args, **kwargs):
        Cache._unload(self, *args, **kwargs)
        self._redis = None
