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

import sys
import threading

from . import util
from . import config
from . import legacy
from . import exceptions

ASYNC_HEADER = -1

class AsyncManager(object):

    def __init__(self, owner):
        object.__init__(self)
        self.owner = owner

    def start(self):
        pass

    def stop(self):
        pass

    def restart(self):
        if self.running: self.stop()
        self.start()

    def add(self, method, args = [], kwargs = {}, request = None, mid = None):
        pass

    @property
    def running(self):
        return False

class SimpleManager(AsyncManager):
    """
    Simple (and resource intensive) async manager that
    creates a new thread for every async execution context.

    Should only be used for testing and debugging purposes
    and be avoided in production environments.
    """

    def add(self, method, args = [], kwargs = {}, request = None, mid = None):
        if request: kwargs["request"] = request
        if mid: kwargs["mid"] = mid
        thread = threading.Thread(
            target = method,
            args = args,
            kwargs = kwargs
        )
        thread.start()

    @property
    def running(self):
        return True

class QueueManager(AsyncManager):
    """
    Queue based async manager that uses a single consumer
    thread to consume work (method calls) introduced into
    a simple FIFO queue.
    """

    def __init__(self, owner):
        AsyncManager.__init__(self, owner)
        self.queue = []
        self.condition = None
        self._running = False

    def start(self):
        util.verify(not self._running)
        self._running = True
        self.thread = threading.Thread(target = self.handler)
        self.thread.daemon = True
        self.condition = threading.Condition()
        self.thread.start()

    def stop(self):
        util.verify(self._running)
        self._running = False
        self.condition.acquire()
        try: self.condition.notify()
        finally: self.condition.release()
        self.thread.join()

    def add(self, method, args = [], kwargs = {}, request = None, mid = None):
        util.verify(self.running)
        if request: kwargs["request"] = request
        if mid: kwargs["mid"] = mid
        item = (method, args, kwargs)
        self.condition.acquire()
        try:
            self.queue.append(item)
            self.condition.notify()
        finally:
            self.condition.release()

    def handler(self):
        # iterates continuously while the running flag is set,
        # this flag should be changed by a different thread
        # that aims at stopping this one (and maybe join it)
        while self.running:
            # acquires the condition and waits until the condition
            # is set and the queue has some "real" items
            self.condition.acquire()
            while not self.queue and self.running:
                self.condition.wait()

            # in case the thread is meant to be stopped, stops the
            # current loop immediately
            if not self.running: break

            try:
                # retrieves the latest item in the queue that is going
                # to be processed as soon as possible
                item = self.queue.pop(0)
            finally:
                # releases the condition lock as an item from the queue
                # has been correctly scheduled for processing
                self.condition.release()

            # unpacks the current item (work unit) into the method and
            # the arguments and runs the call handling a possible exception
            # gracefully (prints exception to the logger)
            method, args, kwargs = item
            try: method(*args, **kwargs)
            except BaseException as exception:
                self.owner.log_error(
                    exception,
                    message = "Problem handling async item: %s"
                )

    @property
    def running(self):
        return self._running

class AwaitWrapper(object):
    pass

class CoroutineWrapper(object):
    pass

class AyncgenWrapper(object):
    pass

def await_wrap(generator):
    return generator

def await_yield(value):
    yield value

def ensure_generator(value):
    if legacy.is_generator(value): return True, value
    return False, value

def is_coroutine(callable):
    if hasattr(callable, "_is_coroutine"): return True
    return False

def is_coroutine_object(generator):
    if legacy.is_generator(generator): return True
    return False

def is_coroutine_native(generator):
    return False

def to_coroutine(callable, *args, **kwargs):
    """
    Converts the provided (callback based) callable into a coroutine
    like object/function that is able to yield a future to be notified
    by a wrapper around the "original" callback.

    The parameters to be used in the calling should be passed as list
    and keyword based arguments.

    :type callable: Callable
    :param callable: The callable that is going to be converted into
    a coroutine.
    :rtype: Future
    :return: The future object that is going to be used in the control
    of the coroutine execution.
    """

    # tries to retrieve both the future and a callback from
    # the provided key based arguments in case thre's no future
    # a new one is created for the current context as for the
    # callback an unset one is used for invalid situations
    future = kwargs.pop("future", None) or build_future()
    callback = kwargs.get("callback", None)

    def callback_wrap(result, *args, **kwargs):
        # sets the final result in the associated future
        # this should contain the contents coming from
        # the callback operation (payload)
        future.set_result(result)

        # in case the "original" callback is set calls it
        # with the provided arguments as expected
        callback and callback(result, *args, **kwargs)

        # runs the wake up operation so that the main loop
        # associated with the current execution environment
        # is able to process the new future result
        wakeup()

    # sets the wrapped callback in the key based arguments and
    # then runs the callback with the new arguments, yielding
    # the future that has just been created, effectively creating
    # a coroutine interface from a callback one
    kwargs["callback"] = callback_wrap
    callable(*args, **kwargs)
    yield future

def wrap_silent(function):
    return function

def unavailable(*args, **kwargs):
    raise exceptions.AppierException(
        message = "No support for async available"
    )

def is_neo():
    return sys.version_info[0] >= 3 and sys.version_info[1] >= 3

def header_a_():
    yield ASYNC_HEADER

def ensure_a_(*args, **kwargs):
    yield ensure_async(*args, **kwargs)

# determines the target service configuration that is
# going to be used, this is going to be used to create
# the proper adaptation for the async models
server = config.conf("SERVER", None)
if server == "netius":
    import netius
    Future = netius.Future
    coroutine = netius.coroutine
    wakeup = netius.wakeup
    sleep = netius.sleep
    wait = netius.wait
    notify = netius.notify
    build_future = netius.build_future
    ensure_async = netius.ensure
else:
    Future = unavailable
    coroutine = wrap_silent
    wakeup = unavailable
    sleep = unavailable
    wait = unavailable
    notify = unavailable
    build_future = unavailable
    ensure_async = unavailable
