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

import redisdb

from . import component
from . import exceptions

class Bus(component.Component):

    def __init__(self, name = "bus", owner = None, *args, **kwargs):
        component.Component.__init__(self, name = name, owner = owner, *args, **kwargs)
        load = kwargs.get("load", True)
        if load: self.load()

    @classmethod
    def new(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    def bind(self, name, method, *args, **kwargs):
        raise exceptions.NotImplementedError()

    def unbind(self, name, *args, **kwargs):
        raise exceptions.NotImplementedError()

    def trigger(self, name, *args, **kwargs):
        raise exceptions.NotImplementedError()

class MemoryBus(Bus):

    def bind(self, name, method, *args, **kwargs):
        methods = self._events.get(name, [])
        methods.append(method)
        self._events[name] = methods

    def unbind(self, name, *args, **kwargs):
        method = kwargs.get("method", None)
        methods = self._events.get(name, [])
        if method: methods.remove(method)
        else: del methods[:]

    def trigger(self, name, *args, **kwargs):
        methods = self._events.get(name, [])
        for method in methods: method(*args, **kwargs)

    def _load(self, *args, **kwargs):
        Bus._load(self, *args, **kwargs)
        self._events = dict()

    def _unload(self, *args, **kwargs):
        Bus._unload(self, *args, **kwargs)
        self._events = None

class RedisBus(Bus):

    def trigger(self, name, *args, **kwargs):
        self._redis.publish(name, *args, **kwargs)

    def _load(self, *args, **kwargs):
        Bus._load(self, *args, **kwargs)
        self._open()

    def _unload(self, *args, **kwargs):
        Bus._unload(self, *args, **kwargs)
        self._close()

    def _open(self):
        self._redis = redisdb.get_connection()
        self._pubsub = self._redis.pubsub()
        self._redis.ping()

    def _close(self):
        self._redis = None
