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
from . import legacy
from . import typesf
from . import config
from . import common
from . import exceptions

try: import pymongo
except: pymongo = None

try: import bson.json_util
except: bson = None

URL = "mongodb://localhost"
""" The default URL to be used for the connection when
no other URL is provided (used most of the times) """

connection = None
""" The global connection object that should persist
the connection relation with the database service """

class Mongo(object):

    def __init__(self, url = None):
        self.url = url
        self._connection = None
        self._db = None

    def get_connection(self, url = None, connect = False):
        if self._connection: return self._connection
        url_c = config.conf("MONGOHQ_URL", None)
        url_c = config.conf("MONGOLAB_URI", url_c)
        url_c = config.conf("MONGO_URL", url_c)
        url = url or self.url or url_c or URL
        if is_new(): self._connection = _pymongo().MongoClient(url, connect = connect)
        else: self._connection = _pymongo().Connection(url)
        return self._connection

    def reset_connection(self):
        if not self._connection: return
        if is_new(): self._connection.close()
        else: self._connection.disconnect()
        self._connection = None

    def get_db(self, name):
        if self._db: return self._db
        connection = self.get_connection()
        self._db = connection[name]
        return self._db

class MongoEncoder(json.JSONEncoder):

    def default(self, obj, **kwargs):
        if not bson: return json.JSONEncoder.default(self, obj, **kwargs)
        if isinstance(obj, bson.objectid.ObjectId): return str(obj)
        if isinstance(obj, legacy.BYTES): return legacy.str(obj, encoding = "utf-8")
        else: return json.JSONEncoder.default(self, obj, **kwargs)

def get_connection(url = URL, connect = False):
    global connection
    if connection: return connection
    url = config.conf("MONGOHQ_URL", url)
    url = config.conf("MONGOLAB_URI", url)
    url = config.conf("MONGO_URL", url)
    if is_new(): connection = _pymongo().MongoClient(url, connect = connect)
    else: connection = _pymongo().Connection(url)
    return connection

def reset_connection():
    global connection
    if not connection: return
    if is_new(): connection.close()
    else: connection.disconnect()
    connection = None

def get_db(name = None):
    url = config.conf("MONGOHQ_URL", None)
    url = config.conf("MONGOLAB_URI", url)
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
    names = _list_names(db)
    for name in names:
        if name.startswith("system."): continue
        db.drop_collection(name)
    connection = get_connection()
    connection.drop_database(db.name)

def object_id(value):
    return bson.ObjectId(value)

def dumps(*args):
    return json.dumps(default = serialize, *args)

def serialize(obj):
    if isinstance(obj, common.model().Model): return obj.model
    if isinstance(obj, typesf.AbstractType): return obj.json_v()
    return bson.json_util.default(obj)

def directions(all = False):
    return (
        _pymongo().ASCENDING,
        _pymongo().DESCENDING,
        _pymongo().HASHED
    ) if all else (
        _pymongo().ASCENDING,
        _pymongo().DESCENDING
    )

def is_mongo(obj):
    if bson and isinstance(obj, bson.ObjectId): return True
    if bson and isinstance(obj, bson.DBRef): return True
    return False

def is_new(major = 3, minor = 0, patch = 0):
    if not pymongo: return False
    _version = _pymongo().version
    _major = int(_version[0])
    _minor = int(_version[2])
    _patch = int(_version[4])
    if _major > major: return True
    elif _major < major: return False
    if _minor > minor: return True
    elif _minor < minor: return False
    if _patch >= patch: return True
    else: return False

def _list_names(db, *args, **kwargs):
    if is_new(3, 7): return db.list_collection_names()
    else: return db.collection_names()

def _count(store, *args, **kwargs):
    if len(args) == 0: args = [{}]
    if is_new(3, 7): return store.count_documents(*args, **kwargs)
    return store.count(*args, **kwargs)

def _store_find_and_modify(store, *args, **kwargs):
    if is_new(): return store.find_one_and_update(*args, **kwargs)
    else: return store.find_and_modify(*args, **kwargs)

def _store_insert(store, *args, **kwargs):
    if is_new(): store.insert_one(*args, **kwargs)
    else: store.insert(*args, **kwargs)

def _store_update(store, *args, **kwargs):
    if is_new(): store.update_one(*args, **kwargs)
    else: store.update(*args, **kwargs)

def _store_remove(store, *args, **kwargs):
    if is_new(): store.delete_many(*args, **kwargs)
    else: store.remove(*args, **kwargs)

def _store_ensure_index(store, *args, **kwargs):
    kwargs["background"] = kwargs.get("background", True)
    if is_new(): store.create_index(*args, **kwargs)
    else: store.ensure_index(*args, **kwargs)

def _store_ensure_index_many(store, *args, **kwargs):
    directions_l = kwargs.pop("directions", None)
    if directions_l == "all": directions_l = directions(all = True)
    elif directions_l == None: directions_l = directions()
    for direction in directions_l:
        _args = list(args)
        _args[0] = [(_args[0], direction)]
        _store_ensure_index(store, *_args, **kwargs)

def _pymongo(verify = True):
    if verify: util.verify(
        not pymongo == None,
        message = "pymongo library not available",
        exception = exceptions.OperationalError
    )
    return pymongo
