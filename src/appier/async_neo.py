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

import inspect

from . import legacy

class AwaitWrapper(object):

    def __init__(self, generator, simple = False):
        if simple: generator = self.generate(generator)
        self.generator = generator

    def __await__(self):
        value = yield from self.generator
        return value

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.generator)

    def next(self):
        return self.__next__()

    def generate(self, value):
        yield value

class AyncWrapper(object):

    def __init__(self, async_iter):
        self.async_iter = async_iter
        self.current = None

    def __iter__(self):
        return self

    def __next__(self):
        try:
            if self.current == None: self.current = self.async_iter.asend(None)
            try: return next(self.current)
            except StopIteration as exception:
                self.current = None
                return exception.args[0]
        except StopAsyncIteration: #@UndefinedVariable
            raise StopIteration

    def next(self):
        return self.__next__()

class CoroutineWrapper(object):

    def __init__(self, coroutine):
        self.coroutine = coroutine

    def __iter__(self):
        return self

    def __next__(self):
        return self.coroutine.send(None)

    def next(self):
        return self.__next__()

def await_wrap(generator):
    return AwaitWrapper(generator)

def await_yield(value):
    return AwaitWrapper(value, simple = True)

def ensure_generator(value):
    if legacy.is_generator(value):
        return True, value

    if hasattr(inspect, "isasyncgen") and\
        inspect.isasyncgen(value): #@UndefinedVariable
        return True, AyncWrapper(value)

    if hasattr(inspect, "iscoroutine") and\
        inspect.iscoroutine(value): #@UndefinedVariable
        return True, CoroutineWrapper(value)

    return False, value
