#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2019 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2019 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

from . import util
from . import config
from . import legacy
from . import exceptions

try: import pika
except ImportError: pika = None

URL = "amqp://guest:guest@localhost"
""" The default URL to be used for the connection when
no other URL is provided (used most of the times) """

TIMEOUT = 100
""" The time the retrieval of a connection waits before
returning this avoid possible problems with the current
implementation of the blocking client """

connection = None
""" The global wide connection to the AMQP server
that is meant to be used across sessions """

class AMQP(object):

    def __init__(self, url = None):
        self.url = url
        self._connection = None

    def get_connection(self, url = None, timeout = TIMEOUT):
        if self._connection: return self._connection
        url_c = config.conf("AMQP_URL", None)
        url_c = config.conf("CLOUDAMQP_URL", url_c)
        url_c = config.conf("RABBITMQ_URL", url_c)
        url = url or self.url or url_c or URL
        url_p = legacy.urlparse(url)
        parameters = _pika().ConnectionParameters(
            host = url_p.hostname,
            virtual_host = url_p.path or "/",
            credentials = _pika().PlainCredentials(url_p.username, url_p.password)
        )
        parameters.socket_timeout = timeout
        self._connection = _pika().BlockingConnection(parameters)
        self._connection = _set_fixes(self._connection)
        return self._connection

def get_connection(url = URL, timeout = TIMEOUT):
    global connection
    url = config.conf("AMQP_URL", url)
    url = config.conf("CLOUDAMQP_URL", url)
    url = config.conf("RABBITMQ_URL", url)
    url_p = legacy.urlparse(url)
    parameters = _pika().ConnectionParameters(
        host = url_p.hostname,
        virtual_host = url_p.path or "/",
        credentials = _pika().PlainCredentials(url_p.username, url_p.password)
    )
    parameters.socket_timeout = timeout
    connection = _pika().BlockingConnection(parameters)
    connection = _set_fixes(connection)
    return connection

def properties(*args, **kwargs):
    return _pika().BasicProperties(*args, **kwargs)

def _set_fixes(connection):
    def disconnect():
        connection.socket.close()

    if not hasattr(connection, "disconnect"):
        connection.disconnect = disconnect
    return connection

def _pika(verify = True):
    if verify: util.verify(
        not pika == None,
        message = "Pika library not available",
        exception = exceptions.OperationalError
    )
    return pika
