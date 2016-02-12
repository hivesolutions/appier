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

from . import util

class Observable(object):
    """
    The base class that implements the observable
    patter allowing the object to handle a series of
    event in a dynamic fashion.

    The class should be able to handle both context
    based event (instance level) and global level
    events (class level).

    This class should be friendly to multiple inheritance
    and should avoid variable naming collision.
    """

    _events_g = {}
    """ The dictionary containing the global association
    between the global event names and the handler methods """

    def __init__(self, *args, **kwargs):
        self._events = {}

    @classmethod
    def name_f(cls, name):
        cls_name = cls.__name__
        cls_name = util.camel_to_underscore(cls_name)
        name_f = cls_name + "." + name
        return name_f

    @classmethod
    def bind_g(cls, name, method, oneshot = False):
        if oneshot: method.oneshot = oneshot
        name_f = cls.name_f(name)
        methods = cls._events_g.get(name_f, [])
        methods.append(method)
        cls._events_g[name_f] = methods

    @classmethod
    def unbind_g(cls, name, method = None):
        name_f = cls.name_f(name)
        methods = cls._events_g.get(name_f, [])
        if method: methods.remove(method)
        else: del methods[:]

    @classmethod
    def trigger_g(cls, name, *args, **kwargs):
        oneshots = None
        name_f = cls.name_f(name)
        methods = cls._events_g.get(name_f, [])
        for method in methods:
            method(*args, **kwargs)
            if not hasattr(method, "oneshot"): continue
            if not method.oneshot: continue
            oneshots = [] if oneshots == None else oneshots
            oneshots.append(method)
        if not oneshots: return
        for oneshot in oneshots: cls.unbind_g(name, oneshot)

    def build(self):
        pass

    def destroy(self):
        self.unbind_all()

    def bind(self, name, method, oneshot = False):
        if oneshot: method.oneshot = oneshot
        methods = self._events.get(name, [])
        methods.append(method)
        self._events[name] = methods

    def unbind(self, name, method = None):
        methods = self._events.get(name, [])
        if method: methods.remove(method)
        else: del methods[:]

    def unbind_all(self):
        if not hasattr(self, "_events"): return
        for methods in self._events.values(): del methods[:]
        self._events.clear()

    def trigger(self, name, *args, **kwargs):
        cls = self.__class__
        self.trigger_l(name, cls, *args, **kwargs)

    def trigger_l(self, name, level, *args, **kwargs):
        oneshots = None
        methods = self._events.get(name, [])
        for method in methods:
            method(*args, **kwargs)
            if not hasattr(method, "oneshot"): continue
            if not method.oneshot: continue
            oneshots = [] if oneshots == None else oneshots
            oneshots.append(method)
        level.trigger_g(name, self, *args, **kwargs)
        if not oneshots: return
        for oneshot in oneshots: self.unbind(name, oneshot)
