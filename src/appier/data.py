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

import os
import uuid
import hashlib

from . import mongo
from . import config
from . import legacy
from . import exceptions

class DataAdapter(object):

    def collection(self, name, *args, **kwargs):
        raise exceptions.NotImplementedError()

    def get_db(self):
        raise exceptions.NotImplementedError()

    def drop_db(self, *args, **kwargs):
        raise exceptions.NotImplementedError()

    def object_id(self, value):
        return value

class MongoAdapter(DataAdapter):

    def collection(self, name, *args, **kwargs):
        db = self.get_db()
        collection = db[name]
        return MongoCollection(collection)

    def get_db(self):
        return mongo.get_db()

    def drop_db(self, *args, **kwargs):
        return mongo.drop_db()

    def object_id(self, value):
        return mongo.object_id(value)

class TinyAdapter(DataAdapter):

    def __init__(self, *args, **kwargs):
        self.file_path = config.conf("TINY_PATH", "db.json")
        self.file_path = kwargs.get("file_path", self.file_path)
        self._db = None

    def collection(self, name, *args, **kwargs):
        db = self.get_db()
        table = db.table(name)
        return TinyCollection(table)

    def get_db(self):
        import tinydb
        if self._db: return self._db
        self._db = tinydb.TinyDB(self.file_path)
        return self._db

    def drop_db(self, *args, **kwargs):
        db = self.get_db()
        db.purge_tables()
        os.remove

class Collection(object):

    def find(self, *args, **kwargs):
        raise exceptions.NotImplementedError()

    def find_one(self, *args, **kwargs):
        raise exceptions.NotImplementedError()

    def find_and_modify(self, *args, **kwargs):
        raise exceptions.NotImplementedError()

    def insert(self, *args, **kwargs):
        raise exceptions.NotImplementedError()

    def update(self, *args, **kwargs):
        raise exceptions.NotImplementedError()

    def remove(self, *args, **kwargs):
        raise exceptions.NotImplementedError()

    def count(self, *args, **kwargs):
        raise exceptions.NotImplementedError()

    def ensure_index(self, *args, **kwargs):
        raise exceptions.NotImplementedError()

    def _id(self):
        token_s = str(uuid.uuid4())
        token_s = legacy.bytes(token_s)
        token = hashlib.md5(token_s).hexdigest()
        return token

class MongoCollection(Collection):

    def __init__(self, base):
        self._base = base

    def find(self, *args, **kwargs):
        return self._base.find(*args, **kwargs)

    def find_one(self, *args, **kwargs):
        return self._base.find_one(*args, **kwargs)

    def find_and_modify(self, *args, **kwargs):
        return mongo._store_find_and_modify(self._base, *args, **kwargs)

    def insert(self, *args, **kwargs):
        return mongo._store_insert(self._base, *args, **kwargs)

    def update(self, *args, **kwargs):
        return mongo._store_update(self._base, *args, **kwargs)

    def remove(self, *args, **kwargs):
        return mongo._store_remove(self._base, *args, **kwargs)

    def count(self, *args, **kwargs):
        return self._base.count(*args, **kwargs)

    def ensure_index(self, *args, **kwargs):
        return mongo._store_ensure_index(self._base, *args, **kwargs)

class TinyCollection(Collection):

    def __init__(self, base):
        self._base = base

    def find(self, *args, **kwargs):
        filter = args[0] if len(args) > 0 else dict()
        condition = self._to_condition(filter)
        return self._base.search(condition)

    def find_one(self, *args, **kwargs):
        filter = args[0] if len(args) > 0 else dict()
        condition = self._to_condition(filter)
        return self._base.get(condition)

    def find_and_modify(self, *args, **kwargs):
        filter = args[0] if len(args) > 0 else dict()
        modification = args[1] if len(args) > 1 else dict()
        create = kwargs.get("new", False)
        condition = self._to_condition(filter)
        object = self._base.get(condition)
        found = True if object else False
        if not found and not create:
            raise exceptions.OperationalError(
                message = "No object found"
            )
        if not found: object = dict(filter)
        object = self._to_update(modification, object = object)
        if found: self.update(object)
        else: self.insert(object)
        return object

    def insert(self, *args, **kwargs):
        object = args[0] if len(args) > 0 else dict()
        has_id = "_id" in object
        if not has_id: object["_id"] = self._id()
        self._base.insert(object)
        return object

    def update(self, *args, **kwargs):
        filter = args[0] if len(args) > 0 else dict()
        updater = args[1] if len(args) > 1 else dict()
        condition = self._to_condition(filter)
        object = updater.get("$set", dict())
        return self._base.update(object, condition)

    def remove(self, *args, **kwargs):
        filter = args[0] if len(args) > 0 else dict()
        condition = self._to_condition(filter)
        return self._base.remove(condition)

    def count(self, *args, **kwargs):
        filter = args[0] if len(args) > 0 else dict()
        condition = self._to_condition(filter)
        return self._base.count(condition)

    def ensure_index(self, *args, **kwargs):
        pass

    def _to_condition(self, filter):
        import tinydb
        query = tinydb.Query()
        condition = query._id.exists()
        for name, value in legacy.iteritems(filter):
            if name.startswith("$"): continue
            query = tinydb.Query()
            _condition = getattr(query, name).__eq__(value)
            condition &= _condition
        return condition

    def _to_update(self, modification, object = None):
        object = object or dict()
        increments = modification.get("$inc", {})
        for name, increment in legacy.iteritems(increments):
            value = object.get(name, 0)
            value += increment
            object[name] = value
        return object
