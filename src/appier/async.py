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

import threading

from . import config
from . import exceptions

class AsyncManager(object):

    def __init__(self, owner):
        object.__init__(self)
        self.owner = owner

    def start(self):
        pass

    def stop(self):
        pass

    def add(self, method, args, kwargs, request = None, mid = None):
        pass

class SimpleManager(AsyncManager):

    def add(self, method, args, kwargs, request = None, mid = None):
        if request: kwargs["request"] = request
        if mid: kwargs["mid"] = mid
        thread = threading.Thread(
            target = method,
            args = args,
            kwargs = kwargs
        )
        thread.start()

class QueueManager(AsyncManager):

    def __init__(self, owner):
        AsyncManager.__init__(self, owner)
        self.queue = []
        self.condition = threading.Condition()

    def start(self):
        self.thread = threading.Thread(target = self.handler)
        self.running = True
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.running = False

    def add(self, method, args, kwargs, request = None, mid = None):
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
        while self.running:
            self.condition.acquire()
            while not self.queue: self.condition.wait()
            try: item = self.queue.pop(0)
            finally: self.condition.release()
            method, args, kwargs = item
            try: method(*args, **kwargs)
            except BaseException as exception:
                self.owner.log_error(
                    exception,
                    message = "Problem handling async item: %s"
                )

def unavailable(*args, **kwargs):
    raise exceptions.AppierException(
        message = "No support for async available"
    )

server = config.conf("SERVER", None)
if server == "netius":
    import netius
    Future = netius.Future
    ensure_async = netius.ensure
    coroutine = netius.coroutine
    sleep = netius.sleep
    wait = netius.wait
    notify = netius.notify
else:
    Future = unavailable
    ensure_async = unavailable
    coroutine = unavailable
    sleep = unavailable
    wait = unavailable
    notify = unavailable
