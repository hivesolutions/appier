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

import json

from . import util
from . import config
from . import exceptions

try: import redis
except ImportError: redis = None

URL = "redis://localhost"
""" The default URL to be used for the connection when
no other URL is provided (used most of the times) """

POOL = True
""" The default boolean value for the enabling/disabling
of the connection pool of redis """

connection = None
""" The global connection object that should persist
the connection relation with the database service """

class Redis(object):

    def __init__(self, url = None, pool = None):
        self.url = url
        self.pool = pool
        self._connection = None

    def get_connection(self, url = None, pool = None):
        if self._connection: return self._connection

        url_c = config.conf("REDISTOGO_URL", None)
        url_c = config.conf("REDIS_URL", url_c)
        pool_c = config.conf("REDIS_POOL", True, cast = bool)

        _url = URL
        if not url_c == None: _url = url_c
        if not self.url == None: _url = self.url
        if not url == None: _url = url

        _pool = POOL
        if not pool_c == None: _pool = pool_c
        if not self.pool == None: _pool = self.pool
        if not pool == None: _pool = pool

        if _pool:
            connection_pool = _redis().BlockingConnectionPool.from_url(_url)
            self._connection = _redis().Redis(connection_pool = connection_pool)
        else:
            self._connection = _redis().from_url(_url)

        return self._connection

def get_connection(url = URL):
    global connection
    if connection: return connection
    url = config.conf("REDISTOGO_URL", url)
    url = config.conf("REDIS_URL", url)
    pool = config.conf("REDIS_POOL", True, cast = bool)
    if pool:
        connection_pool = _redis().BlockingConnectionPool.from_url(url)
        connection = _redis().Redis(connection_pool = connection_pool)
    else:
        connection = _redis().from_url(url)
    return connection

def dumps(*args):
    return json.dumps(*args)

def _redis(verify = True):
    if verify: util.verify(
        not redis == None,
        message = "RedisPy library not available",
        exception = exceptions.OperationalError
    )
    return redis
