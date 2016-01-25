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

import json

from . import config

try: import redis
except: redis = None

connection = None
""" The global connection object that should persist
the connection relation with the database service """

class Redis(object):

    def __init__(self):
        self._connection = None

    def get_connection(self):
        if self._connection: return self._connection
        url = config.conf("REDISTOGO_URL", "redis://localhost:6379")
        url = config.conf("REDIS_URL", url)
        self._connection = redis.from_url(url)
        return self._connection

def get_connection():
    global connection
    if connection: return connection
    url = config.conf("REDISTOGO_URL", "redis://localhost:6379")
    url = config.conf("REDIS_URL", url)
    connection = redis.from_url(url)
    return connection

def dumps(*args):
    return json.dumps(*args)
