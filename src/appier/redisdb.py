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

import json

from . import util
from . import config
from . import exceptions

try: import redis
except: redis = None

URL = "redis://localhost"
""" The default URL to be used for the connection when
no other URL is provided (used most of the times) """

connection = None
""" The global connection object that should persist
the connection relation with the database service """

class Redis(object):

    def __init__(self, url = None):
        self.url = url
        self._connection = None

    def get_connection(self, url = None):
        if self._connection: return self._connection
        url_c = config.conf("REDISTOGO_URL", None)
        url_c = config.conf("REDIS_URL", url_c)
        url = url or self.url or url_c or URL
        self._connection = _redis().from_url(url)
        return self._connection

def get_connection(url = URL):
    global connection
    if connection: return connection
    url = config.conf("REDISTOGO_URL", url)
    url = config.conf("REDIS_URL", url)
    connection = _redis().from_url(url)
    return connection

def dumps(*args):
    return json.dumps(*args)

def _redis(verify = True):
    if verify: util.verify(
        not redis == None,
        message = "redis library not available",
        exception = exceptions.OperationalError
    )
    return redis
