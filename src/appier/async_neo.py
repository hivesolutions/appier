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

import inspect

from . import legacy
from . import async_old

class AwaitWrapper(object):

    _is_generator = True

    def __init__(self, generator, generate = False):
        if generate: generator = self.generate(generator)
        self.generator = generator
        self.is_generator = legacy.is_generator(generator)

    def __await__(self):
        if self.is_generator: return self._await_generator()
        else: return self._await_basic()

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.generator)

    def next(self):
        return self.__next__()

    def generate(self, value):
        yield value

    def _await_generator(self):
        value = yield from self.generator
        return value

    def _await_basic(self):
        return self.generator
        yield

class CoroutineWrapper(object):

    def __init__(self, coroutine):
        self.coroutine = coroutine
        self._buffer = None

    def __iter__(self):
        return self

    def __next__(self):
        if self._buffer: return self._buffer.pop(0)
        return self.coroutine.send(None)

    def next(self):
        return self.__next__()

    def restore(self, value):
        if self._buffer == None: self._buffer = []
        self._buffer.append(value)

class AyncgenWrapper(object):

    def __init__(self, async_iter):
        self.async_iter = async_iter
        self.current = None
        self._buffer = None

    def __iter__(self):
        return self

    def __next__(self):
        if self._buffer: return self._buffer.pop(0)
        try:
            if self.current == None:
                self.current = self.async_iter.asend(None)
            try:
                return next(self.current)
            except StopIteration as exception:
                self.current = None
                if not exception.args: return None
                return exception.args[0]
        except StopAsyncIteration: #@UndefinedVariable
            raise StopIteration()

    def next(self):
        return self.__next__()

    def restore(self, value):
        if self._buffer == None: self._buffer = []
        self._buffer.append(value)

def await_wrap(generator):
    return AwaitWrapper(generator)

def await_yield(value):
    return AwaitWrapper(value, generate = True)

def ensure_generator(value):
    if legacy.is_generator(value):
        return True, value

    if hasattr(value, "_generator"):
        return True, value

    if hasattr(inspect, "iscoroutine") and\
        inspect.iscoroutine(value): #@UndefinedVariable
        return True, CoroutineWrapper(value)

    if hasattr(inspect, "isasyncgen") and\
        inspect.isasyncgen(value): #@UndefinedVariable
        return True, AyncgenWrapper(value)

    return False, value

def is_coroutine(callable):
    if hasattr(callable, "_is_coroutine"):
        return True

    if hasattr(inspect, "iscoroutinefunction") and\
        inspect.iscoroutinefunction(callable): #@UndefinedVariable
        return True

    return False

def is_coroutine_object(generator):
    if legacy.is_generator(generator):
        return True

    if hasattr(inspect, "iscoroutine") and\
        inspect.iscoroutine(generator): #@UndefinedVariable
        return True

    return False

def is_coroutine_native(generator):
    if hasattr(inspect, "iscoroutine") and\
        inspect.iscoroutine(generator): #@UndefinedVariable
        return True

    return False

def to_coroutine(callable, *args, **kwargs):
    # sets the original reference to the future variable, this
    # should never be the final result, otherwise error occurs
    future = None

    # yields the complete set of values from the generator created
    # by the call to the to coroutine converter of the callable
    for value in async_old.to_coroutine(callable, *args, **kwargs):
        yield value
        future = value

    # returns the final result, retrieving it from the future object
    # that has been returned from the coroutine generator function
    return future.result()
