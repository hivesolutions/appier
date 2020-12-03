#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2020 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2020 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import json
import uuid
import heapq
import functools

from . import amqp
from . import legacy
from . import exceptions

class Queue(object):

    def length(self):
        raise exceptions.NotImplementedError()

    def clear(self):
        raise exceptions.NotImplementedError()

    def push(self, value, priority = None, identify = False):
        raise exceptions.NotImplementedError()

    def pop(self, block = True, full = False):
        raise exceptions.NotImplementedError()

    def subscribe(self, callback, full = False):
        raise exceptions.NotImplementedError()

    def loop(self):
        raise exceptions.NotImplementedError()

    def unloop(self):
        raise exceptions.NotImplementedError()

    def ack(self):
        raise exceptions.NotImplementedError()

    def nack(self):
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

    def clear(self):
        del self._queue[:]

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

    def clear(self):
        try: import queue
        except ImportError: import Queue as queue
        self._queue = queue.PriorityQueue()

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

    def __init__(
        self,
        url = None,
        name = "default",
        durable = False,
        max_priority = 255,
        encoder = "pickle",
        protocol = 2,
        encoding = "utf-8",
        amqp = None,
        exchange = None,
        routing_key = None
    ):
        self.url = url
        self.name = name
        self.durable = durable
        self.max_priority = max_priority
        self.encoder = encoder
        self.protocol = protocol
        self.encoding = encoding
        self.amqp = amqp
        self.exchange = exchange
        self._build()

    def clear(self):
        self.channel.queue_purge(queue = self.name)

    def push(self, value, priority = None, identify = False):
        value, identifier = self.build_value(
            value,
            priority = priority,
            identify = identify,
            reverse = False
        )
        body = self._dump(value)

        self._add_callback(
            self.channel.basic_publish,
            exchange = "",
            routing_key = self.name,
            body = body,
            properties = amqp.properties(
                delivery_mode = 2,
                priority = value[0] or 0
            )
        )

        return identifier

    def pop(self, block = True, full = False):
        _method, _properties, body = self.channel.basic_get(
            queue = self.name, auto_ack = False
        )
        priority, identifier, value = self._load(body)
        return (priority, identifier, value) if full else value

    def subscribe(
        self,
        callback,
        full = False,
        auto_ack = True,
        exclusive = False,
        consumer_tag = None,
        arguments = None
    ):
        def handler(channel, method, properties, body):
            priority, identifier, value = self._load(body)
            result = (priority, identifier, value) if full else value
            ack = lambda: self.ack(delivery_tag = method.delivery_tag)
            nack = lambda: self.nack(delivery_tag = method.delivery_tag)
            callback(result) if auto_ack else callback(result, ack, nack)

        self.channel.basic_consume(
            queue = self.name,
            on_message_callback = handler,
            auto_ack = auto_ack,
            exclusive = exclusive,
            consumer_tag = consumer_tag,
            arguments = arguments
        )

    def ack(self, delivery_tag = None):
        self.channel.basic_ack(delivery_tag = delivery_tag)

    def nack(self, delivery_tag = None):
        self.channel.basic_nack(delivery_tag = delivery_tag)

    def loop(self):
        self.channel.start_consuming()

    def unloop(self):
        self.channel.stop_consuming()

    def _dump(self, value):
        return self._dumper(value)

    def _dump_pickle(self, value):
        return legacy.cPickle.dumps(value, protocol = self.protocol)

    def _dump_json(self, value):
        body = json.dumps(value)
        return legacy.bytes(body, encoding = self.encoding)

    def _load(self, body):
        return self._loader(body)

    def _load_pickle(self, body):
        if legacy.PYTHON_3: kwargs = dict(encoding = "bytes")
        else: kwargs = dict()
        return legacy.cPickle.loads(body, **kwargs)

    def _load_json(self, body):
        if legacy.is_bytes(body): body = body.decode(self.encoding)
        return json.loads(body)

    def _build(self):
        if not self.amqp: self.amqp = amqp.AMQP(url = self.url)
        self.connection = self.amqp.get_connection()
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count = 1)
        self.queue = self.channel.queue_declare(
            queue = self.name,
            durable = self.durable,
            arguments = {
                "x-max-priority" : self.max_priority
            }
        )
        if not self.exchange:
            self.channel.queue_bind(
                exchange = self.exchange,
                queue = self.name,
                routing_key = self.routing_key if self.routing_key else ""
            )
        self._dumper = getattr(self, "_dump_" + self.encoder)
        self._loader = getattr(self, "_load_" + self.encoder)

    def _add_callback(self, callback, *args, **kwargs):
        if hasattr(self.connection, "add_callback_threadsafe"):
            self.connection.add_callback_threadsafe(
                functools.partial(callback, *args, **kwargs)
            )
        else:
            callback(*args, **kwargs)

class AMQPExchange(appier.Queue):

    def __init__(self,
        url = None,
        name = "default",
        type = "x-random",
        durable = False,
        encoder = "pickle",
        encoding = "utf-8",
        protocol = 2,
        amqp = None
    ):
        self.url = url
        self.exchange_name = name
        self.exchange_type = type
        self.durable = durable
        self.encoder = encoder
        self.encoding = encoding
        self.protocol = protocol
        self.amqp = amqp

        self._dumper = getattr(self, "_dump_" + self.encoder)

        # sets up the amqp connection if it does not exist
        # sets up the channel and declares this exchange
        self._setup_amqp(url = self.url, amqp = self.amqp)

    def push(self, value, routing_key = "", priority = None, identify = False):
        value, identifier = self.build_value(
            value,
            priority = priority,
            identify = identify,
            reverse = False
        )
        body = self._dump(value)

        # adds a threadsafe callback if possible
        self._add_callback(
            self.channel.basic_publish,
            exchange = self.exchange_name,
            routing_key = routing_key,
            body = body,
            properties = appier.amqp.properties(
                delivery_mode = 2,
                priority = value[0] or 0
            )
        )

        return identifier

    def _setup_amqp(self, url = None, amqp = None):
        self.amqp = amqp if amqp else appier.AMQP(url = url)
        self.connection = self.amqp.get_connection()
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count = 1)
        self.channel.exchange_declare(
            exchange = self.exchange_name,
            exchange_type = self.exchange_type,
            durable = self.durable
        )

    def _dump(self, value):
        return self._dumper(value)

    def _dump_pickle(self, value):
        return appier.legacy.cPickle.dumps(value, protocol = self.protocol)

    def _dump_json(self, value):
        body = json.dumps(value)
        return appier.legacy.bytes(body, encoding = self.encoding)

    def _add_callback(self, callback, *args, **kwargs):
        # adds a threadsafe callback if possible and
        # requests that it is processed as soon as possible
        # if not possible, call the callback immediately
        if hasattr(self.connection, "add_callback_threadsafe") and hasattr(self.connection, "process_data_events"):
            self.connection.add_callback_threadsafe(
                functools.partial(callback, *args, **kwargs)
            )
            self.connection.process_data_events()
        else:
            callback(*args, **kwargs)
