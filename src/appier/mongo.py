#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2015 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2015 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import json

from . import legacy
from . import typesf
from . import config
from . import common

try: import pymongo
except: pymongo = None

try: import bson.json_util
except: bson = None

connection = None
""" The global connection object that should persist
the connection relation with the database service """

class Mongo(object):

    def __init__(self):
        self._connection = None
        self._db = None

    def get_connection(self):
        if self._connection: return self._connection
        url = config.conf("MONGOHQ_URL", "mongodb://localhost:27017")
        url = config.conf("MONGO_URL", url)
        if is_new(): self._connection = pymongo.MongoClient(url)
        else: self._connection = pymongo.Connection(url)
        return self._connection

    def get_db(self, name):
        if self._db: return self._db
        connection = self.get_connection()
        self._db = connection[name]
        return self._db

def get_connection():
    global connection
    if connection: return connection
    url = config.conf("MONGOHQ_URL", "mongodb://localhost:27017")
    url = config.conf("MONGO_URL", url)
    if is_new(): connection = pymongo.MongoClient(url)
    else: connection = pymongo.Connection(url)
    return connection

def get_db(name = None):
    url = config.conf("MONGOHQ_URL", None)
    url = config.conf("MONGO_URL", url)
    result = legacy.urlparse(url or "")
    name = result.path.strip("/") if result.path else None
    name = name or config.conf("MONGO_DB", name)
    name = name or common.base().get_name() or "master"
    connection = get_connection()
    db = connection[name]
    return db

def drop_db(name = None):
    db = get_db(name = name)
    names = db.collection_names()
    for name in names:
        if name.startswith("system."): continue
        db.drop_collection(name)

def object_id(value):
    return bson.ObjectId(value)

def dumps(*args):
    return json.dumps(default = serialize, *args)

def serialize(obj):
    if isinstance(obj, common.model().Model): return obj.model
    if isinstance(obj, typesf.Type): return obj.json_v()
    return bson.json_util.default(obj)

def is_mongo(obj):
    if bson and isinstance(obj, bson.ObjectId): return True
    if bson and isinstance(obj, bson.DBRef): return True
    return False

def is_new():
    return int(pymongo.version[0]) >= 3 if pymongo else False
