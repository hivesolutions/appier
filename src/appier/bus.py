#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2018 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2018 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import pickle
import threading

from . import config
from . import legacy
from . import redisdb
from . import component
from . import exceptions

class Bus(component.Component):

    def __init__(self, name = "bus", owner = None, *args, **kwargs):
        component.Component.__init__(self, name = name, owner = owner, *args, **kwargs)
        load = kwargs.pop("load", True)
        if load: self.load(*args, **kwargs)

    @classmethod
    def new(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    def bind(self, name, method):
        raise exceptions.NotImplementedError()

    def unbind(self, name, method = None):
        raise exceptions.NotImplementedError()

    def trigger(self, name, *args, **kwargs):
        raise exceptions.NotImplementedError()

class MemoryBus(Bus):

    def bind(self, name, method):
        methods = self._events.get(name, [])
        methods.append(method)
        self._events[name] = methods

    def unbind(self, name, method = None):
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

    def _get_state(self):
        state = Bus._get_state(self)
        state.update(_events = self._events)
        return state

    def _set_state(self, state):
        Bus._set_state(self, state)
        _events = state.get("_events", {})
        for name, methods in legacy.iteritems(_events):
            for method in methods:
                self.bind(name, method)

class RedisBus(Bus):

    SERIALIZER = pickle
    """ The serializer to be used for the values contained in
    the bus (used on top of the class) """

    GLOBAL_CHANNEL = "global"
    """ The name of the global channel to which all of the agents
    should be subscribed, for global communication """

    def bind(self, name, method):
        methods = self._events.get(name, [])
        methods.append(method)
        self._events[name] = methods
        channel = self._to_channel(name)
        self._pubsub.subscribe(channel)

    def unbind(self, name, method = None):
        methods = self._events.get(name, [])
        if method: methods.remove(method)
        else: del methods[:]
        channel = self._to_channel(name)
        self._pubsub.unsubscribe(channel)

    def trigger(self, name, *args, **kwargs):
        channel = self._to_channel(name)
        data = self._serializer.dumps(dict(
            args = args,
            kwargs = kwargs
        ))
        self._redis.publish(channel, data)

    def _load(self, *args, **kwargs):
        Bus._load(self, *args, **kwargs)
        self._name = config.conf("BUS_NAME", self.owner.name_i)
        self._name = config.conf("BUS_SCOPE", self._name)
        self._name = kwargs.pop("name", self._name)
        self._serializer = kwargs.pop("serializer", self.__class__.SERIALIZER)
        self._global_channel = kwargs.pop("global_channel", self.__class__.GLOBAL_CHANNEL)
        self._events = dict()
        self._open()

    def _unload(self, *args, **kwargs):
        Bus._unload(self, *args, **kwargs)
        self._events = None
        self._close()

    def _get_state(self):
        state = Bus._get_state(self)
        state.update(_events = self._events)
        return state

    def _set_state(self, state):
        Bus._set_state(self, state)
        _events = state.get("_events", {})
        for name, methods in legacy.iteritems(_events):
            for method in methods:
                self.bind(name, method)

    def _open(self):
        cls = self.__class__
        channel = self._to_channel(self._global_channel)
        self._redis = redisdb.get_connection()
        self._redis.ping()
        self._pubsub = self._redis.pubsub()
        self._pubsub.subscribe(channel)
        self._listener = RedisListener(self)
        self._listener.start()

    def _close(self):
        self._pubsub.unsubscribe()
        self._listener.join()
        self._redis = None
        self._pubsub = None
        self._listener = None

    def _loop(self, safe = True):
        for item in self._pubsub.listen():
            channel = item.get("channel", None)
            channel = legacy.str(channel)
            type = item.get("type", None)
            data = item.get("data", None)
            if not type in ("message",): continue
            if ":" in channel: _prefix, name = channel.split(":", 1)
            else: name = channel
            data = self._serializer.loads(data)
            methods = self._events.get(name, [])
            for method in methods:
                if safe:
                    self.owner.schedule(
                        method,
                        args = data["args"],
                        kwargs = data["kwargs"],
                        timeout = -1,
                        safe = True
                    )
                else:
                    method(
                        *data["args"],
                        **data["kwargs"]
                    )

    def _to_channel(self, name):
        return self._name + ":" + name

class RedisListener(threading.Thread):

    def __init__(self, bus):
        threading.Thread.__init__(self, name = "RedisListener")
        self.daemon = True
        self._bus = bus

    def run(self):
        self._bus._loop()
