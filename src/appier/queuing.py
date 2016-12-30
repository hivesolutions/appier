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

import uuid
import heapq

from . import rabbitmq
from . import exceptions

class Queue(object):

    def length(self):
        raise exceptions.NotImplementedError()

    def push(self, value, priority = None):
        raise exceptions.NotImplementedError()

    def pop(self, block = True, full = False):
        raise exceptions.NotImplementedError()

    def register(self, callback):
        raise exceptions.NotImplementedError()

    def build_value(
        self,
        value,
        priority = None,
        identify = False,
        reverse = False
    ):
        if identify: identifier = self.build_identifier()
        else: identifier = None
        if priority and reverse: priority *= -1
        return (priority, identifier, value), identifier

    def build_identifier(self):
        return str(uuid.uuid4())

class MemoryQueue(Queue):

    def __init__(self):
        Queue.__init__(self)
        self._queue = []

    def length(self):
        return len(self._queue)

    def push(self, value, priority = None, identify = False):
        value, identifier = self.build_value(
            value,
            priority = priority,
            identify = identify,
            reverse = True
        )
        heapq.heappush(self._queue, value)
        return identifier

    def pop(self, block = True, full = False):
        priority, identifier, value = heapq.heappop(self._queue)
        return (priority, identifier, value) if full else value

class MultiprocessQueue(Queue):

    def __init__(self):
        try: import queue
        except ImportError: import Queue as queue
        Queue.__init__(self)
        self._queue = queue.PriorityQueue()

    def length(self):
        return self._queue.qsize()

    def push(self, value, priority = None, identify = False):
        value, identifier = self.build_value(
            value,
            priority = priority,
            identify = identify,
            reverse = True
        )
        self._queue.put(value)
        return identifier

    def pop(self, block = True, full = False):
        priority, identifier, value = self._queue.get(block)
        return (priority, identifier, value) if full else value

class AMQPQueue(Queue):

    def __init__(self, url = None):
        self.rabbitmq = rabbitmq.RabbitMQ(url = url)

    def push(self, value, priority = None, identify = False):
        pass
